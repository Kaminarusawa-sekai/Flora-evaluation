# COOP 递进规划问题分析与修复方案

## 问题分析

### 当前流程

```
AgentActor (root: erp_company_core_roles_overview)
    │
    ├─ _plan_task_execution()
    │   └─ task_planner.generate_execution_plan(agent_id, task_description)
    │       └─ _semantic_decomposition(agent_id, ...)
    │           └─ _get_candidate_agents_info(agent_id)  # 获取子节点
    │               └─ tree_manager.get_children(agent_id)  # 返回 4 个一级子节点
    │
    └─ 规划结果: [erp_product_system, erp_sales_system, ...]  # 一级子节点
        │
        └─ TaskGroupAggregatorActor 执行
            └─ ResultAggregatorActor
                └─ LeafActor (erp_product_system)  # 错误！这不是叶子节点
                    └─ ExecutionActor (Mock 执行)
```

### 问题根源

1. **`_get_candidate_agents_info`** 只获取**直接子节点**（一级），不递归
2. **`AgentActor`** 规划后直接发给 `TaskGroupAggregatorActor` 执行
3. **`ResultAggregatorActor._is_leaf_node`** 判断节点是否为叶子，但 `TreeManager` 在评估模式下没有正确加载树结构
4. **结果**：中间节点被当作叶子节点执行，没有继续递进

### 期望流程

```
AgentActor (root)
    │
    ├─ 规划: [erp_product_system]  # 选择一级子节点
    │
    └─ TaskGroupAggregatorActor
        └─ ResultAggregatorActor
            └─ AgentActor (erp_product_system)  # 递归！不是 LeafActor
                │
                ├─ 规划: [erp_product_system__sku_master_data_specialist]  # 二级
                │
                └─ TaskGroupAggregatorActor
                    └─ ResultAggregatorActor
                        └─ AgentActor (erp_product_system__sku_master_data_specialist)
                            │
                            └─ ... 继续递进直到叶子节点
                                │
                                └─ LeafActor (真正的叶子)
                                    └─ ExecutionActor (Mock)
```

## 修复方案

### 方案 A：修复 TreeManager 的叶子节点判断（推荐）

**问题**：`ResultAggregatorActor._is_leaf_node` 使用 `TreeManager().get_children(agent_id)`，但在评估模式下 TreeManager 没有正确加载树结构。

**修复**：确保 `load_agents_into_tree` 正确设置 TreeManager 的结构。

```python
# coop_eval_actual/coop_runner.py
class CoopRunner:
    def __init__(self, ...):
        # 加载树结构到 treeManager
        self.nodes = load_agents_into_tree(records_path, treeManager)

        # 确保 treeManager 可以正确判断叶子节点
        # 问题：每个 Actor 可能创建新的 TreeManager 实例
```

**关键修复点**：`ResultAggregatorActor._is_leaf_node` 创建了新的 `TreeManager()` 实例，而不是使用全局的 `treeManager`。

```python
# tasks/capability_actors/result_aggregator_actor.py (当前代码)
def _is_leaf_node(self, agent_id: str) -> bool:
    from agents.tree.tree_manager import TreeManager
    tree_manager = TreeManager()  # ❌ 新实例，没有数据
    children = tree_manager.get_children(agent_id)
    return len(children) == 0
```

**修复**：
```python
def _is_leaf_node(self, agent_id: str) -> bool:
    from agents.tree.tree_manager import treeManager  # ✅ 使用全局单例
    children = treeManager.get_children(agent_id)
    return len(children) == 0
```

### 方案 B：在 Agent 记录中预标记叶子节点

**思路**：在加载 Agent 时就标记 `is_leaf`，然后通过 `agent_meta` 传递。

```python
# agent_tree_loader.py 已经做了这个
def _mark_leaf_nodes(nodes):
    parent_ids = {n.get("parent_id") for n in nodes if n.get("parent_id")}
    for node in nodes:
        node["is_leaf"] = node["agent_id"] not in parent_ids
```

**修复**：让 `ResultAggregatorActor` 使用 `agent_meta.is_leaf` 而不是查询 TreeManager。

```python
def _is_leaf_node(self, agent_id: str) -> bool:
    if not self.registry:
        return True  # 安全默认
    agent_info = self.registry.get_agent_meta(agent_id)
    return agent_info.get("is_leaf", True) if agent_info else True
```

### 方案 C：修改评估数据集，期望中间节点

**思路**：既然 COOP 的优势是递进规划，数据集的 `expected_agents` 应该是**执行路径**而不是**叶子节点**。

```python
# 当前数据集
{
    "expected_agents": ["erp_product_system__sku_master_data_specialist__master_data_entry__delete_product"]
}

# 修改为执行路径
{
    "expected_agents": ["erp_product_system", "erp_product_system__sku_master_data_specialist", "..."]
}
```

**问题**：这改变了评估标准，不公平。

## 推荐实施顺序

### 第一步：修复 `_is_leaf_node`（方案 A）

修改 `tasks/capability_actors/result_aggregator_actor.py`：

```python
def _is_leaf_node(self, agent_id: str) -> bool:
    """
    判断当前Agent是否为叶子节点
    通过 registry (treeManager) 查询是否有子节点
    """
    if not self.registry:
        # 没有 registry 时，检查 agent_meta
        return True

    children = self.registry.get_children(agent_id)
    return len(children) == 0
```

### 第二步：确保 TreeManager 数据正确加载

检查 `load_agents_into_tree` 是否正确设置了 `treeManager` 的 `structure`。

### 第三步：验证递进流程

运行实验，观察日志：
- 应该看到多层 `AgentActor` 创建
- 最终只有叶子节点创建 `LeafActor`

## 预期结果

修复后：
```
COOP: executed=["erp_product_system__sku_master_data_specialist__master_data_entry__delete_product", ...]
```

而不是：
```
COOP: executed=["erp_product_system", "erp_product_system", ...]
```

## 文件变更清单

| 文件 | 变更 |
|------|------|
| `tasks/capability_actors/result_aggregator_actor.py` | 修复 `_is_leaf_node` 使用全局 treeManager |
| `coop_eval_actual/agent_tree_loader.py` | 确保 `is_leaf` 标记正确传递 |
| `coop_eval_actual/coop_runner.py` | 验证 treeManager 初始化顺序 |
