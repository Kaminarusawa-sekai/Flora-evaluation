"""Example usage of API Topology Service with Filter Strategy."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_normalization import NormalizationService
from api_topology import TopologyService


def example_filter_strategy():
    """演示过滤器策略：实体关系作为骨架，API 依赖作为肌肉"""
    print("=" * 80)
    print("Example: Filter Strategy (Entity as Filter)")
    print("=" * 80)

    # 1. 规范化 API
    print("\n[Step 1] Normalizing APIs with entity-centric clustering")
    norm_service = NormalizationService(use_entity_clustering=True)
    result = norm_service.normalize_swagger('erp-server.json')

    print(f"✓ Normalized {result['statistics']['total_apis']} APIs")
    print(f"✓ Identified {result['statistics']['total_capabilities']} capabilities")

    # 2. 构建拓扑图（使用过滤器策略）
    print("\n[Step 2] Building topology graph with Filter Strategy")
    print("  Architecture:")
    print("    L1 (骨架): Entity relationships - inferred from field references")
    print("    L3 (肌肉): API dependencies - filtered by entity relationships")

    service = TopologyService(
        neo4j_uri="bolt://192.168.1.210:7687",
        neo4j_user="neo4j",
        neo4j_password="12345678",
        llm_client=None,
        use_entity_inference=True
    )

    build_result = service.build_graph(result['capabilities'])

    print(f"\n✓ Build Results:")
    print(f"  APIs created: {build_result['apis_created']}")
    print(f"  Entities created: {build_result['entities_created']}")
    print(f"  Entity relationships (骨架): {build_result['entity_relationships']}")
    print(f"  API dependencies (肌肉): {build_result['api_dependencies']}")

    # 3. 查询示例
    print("\n[Step 3] Querying the graph")

    with service.builder.driver.session() as session:
        # 查询实体关系（骨架）
        print("\n  Entity Relationships (骨架):")
        result = session.run("""
            MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity)
            RETURN e1.name as source, e2.name as target,
                   r.example_field as field
            LIMIT 5
        """)

        for record in result:
            print(f"    {record['source']} -> {record['target']} (via {record['field']})")

        # 查询 API 依赖（肌肉）
        print("\n  API Dependencies (肌肉 - filtered by entity relations):")
        result = session.run("""
            MATCH (a1:API)-[r:DEPENDS_ON]->(a2:API)
            WHERE r.filtered_by_entity_relation IS NOT NULL
            RETURN a1.operation_id as source, a2.operation_id as target,
                   r.filtered_by_entity_relation as filtered_by,
                   r.score as score
            LIMIT 5
        """)

        for record in result:
            print(f"    {record['source']} -> {record['target']}")
            print(f"      Filtered by: {record['filtered_by']} (score: {record['score']:.2f})")

        # 查询 API 角色
        print("\n  API Roles:")
        result = session.run("""
            MATCH (a:API)
            WHERE a.role IS NOT NULL
            RETURN a.role as role, count(*) as count
            ORDER BY count DESC
        """)

        for record in result:
            print(f"    {record['role']}: {record['count']} APIs")

    service.close()
    print("\n✓ Filter strategy example completed!")


def example_query_workflow():
    """演示 Agent 查询工作流"""
    print("\n" + "=" * 80)
    print("Example: Agent Query Workflow")
    print("=" * 80)

    print("\nScenario: Agent needs to cancel an order")
    print("\nWorkflow:")
    print("  1. Find the entity: 'order'")
    print("  2. Check entity relationships (骨架):")
    print("     Order -> Order (self)")
    print("     Order -> User")
    print("     Order -> Product")
    print("  3. Find Consumer APIs in Order entity:")
    print("     cancelOrder (needs order_id)")
    print("  4. Find Producer APIs in related entities:")
    print("     getOrder (provides order_id)")
    print("  5. Execute:")
    print("     a. Call getOrder to get order_id")
    print("     b. Call cancelOrder with order_id")

    print("\nCypher Query Example:")
    print("""
    // Step 1: Find entity relationships
    MATCH (e:Entity {name: 'order'})-[r:RELATES_TO]->(f:Entity)
    RETURN f.name, r.example_field

    // Step 2: Find Consumer APIs
    MATCH (a:API)-[:BELONGS_TO]->(e:Entity {name: 'order'})
    WHERE a.role = 'CONSUMER'
    RETURN a.operation_id, a.path

    // Step 3: Find Producer APIs in related entities
    MATCH (a:API)-[:BELONGS_TO]->(f:Entity)
    WHERE f.name IN ['order', 'user', 'product']
      AND a.role = 'PRODUCER'
    RETURN a.operation_id, a.entity, a.path
    """)


def example_architecture_explanation():
    """解释架构设计"""
    print("\n" + "=" * 80)
    print("Architecture Explanation: Filter Strategy")
    print("=" * 80)

    print("\n核心原则：以 API 为实，以 Entity 为虚")
    print("\n1. Entity 关系 = 骨架 (Master Logic)")
    print("   - 从字段引用推断（如 user_id -> User）")
    print("   - 定义高层业务逻辑")
    print("   - 作为 API 依赖推断的过滤器")

    print("\n2. API 依赖 = 肌肉 (Detail Filler)")
    print("   - 在骨架指导下填充")
    print("   - 只在关联实体内搜索")
    print("   - 使用 FieldMatcher 精确匹配")

    print("\n3. 过滤器工作流程:")
    print("   createOrder 需要找依赖：")
    print("     ↓")
    print("   查看 Order 的关联实体：User, Product")
    print("     ↓")
    print("   只在 User 和 Product 的 API 中搜索")
    print("     ↓")
    print("   使用 FieldMatcher 匹配字段")
    print("     ↓")
    print("   创建依赖：")
    print("     createOrder -> getUser (filtered_by: 'Order->User')")
    print("     createOrder -> getProduct (filtered_by: 'Order->Product')")

    print("\n4. 优势:")
    print("   ✓ 清晰的层次：骨架 + 肌肉")
    print("   ✓ 高效搜索：O(n×m) 而非 O(n²)")
    print("   ✓ 可控依赖：实体关系作为白名单")
    print("   ✓ 易于追溯：记录 filtered_by_entity_relation")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("API Topology Service - Filter Strategy Examples")
    print("=" * 80)

    # 运行示例
    try:
        example_filter_strategy()
    except Exception as e:
        print(f"⚠ Example failed: {e}")

    # example_query_workflow()
    # example_architecture_explanation()

    print("\n" + "=" * 80)
    print("All Examples Completed!")
    print("=" * 80)
    print("\nKey Features:")
    print("  ✓ Filter Strategy: Entity relationships as filters")
    print("  ✓ Two-layer architecture: Skeleton (Entity) + Muscle (API)")
    print("  ✓ Efficient search: Only in related entities")
    print("  ✓ Traceable dependencies: filtered_by_entity_relation")
    print("=" * 80)

    print("\n✓ LLM-enhanced inference completed!")


# def example_with_fallback():
#     """演示自动降级机制"""
#     print("\n" + "=" * 80)
#     print("Example 3: Auto-Fallback Mechanism")
#     print("=" * 80)

#     # 创建会失败的 LLM 客户端
#     class FailingLLMClient:
#         def __call__(self, prompt: str) -> str:
#             raise Exception("LLM API unavailable")

#     print("\n[Step 1] Normalizing APIs")
#     norm_service = NormalizationService(use_entity_clustering=True)
#     result = norm_service.normalize_swagger('../erp-server.json')
#     print(f"✓ Normalized {result['statistics']['total_apis']} APIs")

#     # 2. 构建拓扑图（LLM 会失败，自动降级）
#     print("\n[Step 2] Building graph with failing LLM (will auto-fallback)")
#     service = TopologyService(
#         neo4j_uri="bolt://192.168.1.210:7687",
#         neo4j_user="neo4j",
#         neo4j_password="12345678",
#         llm_client=FailingLLMClient(),  # 会失败的 LLM
#         use_entity_inference=True
#     )

#     build_result = service.build_graph(result['capabilities'])
#     print(f"\n✓ Created {build_result['apis_created']} API nodes")
#     print(f"✓ Inferred {build_result['inferred_dependencies']} dependencies (via fallback)")
#     print(f"  - Field-based: {build_result.get('field_based_dependencies', 0)}")
#     print(f"  - Entity-based: {build_result.get('entity_based_dependencies', 0)}")

#     service.close()
#     print("\n✓ Auto-fallback mechanism works!")


# def example_inference_priority():
#     """演示推断优先级"""
#     print("\n" + "=" * 80)
#     print("Example 4: Inference Priority Demonstration")
#     print("=" * 80)

#     print("\nInference Priority (High to Low):")
#     print("  1. LLM Inference       - Most intelligent (if available)")
#     print("  2. Schema Reference    - High accuracy (field references)")
#     print("  3. CRUD Flow           - High accuracy (operation patterns)")
#     print("  4. Path Hierarchy      - Medium accuracy (URL structure)")

#     print("\nWhen LLM is available:")
#     print("  ✓ LLM analyzes entity relationships semantically")
#     print("  ✓ Other methods complement LLM results")
#     print("  ✓ Duplicates are removed (keeping highest score)")

#     print("\nWhen LLM fails or unavailable:")
#     print("  ✓ Auto-fallback to traditional methods")
#     print("  ✓ Schema Reference detects field references (e.g., customerId)")
#     print("  ✓ CRUD Flow infers operation dependencies")
#     print("  ✓ Path Hierarchy analyzes URL structure")


# def example_configuration():
#     """演示配置选项"""
#     print("\n" + "=" * 80)
#     print("Example 5: Configuration Options")
#     print("=" * 80)

#     print("\n[Option 1] Basic configuration (no LLM)")
#     print("""
#     service = TopologyService(
#         neo4j_uri="bolt://localhost:7687",
#         neo4j_user="neo4j",
#         neo4j_password="password",
#         llm_client=None,              # No LLM
#         use_entity_inference=True     # Enable entity inference
#     )
#     """)

