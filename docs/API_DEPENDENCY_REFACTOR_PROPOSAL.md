# API 依赖推断架构重构方案

## 问题诊断

### 当前架构的问题

```python
# graph_builder.py
def build():
    # ✅ 正确：纯 API 级字段匹配
    inferred_field = self._infer_field_dependencies(session, api_map)

    # ❌ 问题：基于 entity 分组的推断
    inferred_entity = self._infer_entity_dependencies(session, api_map)
```

**`_infer_entity_dependencies()` 调用的是 `dynamic_entity_inferrer.py`**，它的所有方法都基于 entity 分组：

```python
# dynamic_entity_inferrer.py
def infer_dependencies(self, api_map):
    # 先按 entity 分组
    entity_groups = self._group_by_entity(api_map)

    # ❌ 问题：所有推断都基于 entity_groups
    schema_deps = self._infer_from_schema_references(api_map, entity_groups)
    crud_deps = self._infer_crud_dependencies(entity_groups)
    path_deps = self._infer_from_path_hierarchy(api_map, entity_groups)
```

这导致：
1. **Schema Reference** 只能找到已知 entity 之间的依赖
2. **CRUD Flow** 只能在同一 entity 内推断
3. **Path Hierarchy** 也受限于 entity 分组

## 正确的架构

### 原则：以 API 为实，以 Entity 为虚

```
第一层：API 级依赖发现（实 - 物理事实）
  ├─ Field Matching（字段匹配）- 已有 ✅
  ├─ Schema Reference（字段引用）- 需要改为 API 级 ❌
  ├─ Path Hierarchy（路径层级）- 需要改为 API 级 ❌
  └─ LLM Inference（智能推断）- 可选

第二层：Entity 级聚合（虚 - 视图层）
  └─ 从 API 依赖聚合到 Entity 关系
```

### 重构方案

#### 1. 保留现有的 API 级推断

```python
# graph_builder.py
def _infer_field_dependencies(self, session, api_map):
    """✅ 保持不变 - 纯 API 级字段匹配"""
    # 遍历所有 API 对
    for source_api in api_list:
        for target_api in api_list:
            # 字段匹配
            score = self.matcher.calculate_score(...)
            if score >= threshold:
                # 创建 API 依赖
                session.run("CREATE (a)-[:DEPENDS_ON]->(b)")
```

#### 2. 新增纯 API 级的推断方法

