import logging
import json
import re
import os
import threading
import networkx as nx  # 需要引入 networkx
from typing import List, Dict, Optional, Any, Tuple
from .interface import ITaskPlanningCapability
from external.repositories.agent_structure_repo import AgentStructureRepository

import logging
logger = logging.getLogger(__name__)

# Token 统计器（仅在评估模式下使用）
_token_tracker = None
def get_token_tracker():
    global _token_tracker
    if _token_tracker is None and os.environ.get("COOP_EVAL_EXECUTION") == "1":
        try:
            from coop_eval_actual.utils import token_tracker
            _token_tracker = token_tracker
        except ImportError:
            pass
    return _token_tracker

# 假设的外部依赖，实际使用时请替换为真实路径
# from repositories.structure import AgentStructureRepository 


##TODO:SCC的节点还有一些问题，包括seq预设顺序
class CommonTaskPlanning(ITaskPlanningCapability):
    """
    任务规划器 V2：
    1. 语义层：基于 LLM 将用户自然语言拆解为初步意图链 (Agent vs MCP)。
    2. 结构层：基于 Neo4j 知识图谱，发现隐性依赖（SCC），对 Agent 任务进行协同规划与扩充。
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.tree_manager = None
        self._llm = None
        self._structure_repo = None # 用于连接 Neo4j

    def get_capability_type(self) -> str:
        return 'common_task_planning'

    def initialize(self, config: Dict[str, Any]) -> bool:

        from agents.tree.tree_manager import treeManager

        self.tree_manager = treeManager
        # 延迟获取 LLM，避免初始化顺序问题
        # self._llm 将在首次使用时获取
        self._llm = None

        self._structure_repo = AgentStructureRepository()
        return True

    @property
    def llm(self):
        """延迟获取 LLM 能力"""
        if self._llm is None:
            from ..llm.interface import ILLMCapability
            from ..registry import capability_registry
            self._llm = capability_registry.get_capability("llm", ILLMCapability)
        return self._llm

    def generate_execution_plan(
        self,
        agent_id: str,
        user_input: str,
        memory_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        [主入口] 生成完整的执行规划链（语义拆解 -> 依赖扩充）
        """
        try:
            # Phase 1: 语义拆解（注入记忆）
            # 记忆在这里影响：Agent vs MCP 的选择，以及第一层参数的提取
            base_plan = self._semantic_decomposition(agent_id, user_input, memory_context)
            if not base_plan:
                return [
                    {
                        "step": 1,
                        "type": "MCP",
                        "executor": "mcp_llm",
                        "content": user_input,
                        "description": "auto_fallback",
                    }
                ]

            # Phase 2: 结构化扩充（透传记忆）
            # 将 memory_context 打包进 context，传递给 Neo4j 协同规划层
            expansion_context = {
                "main_intent": user_input,
                "global_memory": memory_context or ""  # <--- 注入点
            }
            final_plan = base_plan
            # final_plan = self._expand_plan_with_dependencies(base_plan, context=expansion_context)
            
            self.logger.info(f"Final plan generated with {len(final_plan)} steps (expanded from {len(base_plan)}).")
            return final_plan

        except Exception as e:
            self.logger.error(f"Planning error: {e}", exc_info=True)
            return []



    def shutdown(self) -> None:
        """释放资源，重置状态"""
        self.tree_manager = None
        self._llm = None
        self._structure_repo = None
        logger.info("[CommonTaskPlanner] Shutdown completed")
    # =========================================================================
    # Phase 1: 语义拆解 (原有逻辑保持不变，改名为 internal method)
    # =========================================================================

    def _semantic_decomposition(self, agent_id: str, user_input: str, memory_context: str) -> List[Dict]:
        candidates = self._get_candidate_agents_info(agent_id)
        candidate_ids = {item.get("id") for item in candidates if item.get("id")}
        if not candidate_ids:
            # 没有子节点，标记为叶子节点直接执行
            return [
                {
                    "step": 1,
                    "type": "LEAF",  # 标记为叶子节点，直接执行
                    "executor": agent_id,
                    "content": user_input,
                    "description": "leaf_execution",
                }
            ]

        # 构建增强版 Prompt
        prompt = self._build_enhanced_planning_prompt(user_input, memory_context, candidates)

        response = self._call_llm(prompt, agent_id=agent_id)
        plans = self._parse_llm_json(response)
        for plan in plans:
            if str(plan.get("type", "")).upper() == "AGENT":
                executor = plan.get("executor")
                # 防止递归：如果 executor 是当前 agent 自己，或者不在候选列表中
                if executor == agent_id or executor not in candidate_ids:
                    # 标记为叶子节点直接执行，避免无限递归
                    plan["type"] = "LEAF"
                    plan["executor"] = agent_id
                    plan["description"] = plan.get("description") or "leaf_execution"
                    self.logger.warning(f"[CommonTaskPlanner] Prevented recursion: executor '{executor}' -> LEAF execution for '{agent_id}'")
        self.logger.info(f"[CommonTaskPlanner] LLM response:\n{plans}")
        return plans


    def _build_enhanced_planning_prompt(self, user_input, memory, agents):
        agents_str = json.dumps(agents, ensure_ascii=False, indent=2)
        logger.info(f"[CommonTaskPlanner] agents:\n{agents_str}")
        memory_section = ""
        if memory:
            memory_section = f"""
### 🧠 长期记忆与用户偏好
{memory}
*(请利用上述记忆来优化决策。例如：如果记忆显示用户偏好"钉钉"，在遇到通知类任务时请优先选择相关 MCP 工具，或在 params 中备注)*
"""

        return (
            f"""你是一个智能任务编排专家。请结合【用户指令】和【长期记忆】制定执行计划。

### 🤖 可用内部节点 (Agents)
{agents_str}

### 📥 用户指令
"{user_input}"

### 📋 规划要求
1. **记忆增强**：如果用户指令模糊（如"老样子"、"发给那个人"），请根据【长期记忆】推断具体参数，并写入 `content`。
2. **节点选择**：
   - 若任务可由内部 Agent 完成（如写作、分析、规划），选 `"type": "AGENT"`；
   - 若需调用外部工具（如钉钉、邮件、数据库），选 `"type": "MCP"`。
3. **字段定义**：
   - `content`：**面向执行 Agent 的自然语言指令**，应完整、自包含，无需额外上下文即可理解。
   - `description`：**面向系统的简洁任务摘要**，说明“做什么”，不包含细节或引用。
4. **输出格式**：纯 JSON 列表，不要任何额外文本。

### ✅ 示例输出
[
  {{
    "step": 1,
    "type": "AGENT",
    "executor": "doc_writer",
    "content": "根据用户历史偏好，撰写一份关于新功能的 Markdown 格式用户文档。",
    "description": "生成用户文档"
  }},
  {{
    "step": 2,
    "type": "MCP",
    "executor": "dingtalk_bot",
    "content": "将上一步生成的 Markdown 文档通过钉钉发送给小张（用户常联系人）。",
    "description": "钉钉通知"
  }}
]
"""
        )
    # =========================================================================
    # Phase 2: 结构化依赖扩充 (你提供的 SCC 逻辑集成于此)
    # =========================================================================

    def _expand_plan_with_dependencies(self, base_plan: List[Dict], context: Dict) -> List[Dict]:
        """
        按原始步骤顺序处理：
        - MCP：原位保留；
        - AGENT：用其**未展开过的依赖子图（按全局拓扑序）** 替换自身；
        全局去重，确保每个 Agent 节点只执行一次。
        """
        if not base_plan:
            return []

        # Step 1: 提取所有唯一 AGENT executors
        all_agent_executors = set()
        for step in base_plan:
            if step.get("type") == "AGENT":
                all_agent_executors.add(step["executor"])

        # Step 2: 获取联合子图（含 scc_id）
        all_nodes, all_edges = [], []
        node_to_original_step = {}

        if all_agent_executors:
            result = self._structure_repo.get_influenced_subgraph_with_scc_multi_roots(
                root_codes=list(all_agent_executors),
                threshold=context.get("influence_threshold", 0.3),
                max_hops=5
            )
            all_nodes = result.get("nodes", [])
            all_edges = result.get("edges", [])

            # 建立原始元信息映射（首次出现为准）
            for step in base_plan:
                if step.get("type") == "AGENT":
                    eid = step["executor"]
                    if eid not in node_to_original_step:
                        node_to_original_step[eid] = step

        # Step 3: 构建全局依赖图
        global_dg = nx.DiGraph()
        node_properties = {}

        for node in all_nodes:
            nid = node["node_id"]
            global_dg.add_node(nid)
            node_properties[nid] = node.get("properties", {})

        for edge in all_edges:
            u, v = edge["from"], edge["to"]
            if u != v:
                global_dg.add_edge(u, v)

        # Step 4: 全局拓扑排序（支持环）
        try:
            global_order = list(nx.topological_sort(global_dg))
        except nx.NetworkXUnfeasible:
            # 使用 SCC 缩点排序（即使 Neo4j 返回了 scc_id，这里仍用 networkx 确保一致）
            global_order = self._topo_sort_with_scc(global_dg, {})

        # Step 5: 协同规划所有节点参数
        task_details = {}
        if all_nodes:
            task_details = self._plan_all_nodes_with_context(
                node_ids=global_order,
                node_properties=node_properties,
                context=context,
                original_meta=node_to_original_step
            )

        # Step 6: 按原始顺序构建最终计划
        final_plan = []
        expanded_cache = set()  # 已加入 plan 的节点 ID

        for orig_step in base_plan:
            if orig_step.get("type") == "MCP":
                final_plan.append(orig_step)
            elif orig_step.get("type") == "AGENT":
                executor = orig_step["executor"]

                # 如果该 executor 本身不在图中（孤立节点），则直接保留
                if executor not in global_dg:
                    final_plan.append(orig_step)
                    expanded_cache.add(executor)
                    continue

                # 找出所有“从 executor 出发可达”的节点（包括自己）
                reachable = {executor}
                try:
                    for descendant in nx.descendants(global_dg, executor):
                        reachable.add(descendant)
                except nx.NodeNotFound:
                    pass  # shouldn't happen

                # 从全局拓扑序中筛选：属于 reachable 且未展开
                to_insert = [
                    nid for nid in global_order
                    if nid in reachable and nid not in expanded_cache
                ]

                if to_insert:
                    expanded_cache.update(to_insert)
                    for nid in to_insert:
                        detail = task_details.get(nid, {})
                        final_plan.append({
                            "type": "AGENT",
                            "executor": nid,
                            "description": detail.get("intent", f"Execute {nid}"),
                            "params": detail.get("parameters", {}),
                            "is_dependency_expanded": True,
                            "original_parent": executor
                        })
                else:
                    # 所有依赖都已执行过，跳过（或保留原步骤？）
                    # 通常不会发生，但为安全起见，保留原步骤
                    final_plan.append(orig_step)

        return self._reindex_steps(final_plan)


    def _fetch_combined_subgraph(self, root_agent_ids: set, context: Dict) -> Tuple[List, List]:
        """
        一次性从 Neo4j 获取多个根节点的联合影响子图。
        假设 AgentStructureRepository 支持多根查询。
        """
        if not self._structure_repo:
            return [], []

        try:
            # 修改 repo 接口：支持 roots=list
            result = self._structure_repo.get_influenced_subgraph_with_scc_multi_roots(
                root_codes=list(root_agent_ids),
                threshold=context.get("influence_threshold", 0.3),
                max_hops=5
            )
            return result.get("nodes", []), result.get("edges", [])
        except Exception as e:
            self.logger.warning(f"Failed to fetch combined subgraph: {e}")
            return [], []


    def _plan_single_node_with_qwen(self, node: Dict, context: Dict) -> Dict:
        """
        使用 Qwen 对单个节点进行规划。
        """
        # 假设我们有一个与Qwen交互的方法，这里简化表示
        response = self._call_llm(
            f"基于以下上下文：{context}, 为节点 {node['properties']} 规划执行参数。",
            node["properties"]
        )
        
        return {
            "intent": response.get("intent", ""),
            "parameters": response.get("params", {}),
        }

    def _qwen_plan_scc_group(
        self,
        scc_id: str,
        nodes: List[Dict],
        influence_map: Dict,
        main_intent: str,
        global_memory: str
    ) -> Dict[str, Dict]:
        """
        使用 Qwen 协同规划 SCC 组。
        """
        # 合并所有节点的信息，构建协同提示
        group_info = [node["properties"] for node in nodes]
        prompt = f"对于一组相互依赖的任务（SCC ID: {scc_id}），它们的共同目标是 '{main_intent}'。"
        prompt += "请根据以下信息为每个任务规划执行参数：\n"
        for info in group_info:
            prompt += f"- {info}\n"

        # 假设我们有一个与Qwen交互的方法，这里简化表示
        response = self._call_llm(prompt, {"influence_map": influence_map, "global_memory": global_memory})
        
        # 解析响应，构造返回结果
        task_details = {}
        for node in nodes:
            detail = response.get(node["node_id"], {})
            task_details[node["node_id"]] = {
                "intent": detail.get("intent", ""),
                "parameters": detail.get("params", {}),
            }
        
        return task_details

    def _plan_all_nodes_with_context(
        self,
        node_ids: List[str],
        node_properties: Dict[str, Dict],
        context: Dict,
        original_meta: Dict[str, Dict]
    ) -> Dict[str, Dict]:
        """
        对所有节点进行参数规划，支持 SCC 分组协同。
        """
        if not node_ids:
            return {}

        # Step 1 & 2: 构建图和分组
        dg = nx.DiGraph()
        dg.add_nodes_from(node_ids)
        use_dynamic_scc = False
        scc_groups = {}
        node_to_scc = {}

        for nid in node_ids:
            props = node_properties.get(nid, {})
            scc_id = props.get("scc_id")
            if scc_id is None:
                use_dynamic_scc = True
                break
            node_to_scc[nid] = scc_id
            scc_groups.setdefault(scc_id, []).append({"node_id": nid, "properties": props})

        if use_dynamic_scc:
            # 动态计算 SCC（退化为单点）
            scc_groups = {}
            for nid in node_ids:
                scc_id = f"SINGLE_{nid}"
                node_to_scc[nid] = scc_id
                scc_groups[scc_id] = [{"node_id": nid, "properties": node_properties.get(nid, {})}]

        # Step 3: 规划每个组
        all_task_details = {}
        main_intent = context.get("main_intent", "")
        global_memory = context.get("global_memory", "")

        for scc_id, group_nodes in scc_groups.items():
            if len(group_nodes) == 1:
                node = group_nodes[0]
                fallback_params = original_meta.get(node["node_id"], {}).get("params", "")
                sub_context = {
                    "main_intent": main_intent,
                    "global_memory": global_memory,
                    "step_params": fallback_params
                }
                detail = self._plan_single_node_with_qwen(node, sub_context)
                all_task_details[node["node_id"]] = detail
            else:
                group_plan = self._qwen_plan_scc_group(
                    scc_id=scc_id,
                    nodes=group_nodes,
                    influence_map={},  # 可扩展传入
                    main_intent=main_intent,
                    global_memory=global_memory
                )
                all_task_details.update(group_plan)

        # Step 4: 格式化输出以符合指定格式
        formatted_output = []
        step = 1
        for nid in node_ids:
            detail = all_task_details.get(nid, {})
            formatted_output.append({
                "step": step,
                "type": "AGENT",
                "executor": nid,
                "params": detail.get("parameters", ""),
                "description": detail.get("intent", f"Execute {nid}")
            })
            step += 1
        
        return formatted_output


    def _reindex_steps(self, plan: List[Dict]) -> List[Dict]:
        """统一重排 step 字段"""
        for i, step in enumerate(plan):
            step["step"] = i + 1
        return plan

    # =========================================================================
    # 你的核心逻辑集成: plan_subtasks & SCC Helpers
    # =========================================================================

    def plan_subtasks(self, parent_agent_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        规划子任务序列（结构层主入口）
        """
        # 只要能连上 Neo4j 且有 LLM，就尝试协同规划
        if self._structure_repo and self.llm:
            return self._plan_with_qwen_coordinated_scc(parent_agent_id, context)
        else:
            # 降级：仅返回自己
            return [{"node_id": parent_agent_id, "intent_params": {"parameters": context.get('step_params')}}]

    def _plan_with_qwen_coordinated_scc(self, root_code: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        # 1. 获取子图 (带 SCC ID)
        nodes_data, edges_data = self._fetch_subgraph_with_scc_from_neo4j(
            root_code=root_code,
            threshold=context.get("influence_threshold", 0.3)
        )

        if not nodes_data:
            # 没有查到依赖，返回单节点
            return [{"node_id": root_code, "intent_params": {"parameters": context.get('step_params')}}]

        # 2. 按 SCC 分组
        scc_groups = {}
        node_to_scc = {}
        node_properties = {}

        for node in nodes_data:
            nid = node["node_id"]
            props = node.get("properties", {})
            scc_id = props.get("scc_id", f"SCC_SINGLE_{nid}")
            node_properties[nid] = props
            node_to_scc[nid] = scc_id
            scc_groups.setdefault(scc_id, []).append(node)

        # 3. 构建影响映射
        influence_map = {nid: [] for nid in node_properties}
        for edge in edges_data:
            u, v, w = edge["from"], edge["to"], edge.get("weight", 0.0)
            if u in influence_map: influence_map[u].append({"target": v, "strength": round(w, 3)})
            if v in influence_map: influence_map[v].append({"source": u, "strength": round(w, 3)})

        # 4. 协同规划每个 SCC 组
        all_task_details = {}
        for scc_id, group_nodes in scc_groups.items():
            if len(group_nodes) == 1:
                # 单点规划
                detail = self._plan_single_node_with_qwen(group_nodes[0], context)
                all_task_details[group_nodes[0]["node_id"]] = detail
            else:
                # 强耦合组协同规划
                group_plan = self._qwen_plan_scc_group(
                    scc_id=scc_id,
                    nodes=group_nodes,
                    influence_map=influence_map,
                    main_intent=context.get("main_intent", ""),
                    execution_memory=context.get("execution_memory", {})
                )
                all_task_details.update(group_plan)

        # 5. 全局拓扑排序 (处理环)
        dg = nx.DiGraph()
        dg.add_nodes_from(node_properties.keys())
        for e in edges_data:
            dg.add_edge(e["from"], e["to"])
        
        try:
            global_order = list(nx.topological_sort(dg))
        except nx.NetworkXUnfeasible:
            global_order = self._topo_sort_with_scc(dg, node_to_scc)

        # 6. 组装结果
        result = []
        for node_id in global_order:
            if node_id in all_task_details:
                result.append({
                    "node_id": node_id,
                    "intent_params": all_task_details[node_id]
                })
        return result

    def _fetch_subgraph_with_scc_from_neo4j(self, root_code: str, threshold: float = 0.3) -> Tuple[List, List]:
        """连接 Neo4j Repository 获取数据"""
        if not self._structure_repo:
            return [], []
        try:
            # 假设 repo 有此方法
            result = self._structure_repo.get_influenced_subgraph_with_scc(
                root_code=root_code, threshold=threshold, max_hops=5
            )
            return result.get("nodes", []), result.get("edges", [])
        except Exception as e:
            self.logger.warning(f"Neo4j fetch failed: {e}")
            return [], []

    def _qwen_plan_scc_group(self, scc_id, nodes, influence_map, context) -> Dict:
        """
        对强耦合组件进行协同规划。
        在此处，记忆的作用是：确保所有关联节点的参数风格一致且符合用户习惯。
        """
        main_intent = context.get("main_intent", "")
        global_memory = context.get("global_memory", "") # <--- 获取记忆
        node_ids = [n["node_id"] for n in nodes]

        prompt = f"""你是一个高级系统协调 AI。正在为一个强耦合任务组（SCC）生成执行参数。

## 组 ID: {scc_id}
## 包含节点: {json.dumps(node_ids, ensure_ascii=False)}
## 主任务意图: "{main_intent}"

## 🧠 上下文记忆与偏好
{global_memory if global_memory else "无可用记忆"}

## 你的任务
为组内每个节点生成 `intent` 和 `parameters`。
**关键要求**：
1. **一致性**：组内节点的参数必须互相兼容（如：文件路径、版本号）。
2. **个性化**：如果【上下文记忆】中提到了相关偏好（如：超时时间设置、默认审批人、日志级别），请务必应用到参数中。
3. **顺序执行**：尽量根据节点间的seq大小，排序执行。

## 输出 (JSON)
{{
    "task_details": {{
        "node_a": {{ "intent": "...", "parameters": {{ ... }} }},
        "node_b": {{ "intent": "...", "parameters": {{ ... }} }}
    }}
}}
"""
        response = self._call_llm(prompt)
        data = self._parse_llm_json(response)
        if isinstance(data, dict) and "task_details" in data:
            return data["task_details"]
        return {n['node_id']: {"intent": "Coordinated Execution", "parameters": {}} for n in nodes}
    
    
    # 单节点规划也同样注入记忆
    def _plan_single_node_with_qwen(self, node, context):
        global_memory = context.get("global_memory", "")
        prompt = f"""
任务节点: {node['node_id']}
当前意图: {context.get('main_intent')}
用户记忆: {global_memory}

请生成该节点的执行参数 JSON (intent, parameters)。参考用户记忆中的偏好。
"""
        res = self._call_llm(prompt)
        parsed = self._parse_llm_json(res)
        if isinstance(parsed, dict): return parsed
        return {"intent": f"Execute {node['node_id']}", "parameters": {}}
    

    def _topo_sort_with_scc(self, graph: nx.DiGraph, node_to_scc: Dict = None) -> List[str]:
        """处理含环图的拓扑排序"""
        scc_graph = nx.DiGraph()
        scc_map = {}
        
        # 重新计算 SCC（忽略传入的 node_to_scc）
        for idx, comp in enumerate(nx.strongly_connected_components(graph)):
            scc_id = f"SCC_{idx}"
            for node in comp:
                scc_map[node] = scc_id
            scc_graph.add_node(scc_id)
        
        for u, v in graph.edges():
            if scc_map[u] != scc_map[v]:
                scc_graph.add_edge(scc_map[u], scc_map[v])
        
        try:
            scc_order = list(nx.topological_sort(scc_graph))
        except:
            scc_order = list(scc_graph.nodes)
        
        # 展开 SCC 内部（顺序不重要，或可按字母排）
        reverse_map = {}
        for node, sid in scc_map.items():
            reverse_map.setdefault(sid, []).append(node)
        
        final_order = []
        for sid in scc_order:
            nodes_in_scc = sorted(reverse_map.get(sid, []))  # 确定性排序
            final_order.extend(nodes_in_scc)
        return final_order

    # =========================================================================
    # Helpers (复用之前的)
    # =========================================================================
    
    def _get_candidate_agents_info(self, agent_id: str) -> List[Dict]:
        """获取子节点的详细描述，供 LLM 判断边界"""
        if not self.tree_manager:
            return []
        
        children_ids = self.tree_manager.get_children(agent_id)
        info_list = []
        for cid in children_ids:
            meta = self.tree_manager.get_agent_meta(cid)
            if meta:
                info_list.append({
                    "id": cid,
                    "seq":meta.get("seq", 100),
                    "name": meta.get("name", "Unknown"),
                    "capabilities": meta.get("capability", []), # 假设这是一个列表或描述字符串
                    "description": meta.get("description", "")
                })
        return info_list

    def _build_planning_prompt(self, user_input: str, memory_context: str, agents: List[Dict]) -> str:
        # 序列化可用 Agent 列表
        agents_str = json.dumps(agents, ensure_ascii=False, indent=2)
        mem_str = memory_context if memory_context else "无"

        return (
            f"""
你是一个高级任务编排专家。请根据【用户指令】制定一个分步执行计划。

### 可用的内部 Agent 节点（Internal Agents）
{agents_str}

### 任务上下文
{mem_str}

### 用户指令
"{user_input}"

### 你的工作要求
1. **拆解任务**：将用户指令拆解为逻辑顺畅的步骤链。
2. **能力匹配（关键）**：
   - 如果某个步骤的任务可以通过上述【内部 Agent 节点】完成，请标记 `type` 为 "AGENT"，并准确填入 `executor` (即 agent id)。
   - 如果某个步骤的任务**不在**上述 Agent 能力范围内（例如发邮件、提交OA、操作系统文件等），请标记 `type` 为 "MCP"，并给出一个建议的工具名称作为 `executor`。
3. **参数提取**：从指令中提取该步骤需要的关键参数。

### 输出格式
请**仅**输出一个标准的 JSON 列表，不要包含 Markdown 标记（如 ```json）。格式范例如下：
[
    {{
        "step": 1,
        "description": "分析文档需求",
        "type": "AGENT",
        "executor": "analyzer_agent",
        "params": "需分析的数据..."
    }},
    {{
        "step": 2,
        "description": "发送邮件给某人",
        "type": "MCP",
        "executor": "email_client",
        "params": "收件人: xxx"
    }}
]
"""
        )

    def _parse_llm_json(self, text: str) -> List[Dict]:
        """健壮的 JSON 解析器，处理 LLM 可能返回的代码块标记"""
        if not text:
            return []
        
        # 1. 清洗：移除 markdown 代码块标记 ```json ... ```
        cleaned_text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r'```', '', cleaned_text)
        cleaned_text = cleaned_text.strip()
        
        try:
            data = json.loads(cleaned_text)
            if isinstance(data, list):
                return data
            # 如果 LLM 包裹了一层字典
            if isinstance(data, dict) and 'plan' in data:
                return data['plan']
            return []
        except json.JSONDecodeError:
            self.logger.error(f"JSON Parse Error. Raw Text: {text}")
            # 尝试用正则提取列表部分（容错）
            match = re.search(r'\[.*\]', cleaned_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            return []

    def _call_llm(self, prompt: str, agent_id: str = "") -> str:
        """统一调用 LLM"""
        # 使用 property 获取 LLM（延迟加载）
        # 注意：token 记录已在 QwenLLM 中完成，这里不再重复记录
        try:
            response = self.llm.generate(prompt)
            return response
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            return ""
