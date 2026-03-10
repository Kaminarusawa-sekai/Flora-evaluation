"""Generate test paths from API topology and create test themes."""

from typing import List, Dict, Any, Optional
import json
import random


class PathGenerator:
    """
    Generate test paths from API topology.

    核心逻辑：
    1. 从拓扑中发现可能的 API 路径（基于实体和依赖关系）
    2. 为每条路径生成测试主题（根据路径功能起名）
    3. 输出路径+主题供场景生成使用
    """

    def __init__(self, llm_client=None):
        """
        Initialize path generator.

        Args:
            llm_client: Optional LLM client (OpenAI-compatible) for theme generation
        """
        self.llm_client = llm_client

    def generate_paths(self,
                      topology_data: Dict[str, Any],
                      max_paths: int = 10,
                      max_path_length: int = 6,
                      min_path_length: int = 2) -> List[Dict[str, Any]]:
        """
        从拓扑中发现路径，并为每条路径生成测试主题。

        工作流程：
        1. 从拓扑中提取实体和 API 依赖关系
        2. 基于实体内的强关联 API 生成候选路径
        3. 使用 LLM 为每条路径生成测试主题和描述
        4. 返回路径+主题列表

        Args:
            topology_data: API topology data including:
                - apis: List of API details
                - dependencies: API dependency relationships
                - entities: Entity information
            max_paths: Maximum number of paths to generate
            max_path_length: Maximum length of each path
            min_path_length: Minimum length of each path

        Returns:
            List of paths with generated themes:
            [
                {
                    "path": ["api1", "api2", "api3"],
                    "test_objective": "测试用户下单流程",  # LLM 生成
                    "description": "验证用户从登录到下单的完整流程",  # LLM 生成
                    "scenario_type": "normal",
                    "parameter_flow": {...}
                }
            ]
        """
        # Step 1: 从拓扑中发现候选路径
        candidate_paths = self._discover_paths_from_topology(
            topology_data,
            max_paths * 3,  # 生成更多候选，后续筛选
            max_path_length,
            min_path_length
        )

        # Step 2: 为路径生成测试主题
        paths_with_themes = self._generate_themes_for_paths(
            candidate_paths,
            topology_data,
            max_paths
        )

        return paths_with_themes[:max_paths]

    def _discover_paths_from_topology(self,
                                     topology_data: Dict[str, Any],
                                     max_candidates: int,
                                     max_length: int,
                                     min_length: int) -> List[Dict[str, Any]]:
        """
        从拓扑中发现候选路径。

        策略：
        1. 按实体分组 API
        2. 在每个实体内，基于依赖关系生成路径
        3. 跨实体路径（如果有强依赖）
        4. 优先选择高分依赖关系
        """
        apis = topology_data.get('apis', [])
        dependencies = topology_data.get('dependencies', [])
        entities = topology_data.get('entities', [])

        if not apis:
            return []

        # 构建依赖图
        dep_graph = self._build_dependency_graph(dependencies)

        # 构建实体到 API 的映射
        entity_apis = self._build_entity_api_map(entities, apis)

        candidate_paths = []

        # 策略 1: 在每个实体内生成路径
        for entity_name, entity_api_list in entity_apis.items():
            if len(entity_api_list) < min_length:
                continue

            # 在实体内生成路径
            entity_paths = self._generate_paths_within_entity(
                entity_api_list,
                dep_graph,
                max_length,
                min_length
            )

            for path in entity_paths:
                candidate_paths.append({
                    'path': path,
                    'entity': entity_name,
                    'type': 'within_entity'
                })

        # 策略 2: 跨实体路径（基于强依赖）
        cross_entity_paths = self._generate_cross_entity_paths(
            entity_apis,
            dep_graph,
            max_length,
            min_length
        )

        for path in cross_entity_paths:
            candidate_paths.append({
                'path': path,
                'entity': 'cross_entity',
                'type': 'cross_entity'
            })

        # 策略 3: 如果候选不足，生成随机路径
        if len(candidate_paths) < max_candidates:
            random_paths = self._generate_random_paths(
                apis,
                dep_graph,
                max_candidates - len(candidate_paths),
                max_length,
                min_length
            )

            for path in random_paths:
                candidate_paths.append({
                    'path': path,
                    'entity': 'random',
                    'type': 'random'
                })

        # 去重
        seen = set()
        unique_paths = []
        for p in candidate_paths:
            path_key = tuple(p['path'])
            if path_key not in seen:
                seen.add(path_key)
                unique_paths.append(p)

        return unique_paths[:max_candidates]

    def _generate_paths_within_entity(self,
                                     api_list: List[str],
                                     dep_graph: Dict[str, List[tuple]],
                                     max_length: int,
                                     min_length: int) -> List[List[str]]:
        """在单个实体内生成路径（基于依赖关系）"""
        paths = []

        # 找到入口点（没有依赖或依赖少的 API）
        entry_points = self._find_entry_points(api_list, dep_graph)

        for entry in entry_points:
            # 从入口点开始，沿着依赖关系构建路径
            path = self._build_path_from_entry(
                entry,
                dep_graph,
                api_list,
                max_length
            )

            if len(path) >= min_length:
                paths.append(path)

        return paths

    def _generate_cross_entity_paths(self,
                                    entity_apis: Dict[str, List[str]],
                                    dep_graph: Dict[str, List[tuple]],
                                    max_length: int,
                                    min_length: int) -> List[List[str]]:
        """生成跨实体路径（基于强依赖关系）"""
        paths = []

        # 找到跨实体的强依赖
        for entity1, apis1 in entity_apis.items():
            for api1 in apis1:
                if api1 not in dep_graph:
                    continue

                for target_api, score in dep_graph[api1]:
                    # 检查 target_api 是否属于不同实体
                    target_entity = None
                    for entity2, apis2 in entity_apis.items():
                        if target_api in apis2 and entity2 != entity1:
                            target_entity = entity2
                            break

                    if target_entity and score > 0.7:  # 强依赖
                        # 构建跨实体路径
                        path = [api1, target_api]

                        # 尝试扩展路径
                        current = target_api
                        while len(path) < max_length and current in dep_graph:
                            next_apis = [api for api, s in dep_graph[current] if api not in path and s > 0.6]
                            if not next_apis:
                                break
                            current = next_apis[0]
                            path.append(current)

                        if len(path) >= min_length:
                            paths.append(path)

        return paths

    def _generate_random_paths(self,
                              apis: List[Dict[str, Any]],
                              dep_graph: Dict[str, List[tuple]],
                              count: int,
                              max_length: int,
                              min_length: int) -> List[List[str]]:
        """生成随机路径（用于补充候选）"""
        paths = []

        for _ in range(count):
            if not apis:
                break

            start_api = random.choice(apis)
            start_id = start_api.get('operation_id')

            path = self._build_path_from_entry(
                start_id,
                dep_graph,
                [api.get('operation_id') for api in apis],
                max_length
            )

            if len(path) >= min_length:
                paths.append(path)

        return paths

    def _build_dependency_graph(self, dependencies: List[Dict[str, Any]]) -> Dict[str, List[tuple]]:
        """构建依赖图：{source: [(target, score), ...]}"""
        graph = {}

        for dep in dependencies:
            source = dep.get('from') or dep.get('source')
            target = dep.get('to') or dep.get('target')
            score = dep.get('score', 0.5)

            if source and target:
                if source not in graph:
                    graph[source] = []
                graph[source].append((target, score))

        # 按分数排序
        for source in graph:
            graph[source].sort(key=lambda x: x[1], reverse=True)

        return graph

    def _build_entity_api_map(self,
                             entities: List[Dict[str, Any]],
                             apis: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """构建实体到 API 的映射"""
        entity_map = {}

        # 从 entities 构建
        for entity in entities:
            name = entity.get('name')
            api_list = entity.get('apis', [])
            if name and api_list:
                entity_map[name] = api_list

        # 如果没有实体信息，从 API 的 entity 字段构建
        if not entity_map:
            for api in apis:
                entity = api.get('entity')
                op_id = api.get('operation_id')
                if entity and op_id:
                    if entity not in entity_map:
                        entity_map[entity] = []
                    entity_map[entity].append(op_id)

        return entity_map

    def _find_entry_points(self,
                          api_list: List[str],
                          dep_graph: Dict[str, List[tuple]]) -> List[str]:
        """找到入口点（没有被依赖或依赖少的 API）"""
        # 统计每个 API 被依赖的次数
        depended_count = {}
        for api in api_list:
            depended_count[api] = 0

        for source, targets in dep_graph.items():
            if source not in api_list:
                continue
            for target, _ in targets:
                if target in api_list:
                    depended_count[target] = depended_count.get(target, 0) + 1

        # 选择被依赖少的作为入口点
        entry_points = sorted(api_list, key=lambda x: depended_count.get(x, 0))

        return entry_points[:3]  # 返回前 3 个

    def _build_path_from_entry(self,
                               entry: str,
                               dep_graph: Dict[str, List[tuple]],
                               allowed_apis: List[str],
                               max_length: int) -> List[str]:
        """从入口点构建路径"""
        path = [entry]
        visited = {entry}
        current = entry

        while len(path) < max_length:
            if current not in dep_graph:
                break

            # 找到下一个未访问的依赖
            next_api = None
            for target, score in dep_graph[current]:
                if target not in visited and target in allowed_apis:
                    next_api = target
                    break

            if not next_api:
                break

            path.append(next_api)
            visited.add(next_api)
            current = next_api

        return path

    def _generate_themes_for_paths(self,
                                  candidate_paths: List[Dict[str, Any]],
                                  topology_data: Dict[str, Any],
                                  max_paths: int) -> List[Dict[str, Any]]:
        """
        为候选路径生成测试主题。

        使用 LLM 根据路径中的 API 功能，生成合适的测试主题和描述。
        """
        if self.llm_client:
            return self._generate_themes_with_llm(candidate_paths, topology_data, max_paths)
        else:
            return self._generate_themes_heuristic(candidate_paths, topology_data)

    def _generate_themes_with_llm(self,
                                 candidate_paths: List[Dict[str, Any]],
                                 topology_data: Dict[str, Any],
                                 max_paths: int) -> List[Dict[str, Any]]:
        """使用 LLM 为路径生成测试主题"""

        # 构建 API 信息映射
        api_map = {api['operation_id']: api for api in topology_data.get('apis', [])}

        # 批量处理路径
        paths_info = []
        for i, path_data in enumerate(candidate_paths[:max_paths]):
            path = path_data['path']

            # 收集路径中每个 API 的信息
            api_descriptions = []
            for api_id in path:
                if api_id in api_map:
                    api = api_map[api_id]
                    desc = f"{api.get('method', 'GET')} {api.get('path', '')} - {api.get('summary', api_id)}"
                    api_descriptions.append(desc)
                else:
                    api_descriptions.append(api_id)

            paths_info.append({
                'index': i,
                'path': path,
                'descriptions': api_descriptions
            })

        # 构建 LLM prompt
        paths_text = "\n\n".join([
            f"路径 {p['index'] + 1}:\n" + "\n".join([f"  {i+1}. {desc}" for i, desc in enumerate(p['descriptions'])])
            for p in paths_info
        ])

        prompt = f"""你是一个 API 测试专家。以下是从 API 拓扑中发现的 {len(paths_info)} 条 API 调用路径。

请为每条路径生成一个测试主题和描述。注意：
1. 测试主题应该简洁明了，描述这条路径要测试什么业务功能
2. 描述应该说明这条路径的测试目的和预期验证的内容
3. 根据路径中的 API 判断是正常流程还是异常流程

{paths_text}

请返回 JSON 数组，格式如下：
[
  {{
    "index": 0,
    "test_objective": "测试用户登录并查询订单",
    "description": "验证用户登录后能够成功查询订单列表",
    "scenario_type": "normal"
  }},
  ...
]

只返回 JSON，不要其他文字。"""

        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一个 API 测试专家，擅长为 API 路径设计测试主题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()

            # 提取 JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            themes = json.loads(content)

            # 合并主题到路径
            result = []
            for theme in themes:
                idx = theme.get('index', 0)
                if idx < len(candidate_paths):
                    path_data = candidate_paths[idx]
                    result.append({
                        'path': path_data['path'],
                        'test_objective': theme.get('test_objective', '测试 API 路径'),
                        'description': theme.get('description', ''),
                        'scenario_type': theme.get('scenario_type', 'normal'),
                        'parameter_flow': self._infer_parameter_flow(path_data['path'], topology_data)
                    })

            return result

        except Exception as e:
            print(f"LLM theme generation failed: {e}, falling back to heuristic")
            return self._generate_themes_heuristic(candidate_paths, topology_data)

    def _generate_themes_heuristic(self,
                                  candidate_paths: List[Dict[str, Any]],
                                  topology_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """使用启发式方法为路径生成测试主题"""

        api_map = {api['operation_id']: api for api in topology_data.get('apis', [])}

        result = []

        for path_data in candidate_paths:
            path = path_data['path']

            # 收集路径中的 API 摘要
            summaries = []
            for api_id in path:
                if api_id in api_map:
                    summary = api_map[api_id].get('summary', api_id)
                    summaries.append(summary)
                else:
                    summaries.append(api_id)

            # 生成简单的测试主题
            if len(summaries) > 0:
                test_objective = f"测试 {summaries[0]}"
                if len(summaries) > 1:
                    test_objective += f" 到 {summaries[-1]} 的流程"

                description = f"验证 {' -> '.join(summaries[:3])} 的业务流程"
            else:
                test_objective = f"测试 API 路径"
                description = f"验证 {' -> '.join(path[:3])} 的调用流程"

            result.append({
                'path': path,
                'test_objective': test_objective,
                'description': description,
                'scenario_type': 'normal',
                'parameter_flow': self._infer_parameter_flow(path, topology_data)
            })

        return result

    def _infer_parameter_flow(self,
                             path: List[str],
                             topology_data: Dict[str, Any]) -> Dict[str, Any]:
        """推断路径中的参数流"""

        api_map = {api['operation_id']: api for api in topology_data.get('apis', [])}

        parameter_flow = {}

        for i in range(1, len(path)):
            current_api = path[i]

            if current_api not in api_map:
                continue

            current_params = api_map[current_api].get('parameters', [])

            # 确保 current_params 不是 None
            if current_params is None:
                current_params = []

            # 如果是字符串，尝试解析
            if isinstance(current_params, str):
                try:
                    import ast
                    current_params = ast.literal_eval(current_params)
                except:
                    current_params = []

            # 查找参数来源
            for param in current_params:
                param_name = param.get('name') if isinstance(param, dict) else param

                # 检查前面的 API 是否提供此参数
                for j in range(i):
                    prev_api = path[j]
                    if prev_api not in api_map:
                        continue

                    prev_responses = api_map[prev_api].get('responses', {})

                    # 确保 prev_responses 不是 None
                    if prev_responses is None:
                        prev_responses = {}

                    # 如果是字符串，尝试解析
                    if isinstance(prev_responses, str):
                        try:
                            import ast
                            prev_responses = ast.literal_eval(prev_responses)
                        except:
                            prev_responses = {}

                    if self._fields_match(param_name, prev_responses):
                        if current_api not in parameter_flow:
                            parameter_flow[current_api] = {}

                        parameter_flow[current_api][param_name] = f"{prev_api}.response.{param_name}"
                        break

        return parameter_flow

    def _fields_match(self, param_name: str, responses: Any) -> bool:
        """检查参数名是否匹配响应字段"""
        if isinstance(responses, dict):
            return param_name in responses
        elif isinstance(responses, list):
            return any(param_name in str(r) for r in responses)
        return False