```python
# 新文件：api_topology/api_dependency_inferrer.py

class APIDependencyInferrer:
    """
    纯 API 级依赖推断（不依赖 entity 分组）
    """

    def infer_from_schema_references(self, api_map):
        """
        从字段引用推断 API 依赖（不依赖 entity）

        逻辑：
        - 如果 API A 的 request 有 "customer_id" 字段
        - 遍历所有 API，找到 response 包含 "customer_id" 或 "id" 的
        - 创建 A -> B 依赖
        """
        dependencies = []

        for source_op_id, source_api in api_map.items():
            # 提取 request 字段
            request_fields = self._extract_field_names(source_api, 'request')

            for field_name in request_fields:
                # 查找可能的 ID 字段（如 customer_id, product_id）
                if self._is_id_field(field_name):
                    # 提取实体名（customer_id -> customer）
                    entity_name = self._extract_entity_name(field_name)

                    # 遍历所有 API，找到可能提供这个 ID 的
                    for target_op_id, target_api in api_map.items():
                        if source_op_id == target_op_id:
                            continue

                        # 检查 target API 是否提供这个字段
                        if self._api_provides_field(target_api, field_name, entity_name):
                            dependencies.append({
                                'source': source_op_id,
                                'target': target_op_id,
                                'score': 0.8,
                                'type': 'SCHEMA_REFERENCE',
                                'field': field_name,
                                'reason': f"Requires field '{field_name}'"
                            })

        return dependencies

    def infer_from_path_hierarchy(self, api_map):
        """
        从路径层级推断 API 依赖（不依赖 entity）

        逻辑：
        - /order/{id}/items 依赖 /order/{id}
        - /user/{id}/orders 依赖 /user/{id}
        """
        dependencies = []

        for source_op_id, source_api in api_map.items():
            source_path = source_api.get('path', '')

            # 提取路径段
            source_segments = self._parse_path(source_path)

            # 查找父路径
            for target_op_id, target_api in api_map.items():
                if source_op_id == target_op_id:
                    continue

                target_path = target_api.get('path', '')
                target_segments = self._parse_path(target_path)

                # 检查是否是父子关系
                if self._is_parent_path(target_segments, source_segments):
                    dependencies.append({
                        'source': source_op_id,
                        'target': target_op_id,
                        'score': 0.7,
                        'type': 'PATH_HIERARCHY',
                        'reason': f"Path hierarchy: {target_path} is parent of {source_path}"
                    })

        return dependencies

    def infer_crud_patterns(self, api_map):
        """
        从 CRUD 模式推断 API 依赖（不依赖 entity）

        逻辑：
        - UPDATE 操作通常依赖 GET 操作（同一资源）
        - DELETE 操作通常依赖 GET 操作（同一资源）
        """
        dependencies = []

        # 按路径基础分组（去掉操作后缀）
        path_groups = defaultdict(list)
        for op_id, api in api_map.items():
            path = api.get('path', '')
            base_path = self._get_base_path(path)  # /order/update -> /order
            path_groups[base_path].append((op_id, api))

        # 在同一路径组内推断 CRUD 依赖
        for base_path, apis in path_groups.items():
            update_apis = []
            delete_apis = []
            get_apis = []

            for op_id, api in apis:
                op_type = self._get_operation_type(api)
                if op_type == 'update':
                    update_apis.append(op_id)
                elif op_type == 'delete':
                    delete_apis.append(op_id)
                elif op_type in ['get', 'list', 'page']:
                    get_apis.append(op_id)

            # UPDATE -> GET
            for update_op in update_apis:
                for get_op in get_apis:
                    dependencies.append({
                        'source': update_op,
                        'target': get_op,
                        'score': 0.8,
                        'type': 'CRUD_PATTERN',
                        'reason': f"Update requires fetching current data"
                    })

            # DELETE -> GET
            for delete_op in delete_apis:
                for get_op in get_apis:
                    dependencies.append({
                        'source': delete_op,
                        'target': get_op,
                        'score': 0.6,
                        'type': 'CRUD_PATTERN',
                        'reason': f"Delete may require verification"
                    })

        return dependencies
```

#### 3. 修改 graph_builder.py

