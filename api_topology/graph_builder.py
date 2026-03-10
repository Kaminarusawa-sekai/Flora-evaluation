"""Build API dependency graph in Neo4j."""

from typing import List, Dict, Any, Optional, Set
from neo4j import GraphDatabase
from collections import defaultdict
import re
from .field_matcher import FieldMatcher, FieldMatch
from .path_extractor import PathExtractor
from .transformation_detector import TransformationDetector
from .llm_entity_inferrer import LLMEntityInferrer


class GraphBuilder:
    """Build and store API dependency graphs in Neo4j."""

    def __init__(self, uri: str, user: str, password: str, llm_client=None, use_entity_inference: bool = True):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.matcher = FieldMatcher(llm_client=llm_client)
        self.path_extractor = PathExtractor()
        self.llm_client = llm_client
        self.use_entity_inference = use_entity_inference
        # Initialize LLM entity inferrer with fallback enabled
        self.llm_inferrer = LLMEntityInferrer(llm_client=llm_client, enable_fallback=True) if llm_client else None

    def build(self, capabilities: List[Dict[str, Any]],
              dependencies: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Build graph from capabilities and dependencies using filter strategy."""
        with self.driver.session() as session:
            # Clear existing graph
            session.run("MATCH (n) DETACH DELETE n")

            # Create API nodes with fields
            api_count = 0
            api_map = {}  # operation_id -> api_data

            print("\n[Step 1] Creating API nodes...")
            for cap in capabilities:
                for api in cap.get('apis', []):
                    # Extract fields from different sources
                    response_fields = self._extract_response_fields(api)
                    request_fields = self._extract_request_fields(api)

                    session.run(
                        """
                        CREATE (a:API {
                            operation_id: $operation_id,
                            method: $method,
                            path: $path,
                            summary: $summary,
                            capability: $capability,
                            entity: $entity,
                            resource: $resource,
                            response_fields: $response_fields,
                            request_fields: $request_fields
                        })
                        """,
                        operation_id=api['operation_id'],
                        method=api['method'],
                        path=api['path'],
                        summary=api.get('summary', ''),
                        capability=cap.get('name', ''),
                        entity=api.get('entity_anchor', cap.get('resource', '')),
                        resource=cap.get('resource', ''),
                        response_fields=str(response_fields),
                        request_fields=str(request_fields)
                    )
                    api_map[api['operation_id']] = {
                        **api,
                        'capability': cap.get('name', ''),
                        'entity': api.get('entity_anchor', cap.get('resource', '')),
                        'resource': cap.get('resource', ''),
                        'response_fields': response_fields,
                        'request_fields': request_fields
                    }
                    api_count += 1

            print(f"  Created {api_count} API nodes")

            # Create explicit dependencies
            dep_count = 0
            if dependencies:
                for dep in dependencies:
                    session.run(
                        """
                        MATCH (a:API {operation_id: $from})
                        MATCH (b:API {operation_id: $to})
                        CREATE (a)-[:DEPENDS_ON {score: 1.0, type: 'CERTAIN'}]->(b)
                        """,
                        **dep
                    )
                    dep_count += 1

            # Step 2: Create Entity nodes and BELONGS_TO relationships
            print("\n[Step 2] Creating Entity nodes...")
            entity_count = self._create_entities_and_belongs_to(session, api_map)
            print(f"  Created {entity_count} Entity nodes")

            # Step 3: Infer Entity relationships (骨架)
            print("\n[Step 3] Inferring Entity relationships (骨架)...")
            entity_relations = self._infer_entity_relations(session, api_map)
            print(f"  Inferred {len(entity_relations)} Entity relationships")

            # Step 4: Infer API dependencies with Entity filter (肌肉)
            print("\n[Step 4] Inferring API dependencies with Entity filter (肌肉)...")
            api_deps = self._infer_api_dependencies_with_filter(session, api_map, entity_relations)
            print(f"  Inferred {len(api_deps)} API dependencies")

            # Step 5: Annotate API roles
            print("\n[Step 5] Annotating API roles...")
            self._annotate_api_roles(session)

            return {
                'apis_created': api_count,
                'explicit_dependencies': dep_count,
                'entities_created': entity_count,
                'entity_relationships': len(entity_relations),
                'api_dependencies': len(api_deps),
                'inferred_dependencies': len(api_deps)
            }

    def _create_entities_and_belongs_to(self, session, api_map: Dict[str, Dict]) -> int:
        """创建 Entity 节点和 BELONGS_TO 关系"""
        # 统计每个 entity 的信息
        entity_info = defaultdict(lambda: {
            'apis': [],
            'operations': set()
        })

        for op_id, api in api_map.items():
            entity = api.get('entity')
            if entity and entity != 'unknown':
                entity_info[entity]['apis'].append(op_id)
                # 提取操作类型
                op_type = self._get_operation_type(api)
                entity_info[entity]['operations'].add(op_type)

        # 创建 Entity 节点
        count = 0
        for entity, info in entity_info.items():
            session.run("""
                CREATE (e:Entity {
                    name: $name,
                    api_count: $api_count,
                    operations: $operations
                })
            """,
                name=entity,
                api_count=len(info['apis']),
                operations=list(info['operations'])
            )
            count += 1

        # 创建 BELONGS_TO 关系
        for op_id, api in api_map.items():
            entity = api.get('entity')
            if entity and entity != 'unknown':
                session.run("""
                    MATCH (a:API {operation_id: $op_id})
                    MATCH (e:Entity {name: $entity})
                    CREATE (a)-[:BELONGS_TO]->(e)
                """,
                    op_id=op_id,
                    entity=entity
                )

        return count

    def _infer_entity_relations(self, session, api_map: Dict[str, Dict]) -> List[Dict]:
        """
        推断实体之间的关系（L1 层 - 骨架）

        策略：
        1. LLM 推断（优先）：理解实体语义，如 purchase-order 依赖 supplier
        2. 字段引用推断（降级）：从字段名推断，如 supplier_id → supplier
        3. Path Hierarchy（补充）：从路径推断，如 /order/{id}/items
        """
        entity_relations = []

        # 构建 entity_groups 用于 LLM 推断
        entity_groups = defaultdict(list)
        for op_id, api in api_map.items():
            entity = api.get('entity')
            if entity and entity != 'unknown':
                entity_groups[entity].append(api)

        # 策略1: LLM 推断实体关系（优先级最高）
        if self.llm_inferrer:
            print("  [Strategy 1] LLM entity relationship inference...")
            llm_entity_relations = self._infer_entity_relations_by_llm(entity_groups)
            if llm_entity_relations:
                print(f"  [LLM] Found {len(llm_entity_relations)} entity relationships")
                entity_relations.extend(llm_entity_relations)
            else:
                print("  [LLM] Failed or no results, falling back to rule-based methods")

        # 策略2: 字段引用推断（降级方案）
        print("  [Strategy 2] Field reference inference...")
        field_relations = self._infer_entity_relations_by_fields(api_map, entity_groups)
        entity_relations.extend(field_relations)

        # 策略3: Path Hierarchy 推断（补充）
        print("  [Strategy 3] Path hierarchy inference...")
        path_relations = self._infer_entity_relations_by_path(api_map, entity_groups)
        entity_relations.extend(path_relations)

        # 去重（保留优先级最高的）
        entity_relations = self._deduplicate_entity_relations_with_priority(entity_relations)

        # 创建 Entity 关系边
        for rel in entity_relations:
            session.run("""
                MATCH (e1:Entity {name: $source})
                MATCH (e2:Entity {name: $target})
                MERGE (e1)-[r:RELATES_TO]->(e2)
                SET r.inferred_from = $inferred_from,
                    r.confidence = $confidence,
                    r.example_field = $example_field,
                    r.example_api = $example_api
            """,
                source=rel['source'],
                target=rel['target'],
                inferred_from=rel['inferred_from'],
                confidence=rel.get('confidence', 0.7),
                example_field=rel.get('example_field', ''),
                example_api=rel.get('example_api', '')
            )

            print(f"  {rel['source']} -> {rel['target']} (via {rel['inferred_from']}, confidence={rel.get('confidence', 0.7):.2f})")

        return entity_relations

    def _infer_entity_relations_by_llm(self, entity_groups: Dict[str, List[Dict]]) -> List[Dict]:
        """
        使用 LLM 推断实体之间的关系

        LLM 会分析实体的操作和字段，理解语义关系
        例如：purchase-order 有 supplierId 字段 → purchase-order 依赖 supplier
        """
        if not self.llm_inferrer:
            return []

        # 调用 LLM inferrer 的 infer_dependencies 方法
        # 它会返回 API 级别的依赖，我们需要提取实体级别的关系
        api_map = {}
        for entity, apis in entity_groups.items():
            for api in apis:
                api_map[api['operation_id']] = api

        llm_api_deps = self.llm_inferrer.infer_dependencies(api_map, entity_groups)

        # 从 API 依赖中提取实体关系
        entity_relations = []
        seen = set()

        for dep in llm_api_deps:
            source_api = api_map.get(dep['source'])
            target_api = api_map.get(dep['target'])

            if not source_api or not target_api:
                continue

            source_entity = source_api.get('entity')
            target_entity = target_api.get('entity')

            # 只保留跨实体的关系
            if source_entity and target_entity and source_entity != target_entity:
                key = (source_entity, target_entity)
                if key not in seen:
                    seen.add(key)
                    entity_relations.append({
                        'source': source_entity,
                        'target': target_entity,
                        'inferred_from': 'LLM_INFERENCE',
                        'confidence': dep.get('score', 0.9),
                        'example_api': dep['source']
                    })

        return entity_relations

    def _infer_entity_relations_by_fields(self, api_map: Dict[str, Dict],
                                         entity_groups: Dict[str, List[Dict]]) -> List[Dict]:
        """
        从字段引用推断实体关系（降级方案）

        逻辑：如果 purchase-order 的 API 有 supplier_id 字段，
             推断 purchase-order → supplier 关系
        """
        entity_relations = []

        # 构建实体名称变体
        entity_variations = {}
        for entity in entity_groups.keys():
            entity_variations[entity] = self._get_entity_variations(entity)

        # 分析每个实体的 API 字段
        for source_entity, apis in entity_groups.items():
            for api in apis:
                # 提取 request 字段名
                request_fields = self._extract_field_names_from_api(api, 'request')

                for field_name in request_fields:
                    # 检查是否引用其他实体
                    referenced_entity = self._extract_entity_from_field(field_name, entity_variations)

                    if referenced_entity and referenced_entity != source_entity:
                        entity_relations.append({
                            'source': source_entity,
                            'target': referenced_entity,
                            'inferred_from': 'FIELD_REFERENCE',
                            'confidence': 0.8,
                            'example_field': field_name,
                            'example_api': api['operation_id']
                        })

        return entity_relations

    def _infer_entity_relations_by_path(self, api_map: Dict[str, Dict],
                                       entity_groups: Dict[str, List[Dict]]) -> List[Dict]:
        """
        从路径层次推断实体关系

        逻辑：如果路径是 /purchase-order/{id}/supplier，
             推断 purchase-order → supplier 关系
        """
        entity_relations = []

        for source_entity, apis in entity_groups.items():
            for api in apis:
                path = api.get('path', '').lower()

                # 检查路径中是否包含其他实体名称
                for target_entity in entity_groups.keys():
                    if target_entity != source_entity:
                        target_variations = self._get_entity_variations(target_entity)
                        for variation in target_variations:
                            if variation in path:
                                entity_relations.append({
                                    'source': source_entity,
                                    'target': target_entity,
                                    'inferred_from': 'PATH_HIERARCHY',
                                    'confidence': 0.75,
                                    'example_api': api['operation_id']
                                })
                                break

        return entity_relations

    def _deduplicate_entity_relations_with_priority(self, relations: List[Dict]) -> List[Dict]:
        """
        去重实体关系，保留优先级最高的

        优先级：LLM_INFERENCE > FIELD_REFERENCE > PATH_HIERARCHY
        """
        priority_map = {
            'LLM_INFERENCE': 3,
            'FIELD_REFERENCE': 2,
            'PATH_HIERARCHY': 1
        }

        relation_map = {}

        for rel in relations:
            key = (rel['source'], rel['target'])
            inferred_from = rel['inferred_from']
            priority = priority_map.get(inferred_from, 0)

            if key not in relation_map:
                relation_map[key] = rel
            else:
                # 保留优先级更高的
                existing_priority = priority_map.get(relation_map[key]['inferred_from'], 0)
                if priority > existing_priority:
                    relation_map[key] = rel

        return list(relation_map.values())

    def _infer_api_dependencies_with_filter(self, session, api_map: Dict[str, Dict],
                                           entity_relations: List[Dict]) -> List[Dict]:
        """
        使用实体关系作为过滤器，推断 API 依赖（L3 层 - 肌肉）

        多层推断策略：
        1. FieldMatcher（精确字段匹配）
        2. LLM 语义推断（处理字段命名不规范的情况）
        3. CRUD Flow（同实体内的操作依赖，如 update → get）
        """
        dependencies = []

        # 构建实体关系索引：entity -> [related_entities]
        entity_relation_map = defaultdict(set)
        for rel in entity_relations:
            entity_relation_map[rel['source']].add(rel['target'])

        # 按实体分组 API
        entity_api_map = defaultdict(list)
        for op_id, api in api_map.items():
            entity = api.get('entity')
            if entity and entity != 'unknown':
                entity_api_map[entity].append((op_id, api))

        # 策略1: FieldMatcher（精确匹配）
        print("  [API Inference] Strategy 1: Field matching...")
        field_deps = self._infer_api_deps_by_field_match(
            entity_api_map, entity_relation_map, api_map
        )
        dependencies.extend(field_deps)
        print(f"    Found {len(field_deps)} dependencies by field matching")

        # 策略2: LLM 语义推断（补充，处理命名不规范的情况）
        if self.llm_inferrer and not self.llm_inferrer.llm_failed:
            print("  [API Inference] Strategy 2: LLM semantic inference...")
            llm_deps = self._infer_api_deps_by_llm_semantic(
                entity_api_map, entity_relation_map, api_map, dependencies
            )
            dependencies.extend(llm_deps)
            print(f"    Found {len(llm_deps)} additional dependencies by LLM")

        # 策略3: CRUD Flow（同实体内的操作依赖）
        print("  [API Inference] Strategy 3: CRUD flow inference...")
        crud_deps = self._infer_api_deps_by_crud_flow(entity_api_map)
        dependencies.extend(crud_deps)
        print(f"    Found {len(crud_deps)} dependencies by CRUD flow")

        # 去重（保留最高分数）
        dependencies = self._deduplicate_dependencies(dependencies)

        # 创建 API 依赖边
        for dep in dependencies:
            session.run("""
                MATCH (a:API {operation_id: $source})
                MATCH (b:API {operation_id: $target})
                MERGE (a)-[r:DEPENDS_ON]->(b)
                SET r.score = $score,
                    r.type = $type,
                    r.matched_fields = $matched_fields,
                    r.filtered_by_entity_relation = $filtered_by
            """,
                source=dep['source'],
                target=dep['target'],
                score=dep['score'],
                type=dep['type'],
                matched_fields=str(dep.get('matched_fields', [])),
                filtered_by=dep.get('filtered_by', '')
            )

        return dependencies

    def _infer_api_deps_by_field_match(self, entity_api_map: Dict,
                                      entity_relation_map: Dict,
                                      api_map: Dict) -> List[Dict]:
        """
        策略1: 使用 FieldMatcher 进行精确字段匹配
        """
        dependencies = []

        for source_entity, source_apis in entity_api_map.items():
            # 获取关联实体
            related_entities = entity_relation_map.get(source_entity, set())
            related_entities_with_self = related_entities | {source_entity}

            if related_entities:
                print(f"    [Filter] {source_entity} -> {related_entities}")

            for source_op_id, source_api in source_apis:
                request_fields = source_api.get('request_fields', [])
                if not request_fields:
                    continue

                # 只在关联实体的 API 中寻找依赖
                for target_entity in related_entities_with_self:
                    target_apis = entity_api_map.get(target_entity, [])

                    for target_op_id, target_api in target_apis:
                        if source_op_id == target_op_id:
                            continue

                        response_fields = target_api.get('response_fields', [])
                        if not response_fields:
                            continue

                        # 使用 FieldMatcher 匹配字段
                        score, matched_fields = self._match_fields(
                            request_fields, response_fields,
                            source_api, target_api
                        )

                        if score >= self.matcher.final_threshold:
                            filter_info = f"{source_entity}->{target_entity}" if source_entity != target_entity else f"{source_entity}(self)"

                            dependencies.append({
                                'source': source_op_id,
                                'target': target_op_id,
                                'score': score,
                                'type': 'FIELD_MATCH',
                                'matched_fields': matched_fields,
                                'filtered_by': filter_info
                            })

        return dependencies

    def _infer_api_deps_by_llm_semantic(self, entity_api_map: Dict,
                                       entity_relation_map: Dict,
                                       api_map: Dict,
                                       existing_deps: List[Dict]) -> List[Dict]:
        """
        策略2: 使用 LLM 进行语义推断（补充字段匹配的不足）

        只对没有找到依赖的 API 进行 LLM 推断，避免重复
        """
        if not self.llm_inferrer:
            return []

        dependencies = []

        # 找出已有依赖的 API
        apis_with_deps = set()
        for dep in existing_deps:
            apis_with_deps.add(dep['source'])

        # 对没有依赖的写操作 API 进行 LLM 推断
        for source_entity, source_apis in entity_api_map.items():
            related_entities = entity_relation_map.get(source_entity, set())
            related_entities_with_self = related_entities | {source_entity}

            for source_op_id, source_api in source_apis:
                # 跳过已有依赖的 API
                if source_op_id in apis_with_deps:
                    continue

                # 只对写操作进行推断
                if not self._is_write_operation(source_api):
                    continue

                # 构建候选目标 API
                candidate_targets = []
                for target_entity in related_entities_with_self:
                    target_apis = entity_api_map.get(target_entity, [])
                    for target_op_id, target_api in target_apis:
                        if source_op_id != target_op_id and self._is_read_operation(target_api):
                            candidate_targets.append((target_op_id, target_api, target_entity))

                # 使用 LLM 推断（简化版，直接基于操作类型和实体关系）
                for target_op_id, target_api, target_entity in candidate_targets:
                    # 简单的启发式：如果有实体关系，且是写→读，给一个中等置信度
                    if target_entity in related_entities:
                        filter_info = f"{source_entity}->{target_entity}"
                        dependencies.append({
                            'source': source_op_id,
                            'target': target_op_id,
                            'score': 0.6,  # 中等置信度
                            'type': 'LLM_SEMANTIC',
                            'matched_fields': [],
                            'filtered_by': filter_info
                        })

        return dependencies

    def _infer_api_deps_by_crud_flow(self, entity_api_map: Dict) -> List[Dict]:
        """
        策略3: CRUD Flow 推断（同实体内的操作依赖）

        逻辑：
        - UPDATE 操作 → 依赖 GET 操作（需要先获取数据）
        - DELETE 操作 → 依赖 GET 操作（需要验证）
        """
        dependencies = []

        for entity, apis in entity_api_map.items():
            # 找出读操作和写操作
            read_ops = []
            write_ops = []

            for op_id, api in apis:
                if self._is_read_operation(api):
                    read_ops.append((op_id, api))
                elif self._is_write_operation(api):
                    write_ops.append((op_id, api))

            # 为每个写操作找到对应的读操作
            for write_op_id, write_api in write_ops:
                write_type = self._get_operation_type(write_api)

                # UPDATE 和 DELETE 依赖 GET
                if write_type in ['update', 'delete']:
                    for read_op_id, read_api in read_ops:
                        read_type = self._get_operation_type(read_api)

                        # 优先匹配 get 操作
                        if read_type == 'get':
                            dependencies.append({
                                'source': write_op_id,
                                'target': read_op_id,
                                'score': 0.85,
                                'type': 'CRUD_FLOW',
                                'matched_fields': [],
                                'filtered_by': f"{entity}(self)"
                            })
                            break  # 只添加一个依赖

        return dependencies

    def _is_write_operation(self, api: Dict) -> bool:
        """检查是否为写操作"""
        method = api.get('method', '').upper()
        path = api.get('path', '').lower()
        return (method in ['POST', 'PUT', 'PATCH'] or
                '/create' in path or '/update' in path)

    def _is_read_operation(self, api: Dict) -> bool:
        """检查是否为读操作"""
        method = api.get('method', '').upper()
        path = api.get('path', '').lower()
        return (method == 'GET' or
                '/get' in path or '/list' in path or '/page' in path)

    def _match_fields(self, request_fields: List, response_fields: List,
                     source_api: Dict, target_api: Dict) -> tuple:
        """使用 FieldMatcher 匹配字段"""
        best_score = 0.0
        matched_fields = []

        same_cluster = source_api.get('capability') == target_api.get('capability')

        for req_field in request_fields:
            for resp_field in response_fields:
                score = self.matcher.calculate_score(
                    resp_field, req_field, same_cluster,
                    source_api.get('summary', ''),
                    target_api.get('summary', '')
                )

                if score > best_score:
                    best_score = score

                if score >= self.matcher.final_threshold:
                    matched_fields.append({
                        'source': resp_field.get('path', resp_field.get('name')),
                        'target': req_field.get('path', req_field.get('name')),
                        'score': score
                    })

        return best_score, matched_fields

    def _annotate_api_roles(self, session):
        """
        基于跨实体依赖标注 API 角色

        Producer: 被其他实体的 API 依赖
        Consumer: 依赖其他实体的 API
        Bridge: 既是 Producer 又是 Consumer
        Internal: 只在实体内部使用
        """
        # 统计每个 API 的跨实体依赖
        result = session.run("""
            MATCH (a:API)-[:BELONGS_TO]->(e:Entity)
            OPTIONAL MATCH (a)-[r1:DEPENDS_ON]->(other:API)-[:BELONGS_TO]->(e2:Entity)
            WHERE e.name <> e2.name
            OPTIONAL MATCH (other2:API)-[r2:DEPENDS_ON]->(a)
            OPTIONAL MATCH (other2)-[:BELONGS_TO]->(e3:Entity)
            WHERE e.name <> e3.name
            RETURN a.operation_id as op_id,
                   count(DISTINCT r1) as outgoing,
                   count(DISTINCT r2) as incoming
        """)

        for record in result:
            op_id = record['op_id']
            outgoing = record['outgoing'] or 0
            incoming = record['incoming'] or 0

            # 确定角色
            if incoming > 0 and outgoing == 0:
                role = 'PRODUCER'
            elif outgoing > 0 and incoming == 0:
                role = 'CONSUMER'
            elif incoming > 0 and outgoing > 0:
                role = 'BRIDGE'
            else:
                role = 'INTERNAL'

            # 更新 API 节点
            session.run("""
                MATCH (a:API {operation_id: $op_id})
                SET a.role = $role,
                    a.incoming_cross_entity = $incoming,
                    a.outgoing_cross_entity = $outgoing
            """,
                op_id=op_id,
                role=role,
                incoming=incoming,
                outgoing=outgoing
            )


    # ========== 辅助方法 ==========

    def _get_entity_variations(self, entity: str) -> Set[str]:
        """生成实体名称变体（用于匹配）"""
        variations = {entity}

        # 移除分隔符
        variations.add(entity.replace('-', '').replace('_', ''))

        # 分割
        parts = re.split(r'[-_]', entity)
        variations.update(parts)

        # 单复数
        if entity.endswith('s'):
            variations.add(entity[:-1])
        else:
            variations.add(entity + 's')

        return variations

    def _extract_entity_from_field(self, field_name: str, entity_variations: Dict) -> Optional[str]:
        """从字段名提取实体引用（如 user_id -> user）"""
        field_lower = field_name.lower()

        # 移除常见后缀
        for suffix in ['_id', 'id', '_key', 'key', '_code', 'code']:
            if field_lower.endswith(suffix):
                field_base = field_lower[:-len(suffix)]

                # 检查是否匹配任何实体
                for entity, variations in entity_variations.items():
                    if field_base in variations:
                        return entity

        return None

    def _extract_field_names_from_api(self, api: Dict, schema_type: str = 'request') -> Set[str]:
        """从 API 提取字段名"""
        fields = set()

        if schema_type == 'request':
            # 使用统一的提取方法
            request_fields = api.get('request_fields', [])
            if isinstance(request_fields, list):
                for field in request_fields:
                    if isinstance(field, dict):
                        name = field.get('name') or field.get('path', '')
                        if name:
                            # 提取最后一部分作为字段名（处理嵌套路径）
                            field_name = name.split('.')[-1] if '.' in name else name
                            fields.add(field_name.lower())
        else:
            # 使用统一的提取方法
            response_fields = api.get('response_fields', [])
            if isinstance(response_fields, list):
                for field in response_fields:
                    if isinstance(field, dict):
                        name = field.get('name') or field.get('path', '')
                        if name:
                            # 提取最后一部分作为字段名（处理嵌套路径）
                            field_name = name.split('.')[-1] if '.' in name else name
                            fields.add(field_name.lower())

        return fields

    def _get_schema_fields(self, schema: Dict, depth: int = 0) -> Set[str]:
        """递归提取 schema 字段名"""
        if depth > 2 or not schema:
            return set()

        fields = set()

        # 获取 properties
        properties = schema.get('properties', {})
        for field_name in properties.keys():
            fields.add(field_name.lower())

        # 处理数组
        if schema.get('type') == 'array':
            items = schema.get('items', {})
            fields.update(self._get_schema_fields(items, depth + 1))

        return fields

    def _get_operation_type(self, api: Dict) -> str:
        """提取操作类型"""
        path = api.get('path', '').lower()
        method = api.get('method', '').upper()

        if '/create' in path or method == 'POST':
            return 'create'
        elif '/update' in path or method in ['PUT', 'PATCH']:
            return 'update'
        elif '/delete' in path or method == 'DELETE':
            return 'delete'
        elif '/page' in path:
            return 'page'
        elif '/list' in path:
            return 'list'
        elif '/get' in path or '/{id}' in path or method == 'GET':
            return 'get'
        return 'other'

    def _deduplicate_entity_relations(self, relations: List[Dict]) -> List[Dict]:
        """去重实体关系"""
        seen = set()
        unique = []

        for rel in relations:
            key = (rel['source'], rel['target'])
            if key not in seen:
                seen.add(key)
                unique.append(rel)

        return unique

    def _deduplicate_dependencies(self, dependencies: List[Dict]) -> List[Dict]:
        """去重 API 依赖，保留最高分数"""
        dep_map = {}

        for dep in dependencies:
            key = (dep['source'], dep['target'])

            if key not in dep_map:
                dep_map[key] = dep
            else:
                # 保留分数更高的
                if dep['score'] > dep_map[key]['score']:
                    dep_map[key] = dep

        return list(dep_map.values())

    def close(self):
        """Close database connection."""
        self.driver.close()

    # ========== 字段提取方法 ==========

    def _extract_request_fields(self, api: Dict) -> List[Dict]:
        """
        从 API 提取请求字段

        支持多种数据格式：
        1. request_fields (直接字段列表)
        2. request_schema (schema 对象)
        3. parameters (包含 body, query, path, header)
        """
        fields = []

        # 方式1: 直接的 request_fields
        if 'request_fields' in api:
            return api['request_fields']

        # 方式2: request_schema
        if 'request_schema' in api:
            schema = api['request_schema']
            if schema:
                fields.extend(self.path_extractor.flatten_schema(schema))

        # 方式3: parameters (body, query, path)
        if 'parameters' in api:
            params = api['parameters']
            if isinstance(params, dict):
                # Body parameters
                for param in params.get('body', []):
                    fields.append({
                        'name': param.get('name', ''),
                        'type': param.get('type', 'string'),
                        'path': param.get('name', ''),
                        'required': param.get('required', False)
                    })

                # Query parameters
                for param in params.get('query', []):
                    fields.append({
                        'name': param.get('name', ''),
                        'type': param.get('type', 'string'),
                        'path': param.get('name', ''),
                        'required': param.get('required', False)
                    })

                # Path parameters
                for param in params.get('path', []):
                    fields.append({
                        'name': param.get('name', ''),
                        'type': param.get('type', 'string'),
                        'path': param.get('name', ''),
                        'required': param.get('required', True)  # Path params usually required
                    })

        return fields

    def _extract_response_fields(self, api: Dict) -> List[Dict]:
        """
        从 API 提取响应字段

        支持多种数据格式：
        1. response_fields (直接字段列表)
        2. response_schema (单个 schema)
        3. response_schemas (多个状态码的 schemas)
        """
        fields = []

        # 方式1: 直接的 response_fields
        if 'response_fields' in api:
            return api['response_fields']

        # 方式2: response_schema (单个)
        if 'response_schema' in api:
            schema = api['response_schema']
            if schema:
                fields.extend(self.path_extractor.flatten_schema(schema))

        # 方式3: response_schemas (多个状态码)
        if 'response_schemas' in api:
            schemas = api['response_schemas']
            if isinstance(schemas, dict):
                # 优先使用 2xx 状态码的响应
                for status_code in ['200', '201', '204']:
                    if status_code in schemas:
                        schema = schemas[status_code]
                        if schema:
                            fields.extend(self.path_extractor.flatten_schema(schema))
                        break
                else:
                    # 如果没有找到 2xx，使用第一个
                    for schema in schemas.values():
                        if schema:
                            fields.extend(self.path_extractor.flatten_schema(schema))
                            break

        return fields

    # ========== 辅助方法 ==========

    def _get_entity_variations(self, entity: str) -> Set[str]:
        """生成实体名称变体（用于匹配）"""
        variations = {entity}

        # 移除分隔符
        variations.add(entity.replace('-', '').replace('_', ''))

        # 分割
        parts = re.split(r'[-_]', entity)
        variations.update(parts)

        # 单复数
        if entity.endswith('s'):
            variations.add(entity[:-1])
        else:
            variations.add(entity + 's')

        return variations

    def _extract_entity_from_field(self, field_name: str, entity_variations: Dict) -> Optional[str]:
        """从字段名提取实体引用（如 user_id -> user）"""
        field_lower = field_name.lower()

        # 移除常见后缀
        for suffix in ['_id', 'id', '_key', 'key', '_code', 'code']:
            if field_lower.endswith(suffix):
                field_base = field_lower[:-len(suffix)]

                # 检查是否匹配任何实体
                for entity, variations in entity_variations.items():
                    if field_base in variations:
                        return entity

        return None

    def _extract_field_names_from_api(self, api: Dict, schema_type: str = 'request') -> Set[str]:
        """从 API 提取字段名"""
        fields = set()

        if schema_type == 'request':
            # 使用统一的提取方法
            request_fields = api.get('request_fields', [])
            if isinstance(request_fields, list):
                for field in request_fields:
                    if isinstance(field, dict):
                        name = field.get('name') or field.get('path', '')
                        if name:
                            # 提取最后一部分作为字段名（处理嵌套路径）
                            field_name = name.split('.')[-1] if '.' in name else name
                            fields.add(field_name.lower())
        else:
            # 使用统一的提取方法
            response_fields = api.get('response_fields', [])
            if isinstance(response_fields, list):
                for field in response_fields:
                    if isinstance(field, dict):
                        name = field.get('name') or field.get('path', '')
                        if name:
                            # 提取最后一部分作为字段名（处理嵌套路径）
                            field_name = name.split('.')[-1] if '.' in name else name
                            fields.add(field_name.lower())

        return fields

    def _get_schema_fields(self, schema: Dict, depth: int = 0) -> Set[str]:
        """递归提取 schema 字段名"""
        if depth > 2 or not schema:
            return set()

        fields = set()

        # 获取 properties
        properties = schema.get('properties', {})
        for field_name in properties.keys():
            fields.add(field_name.lower())

        # 处理数组
        if schema.get('type') == 'array':
            items = schema.get('items', {})
            fields.update(self._get_schema_fields(items, depth + 1))

        return fields

    def _get_operation_type(self, api: Dict) -> str:
        """提取操作类型"""
        path = api.get('path', '').lower()
        method = api.get('method', '').upper()

        if '/create' in path or method == 'POST':
            return 'create'
        elif '/update' in path or method in ['PUT', 'PATCH']:
            return 'update'
        elif '/delete' in path or method == 'DELETE':
            return 'delete'
        elif '/page' in path:
            return 'page'
        elif '/list' in path:
            return 'list'
        elif '/get' in path or '/{id}' in path or method == 'GET':
            return 'get'
        return 'other'

    def _deduplicate_entity_relations(self, relations: List[Dict]) -> List[Dict]:
        """去重实体关系"""
        seen = set()
        unique = []

        for rel in relations:
            key = (rel['source'], rel['target'])
            if key not in seen:
                seen.add(key)
                unique.append(rel)

        return unique

    def _deduplicate_dependencies(self, dependencies: List[Dict]) -> List[Dict]:
        """去重 API 依赖，保留最高分数"""
        dep_map = {}

        for dep in dependencies:
            key = (dep['source'], dep['target'])

            if key not in dep_map:
                dep_map[key] = dep
            else:
                # 保留分数更高的
                if dep['score'] > dep_map[key]['score']:
                    dep_map[key] = dep

        return list(dep_map.values())

    def close(self):
        """Close database connection."""
        self.driver.close()