#     print("\n[Option 2] With LLM (auto-fallback enabled)")
#     print("""
#     from openai import OpenAI

#     # OpenAI
#     llm_client = OpenAI(api_key="sk-...")

#     # Qwen (通义千问)
#     llm_client = OpenAI(
#         api_key="sk-...",
#         base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
#     )

#     # DeepSeek
#     llm_client = OpenAI(
#         api_key="sk-...",
#         base_url="https://api.deepseek.com"
#     )

#     service = TopologyService(
#         neo4j_uri="bolt://localhost:7687",
#         neo4j_user="neo4j",
#         neo4j_password="password",
#         llm_client=llm_client,  # Enable LLM
#         use_entity_inference=True
#     )
#     # Auto-fallback is enabled by default
#     """)

#     print("\n[Option 3] Disable entity inference (field-based only)")
#     print("""
#     service = TopologyService(
#         neo4j_uri="bolt://localhost:7687",
#         neo4j_user="neo4j",
#         neo4j_password="password",
#         llm_client=None,
#         use_entity_inference=False    # Only field matching
#     )
#     """)

#     print("\n[Option 4] Custom confidence threshold")
#     print("""
#     from api_topology.dynamic_entity_inferrer import DynamicEntityInferrer

#     inferrer = DynamicEntityInferrer(
#         min_confidence=0.7,           # Higher threshold
#         llm_client=llm_client,
#         enable_llm_fallback=True
#     )
#     """)


# if __name__ == "__main__":
#     print("\n" + "=" * 80)
#     print("API Topology Service - Complete Examples")
#     print("=" * 80)

#     # 运行示例
#     # try:
#     #     example_basic_usage()
#     # except Exception as e:
#     #     print(f"⚠ Example 1 failed: {e}")

#     try:
#         example_filter_strategy()
#     except Exception as e:
#         print(f"⚠ Example 2 failed: {e}")

#     # try:
#     #     example_with_fallback()
#     # except Exception as e:
#     #     print(f"⚠ Example 3 failed: {e}")

#     # example_inference_priority()
#     # example_configuration()

#     print("\n" + "=" * 80)
#     print("All Examples Completed!")
#     print("=" * 80)
#     print("\nKey Features:")
#     print("  ✓ LLM intelligent inference (highest priority)")
#     print("  ✓ Auto-fallback mechanism (when LLM fails)")
#     print("  ✓ Multi-level inference (4 methods)")
#     print("  ✓ Flexible configuration")
#     print("  ✓ Robust error handling")
#     print("=" * 80)