```python
# graph_builder.py

from .api_dependency_inferrer import APIDependencyInferrer

class GraphBuilder:
    def __init__(self, ...):
        self.matcher = FieldMatcher(llm_client=llm_client)
        self.api_inferrer = APIDependencyInferrer()  # 新增
        self.entity_relationship_builder = EntityRelationshipBuilder()

    def build(self, capabilities, dependencies=None):
        with self.driver.session() as session:
            # 清空图
            session.run("MATCH (n) DETACH DELETE n")

            api_map = {}

            # Step 1: 创建 API 节点
            for cap in capabilities:
                for api in cap.get('apis', []):
                    session.run("CREATE (a:API {...})")
                    api_map[api['operation_id']] = {...}

            # Step 2: API 级依赖推断（实 - 物理事实）
            all_api_deps = []

            # 2.1 字段匹配（已有）
            field_deps = self._infer_field_dependencies_to_list(api_map)
            all_api_deps.extend(field_deps)

            # 2.2 Schema Reference（新 - 纯 API 级）
            schema_deps = self.api_inferrer.infer_from_schema_references(api_map)
            all_api_deps.extend(schema_deps)

            # 2.3 Path Hierarchy（新 - 纯 API 级）
            path_deps = self.api_inferrer.infer_from_path_hierarchy(api_map)
            all_api_deps.extend(path_deps)

            # 2.4 CRUD Patterns（新 - 纯 API 级）
            crud_deps = self.api_inferrer.infer_crud_patterns(api_map)
            all_api_deps.extend(crud_deps)

            # 2.5 LLM Inference（可选）
            if self.llm_client:
                llm_deps = self._infer_llm_dependencies(api_map)
                all_api_deps.extend(llm_deps)

            # 去重
            all_api_deps = self._deduplicate_dependencies(all_api_deps)

            # 创建 API 依赖边
            api_dep_count = self._create_api_dependencies(session, all_api_deps)

            # Step 3: Entity 级聚合（虚 - 视图层）
            entity_stats = self._build_entity_skeleton(session, api_map, all_api_deps)

            return {
                'apis_created': len(api_map),
                'api_dependencies': api_dep_count,
                'entities_created': entity_stats['entities'],
                'entity_relationships': entity_stats['relationships']
            }

    def _infer_field_dependencies_to_list(self, api_map):
        """
        修改现有的 _infer_field_dependencies，返回依赖列表而不是直接创建
        """
        dependencies = []

        api_list = list(api_map.values())
        for i, source_api in enumerate(api_list):
            response_fields = source_api.get('response_fields', [])
            if not response_fields:
                continue

            for target_api in api_list[i+1:]:
                request_fields = target_api.get('request_fields', [])
                if not request_fields:
                    continue

                # 字段匹配
                best_score = 0.0
                matched_fields = []

                for resp_field in response_fields:
                    for req_field in request_fields:
                        score = self.matcher.calculate_score(...)
                        if score > best_score:
                            best_score = score
                            matched_fields.append({...})

                if best_score >= self.matcher.final_threshold:
                    dependencies.append({
                        'source': source_api['operation_id'],
                        'target': target_api['operation_id'],
                        'score': best_score,
                        'type': 'FIELD_MATCH',
                        'matched_fields': matched_fields
                    })

        return dependencies

    def _create_api_dependencies(self, session, dependencies):
        """批量创建 API 依赖边"""
        count = 0
        for dep in dependencies:
            session.run("""
                MATCH (a:API {operation_id: $source})
                MATCH (b:API {operation_id: $target})
                MERGE (a)-[r:DEPENDS_ON]->(b)
                SET r.score = $score,
                    r.type = $type,
                    r.reason = $reason,
                    r.field = $field
            """,
                source=dep['source'],
                target=dep['target'],
                score=dep['score'],
                type=dep['type'],
                reason=dep.get('reason', ''),
                field=dep.get('field', '')
            )
            count += 1
        return count

    def _build_entity_skeleton(self, session, api_map, api_dependencies):
        """
        从 API 依赖聚合到 Entity 层（虚 - 视图层）
        """
        # 1. 创建 Entity 节点
        entities = self._create_entity_nodes(session, api_map)

        # 2. 创建 BELONGS_TO 关系
        self._create_belongs_to_relationships(session, api_map)

        # 3. 聚合 Entity 依赖（带锚点）
        relationships = self.entity_relationship_builder.aggregate_from_api_dependencies(
            session, api_map, api_dependencies
        )

        # 4. 标注 API 角色
        self._annotate_api_roles(session)

        return {
            'entities': entities,
            'relationships': relationships
        }
```

## 关键改进

### 1. 分离关注点

- **APIDependencyInferrer**：纯 API 级推断，不依赖 entity
- **EntityRelationshipBuilder**：从 API 依赖聚合到 Entity 层

### 2. 推断流程

```
API 级推断（实）:
  ├─ Field Matching: 字段匹配
  ├─ Schema Reference: customer_id -> 找提供 customer_id 的 API
  ├─ Path Hierarchy: /order/{id}/items -> /order/{id}
  ├─ CRUD Patterns: updateOrder -> getOrder
  └─ LLM Inference: 智能推断
         ↓
  去重 + 创建 DEPENDS_ON 边
         ↓
Entity 级聚合（虚）:
  ├─ 创建 Entity 节点
  ├─ 创建 BELONGS_TO 关系
  ├─ 聚合 REQUIRES_DATA 边（带锚点）
  └─ 标注 API 角色
```

### 3. 优势

1. **纯 API 级推断**：不受 entity 分组限制
2. **更全面的依赖发现**：可以发现任意 API 之间的依赖
3. **清晰的分层**：API 层（实）和 Entity 层（虚）完全分离
4. **易于扩展**：可以轻松添加新的 API 级推断方法

## 实现步骤

1. 创建 `api_dependency_inferrer.py`
2. 修改 `graph_builder.py` 的 `build()` 方法
3. 修改 `_infer_field_dependencies()` 返回列表
4. 新增 `_create_api_dependencies()` 批量创建边
5. 修改 `_build_entity_skeleton()` 使用新的聚合逻辑
6. 保留 `entity_relationship_builder.py`（用于聚合）
7. 废弃 `dynamic_entity_inferrer.py`（或重构为纯聚合器）

## 总结

核心改变：
- ❌ 删除：基于 entity 分组的 API 推断
- ✅ 新增：纯 API 级的推断方法
- ✅ 保留：Entity 级聚合（从 API 依赖聚合）

这样就真正实现了"以 API 为实，以 Entity 为虚"的架构。
