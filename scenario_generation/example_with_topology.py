"""Example: Generate test scenarios from API topology."""
import sys
import os
import json

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scenario_generation.scenario_generation_service import ScenarioGenerationService
from scenario_generation.path_generator import PathGenerator


def example_with_real_topology():
    """演示从真实拓扑数据生成测试场景"""
    print("=" * 80)
    print("Example: Generate Test Scenarios from Real API Topology")
    print("=" * 80)

    # 检查依赖
    missing_modules = []

    try:
        import neo4j
    except ImportError:
        missing_modules.append('neo4j')

    try:
        from api_normalization import NormalizationService
        from api_topology import TopologyService
    except ImportError as e:
        print(f"\n[ERROR] Failed to import required modules: {e}")
        print("Please ensure api_normalization and api_topology are available.")
        missing_modules.append('api_normalization/api_topology')

    if missing_modules:
        print(f"\n[ERROR] Missing required modules: {', '.join(missing_modules)}")
        print("\nTo install missing dependencies:")
        print("  pip install neo4j")
        print("\nOr use conda:")
        print("  conda install -c conda-forge neo4j-python-driver")
        return

    # Step 1: 规范化 API
    print("\n[Step 1] Normalizing APIs with entity-centric clustering")
    norm_service = NormalizationService(use_entity_clustering=True)

    # 使用 erp-server.json（需要在项目根目录）
    swagger_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'erp-server.json')

    if not os.path.exists(swagger_file):
        print(f"\n[ERROR] Swagger file not found: {swagger_file}")
        print("Please ensure erp-server.json exists in the project root directory.")
        return

    norm_result = norm_service.normalize_swagger(swagger_file)

    print(f"  [OK] Normalized {norm_result['statistics']['total_apis']} APIs")
    print(f"  [OK] Identified {norm_result['statistics']['total_capabilities']} capabilities")

    # Step 2: 构建拓扑图
    print("\n[Step 2] Building topology graph with Filter Strategy")
    print("  Architecture:")
    print("    L1 (骨架): Entity relationships - inferred from field references")
    print("    L3 (肌肉): API dependencies - filtered by entity relationships")

    # 配置 Neo4j 连接（根据实际情况修改）
    topology_service = TopologyService(
        neo4j_uri="bolt://192.168.1.210:7687",
        neo4j_user="neo4j",
        neo4j_password="12345678",
        llm_client=None,
        use_entity_inference=True
    )

    try:
        build_result = topology_service.build_graph(norm_result['capabilities'])

        print(f"\n  [OK] Build Results:")
        print(f"    APIs created: {build_result['apis_created']}")
        print(f"    Entities created: {build_result['entities_created']}")
        print(f"    Entity relationships: {build_result['entity_relationships']}")
        print(f"    API dependencies: {build_result['api_dependencies']}")

        # Step 3: 从 Neo4j 提取拓扑数据
        print("\n[Step 3] Extracting topology data from Neo4j")

        with topology_service.builder.driver.session() as session:
            # 获取 APIs
            apis_result = session.run("""
                MATCH (a:API)
                RETURN a.operation_id as operation_id,
                       a.method as method,
                       a.path as path,
                       a.summary as summary,
                       a.parameters as parameters,
                       a.responses as responses,
                       a.entity as entity,
                       a.role as role
            """)
            apis = []
            for record in apis_result:
                api_data = dict(record)
                # 解析 parameters 和 responses（可能是字符串）
                if isinstance(api_data.get('parameters'), str):
                    try:
                        import ast
                        api_data['parameters'] = ast.literal_eval(api_data['parameters'])
                    except:
                        pass
                if isinstance(api_data.get('responses'), str):
                    try:
                        import ast
                        api_data['responses'] = ast.literal_eval(api_data['responses'])
                    except:
                        pass
                apis.append(api_data)

            # 获取依赖关系
            deps_result = session.run("""
                MATCH (a1:API)-[r:DEPENDS_ON]->(a2:API)
                RETURN a1.operation_id as from,
                       a2.operation_id as to,
                       r.score as score,
                       r.filtered_by_entity_relation as filtered_by
            """)
            dependencies = [dict(record) for record in deps_result]

            # 获取实体
            entities_result = session.run("""
                MATCH (e:Entity)
                OPTIONAL MATCH (a:API)-[:BELONGS_TO]->(e)
                RETURN e.name as name,
                       collect(a.operation_id) as apis
            """)
            entities = [dict(record) for record in entities_result]

        topology_data = {
            'apis': apis,
            'dependencies': dependencies,
            'entities': entities
        }

        print(f"  [OK] Extracted {len(apis)} APIs")
        print(f"  [OK] Extracted {len(dependencies)} dependencies")
        print(f"  [OK] Extracted {len(entities)} entities")

        # Step 4: 从拓扑中发现路径并生成测试主题
        print("\n[Step 4] Discovering paths from topology and generating themes")
        print("  核心逻辑：对着答案编题目")
        print("    1. 从拓扑中发现可能的 API 路径")
        print("    2. 为路径生成测试主题")

        path_generator = PathGenerator(llm_client=None)  # 可以配置 LLM

        paths = path_generator.generate_paths(
            topology_data=topology_data,
            max_paths=10,
            max_path_length=6,
            min_path_length=2
        )

        print(f"\n  [OK] Discovered {len(paths)} paths with generated themes:")
        for i, path_info in enumerate(paths[:5], 1):
            print(f"\n    Path {i}: {' -> '.join(path_info['path'])}")
            print(f"      Test Objective: {path_info['test_objective']}")
            print(f"      Description: {path_info['description'][:80]}...")

        # Step 5: 为每条路径生成测试场景
        print("\n[Step 5] Generating test scenarios for each path")
        scenario_service = ScenarioGenerationService()

        all_scenarios = []

        for i, path_info in enumerate(paths, 1):
            print(f"\n  Generating scenarios for Path {i}...")

            # 构建 api_details
            api_details = {api['operation_id']: api for api in topology_data['apis']}

            # 生成场景
            scenarios = scenario_service.generate_scenarios(
                api_path=path_info['path'],
                api_details=api_details,
                parameter_flow=path_info.get('parameter_flow', {}),
                scenario_types=['normal', 'exception'],
                count_per_type=1
            )

            all_scenarios.extend(scenarios)

            print(f"    [OK] Generated {len(scenarios)} scenarios")

        # Step 6: 输出结果摘要
        print("\n[Step 6] Test Scenario Summary")
        print("=" * 80)

        for i, result in enumerate(all_scenarios[:10], 1):
            scenario = result['scenario']
            validation = result['validation']

            print(f"\n=== Scenario {i} ===")
            print(f"Path: {' -> '.join(result['api_path'])}")
            print(f"Type: {scenario['scenario_type']}")
            print(f"Title: {scenario['title']}")
            print(f"Valid: {validation['is_valid']}")
            print(f"Score: {validation['score']:.2f}")

            if validation['warnings']:
                print(f"Warnings: {len(validation['warnings'])}")

        if len(all_scenarios) > 10:
            print(f"\n... and {len(all_scenarios) - 10} more scenarios")

        # Step 7: 保存结果
        output_file = 'output/real_topology_scenarios.json'
        os.makedirs('output', exist_ok=True)

        output_data = {
            'metadata': {
                'source_file': swagger_file,
                'total_apis': len(apis),
                'total_dependencies': len(dependencies),
                'total_entities': len(entities)
            },
            'topology_summary': {
                'total_apis': len(apis),
                'total_dependencies': len(dependencies),
                'total_entities': len(entities)
            },
            'paths': paths,
            'scenarios': [
                {
                    'api_path': result['api_path'],
                    'scenario': result['scenario'],
                    'validation': result['validation']
                }
                for result in all_scenarios
            ],
            'statistics': {
                'total_paths': len(paths),
                'total_scenarios': len(all_scenarios),
                'valid_scenarios': sum(1 for r in all_scenarios if r['validation']['is_valid']),
                'average_score': sum(r['validation']['score'] for r in all_scenarios) / len(all_scenarios) if all_scenarios else 0
            }
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"\n[OK] Results saved to {output_file}")

        print("\n" + "=" * 80)
        print("Statistics:")
        print(f"  Total APIs: {len(apis)}")
        print(f"  Total Dependencies: {len(dependencies)}")
        print(f"  Total Entities: {len(entities)}")
        print(f"  Total Paths: {len(paths)}")
        print(f"  Total Scenarios: {len(all_scenarios)}")
        print(f"  Valid Scenarios: {output_data['statistics']['valid_scenarios']}")
        print(f"  Average Score: {output_data['statistics']['average_score']:.2f}")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] Failed to build topology or generate scenarios: {e}")
        import traceback
        traceback.print_exc()
    finally:
        topology_service.close()


def example_with_topology_data():
    """演示从拓扑数据生成测试场景"""
    print("=" * 80)
    print("Example: Generate Test Scenarios from API Topology")
    print("=" * 80)

    # 模拟从 api_topology 获取的数据
    # 实际使用时，这些数据来自 TopologyService.build_graph() 的结果
    topology_data = {
        'apis': [
            {
                'operation_id': 'login',
                'method': 'POST',
                'path': '/api/auth/login',
                'summary': '用户登录',
                'parameters': ['username', 'password'],
                'responses': {'user_id': 'string', 'token': 'string'}
            },
            {
                'operation_id': 'list_orders',
                'method': 'GET',
                'path': '/api/orders',
                'summary': '查询订单列表',
                'parameters': ['user_id', 'token'],
                'responses': {'orders': [{'id': 'string', 'status': 'string'}]}
            },
            {
                'operation_id': 'get_order_detail',
                'method': 'GET',
                'path': '/api/orders/{order_id}',
                'summary': '获取订单详情',
                'parameters': ['order_id', 'token'],
                'responses': {'order': {'id': 'string', 'status': 'string', 'amount': 'number'}}
            },
            {
                'operation_id': 'cancel_order',
                'method': 'POST',
                'path': '/api/orders/{order_id}/cancel',
                'summary': '取消订单',
                'parameters': ['order_id', 'reason', 'token'],
                'responses': {'success': 'boolean'}
            }
        ],
        'dependencies': [
            {'from': 'list_orders', 'to': 'login', 'score': 0.9},
            {'from': 'get_order_detail', 'to': 'list_orders', 'score': 0.8},
            {'from': 'get_order_detail', 'to': 'login', 'score': 0.85},
            {'from': 'cancel_order', 'to': 'get_order_detail', 'score': 0.85},
            {'from': 'cancel_order', 'to': 'login', 'score': 0.9}
        ],
        'entities': [
            {'name': 'User', 'apis': ['login']},
            {'name': 'Order', 'apis': ['list_orders', 'get_order_detail', 'cancel_order']}
        ]
    }

    # Step 1: 从拓扑中发现路径并生成测试主题
    print("\n[Step 1] Discovering paths from topology and generating themes")
    print("  核心逻辑：")
    print("    1. 从拓扑中发现可能的 API 路径（基于实体和依赖关系）")
    print("    2. 为每条路径生成测试主题（根据路径功能起名）")
    print("    3. 这是'对着答案编题目'的过程")

    path_generator = PathGenerator(llm_client=None)  # 使用启发式方法

    # 注意：不再传入 test_objectives，而是让系统自己发现路径并生成主题
    paths = path_generator.generate_paths(
        topology_data=topology_data,
        max_paths=5,
        max_path_length=4,
        min_path_length=2
    )

    print(f"\n[OK] Discovered {len(paths)} paths with generated themes:")
    for i, path_info in enumerate(paths, 1):
        print(f"\n  Path {i}: {' -> '.join(path_info['path'])}")
        print(f"    Test Objective: {path_info['test_objective']}")
        print(f"    Description: {path_info['description']}")
        print(f"    Type: {path_info['scenario_type']}")

    # Step 2: 为每条路径生成测试场景
    print("\n[Step 2] Generating test scenarios for each path")
    scenario_service = ScenarioGenerationService()

    all_scenarios = []

    for i, path_info in enumerate(paths, 1):
        print(f"\n  Generating scenarios for Path {i}...")

        # 构建 api_details
        api_details = {api['operation_id']: api for api in topology_data['apis']}

        # 生成场景
        scenarios = scenario_service.generate_scenarios(
            api_path=path_info['path'],
            api_details=api_details,
            parameter_flow=path_info.get('parameter_flow', {}),
            scenario_types=['normal', 'exception'],
            count_per_type=1
        )

        all_scenarios.extend(scenarios)

        print(f"    [OK] Generated {len(scenarios)} scenarios")

    # Step 3: 输出结果
    print("\n[Step 3] Test Scenario Summary")
    print("=" * 80)

    for i, result in enumerate(all_scenarios, 1):
        scenario = result['scenario']
        validation = result['validation']

        print(f"\n=== Scenario {i} ===")
        print(f"Path: {' -> '.join(result['api_path'])}")
        print(f"Type: {scenario['scenario_type']}")
        print(f"Title: {scenario['title']}")
        print(f"Description: {scenario.get('description', 'N/A')[:100]}...")
        print(f"Valid: {validation['is_valid']}")
        print(f"Score: {validation['score']:.2f}")

        if validation['warnings']:
            print(f"Warnings: {len(validation['warnings'])}")
            for warning in validation['warnings'][:2]:
                print(f"  - {warning}")

        if validation['issues']:
            print(f"Issues: {validation['issues']}")

    # Step 4: 保存结果
    output_file = 'output/generated_scenarios.json'
    os.makedirs('output', exist_ok=True)

    output_data = {
        'topology_summary': {
            'total_apis': len(topology_data['apis']),
            'total_dependencies': len(topology_data['dependencies']),
            'total_entities': len(topology_data['entities'])
        },
        'paths': paths,
        'scenarios': [
            {
                'api_path': result['api_path'],
                'scenario': result['scenario'],
                'validation': result['validation']
            }
            for result in all_scenarios
        ],
        'statistics': {
            'total_paths': len(paths),
            'total_scenarios': len(all_scenarios),
            'valid_scenarios': sum(1 for r in all_scenarios if r['validation']['is_valid']),
            'average_score': sum(r['validation']['score'] for r in all_scenarios) / len(all_scenarios) if all_scenarios else 0
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Results saved to {output_file}")

    print("\n" + "=" * 80)
    print("Statistics:")
    print(f"  Total Paths: {output_data['statistics']['total_paths']}")
    print(f"  Total Scenarios: {output_data['statistics']['total_scenarios']}")
    print(f"  Valid Scenarios: {output_data['statistics']['valid_scenarios']}")
    print(f"  Average Score: {output_data['statistics']['average_score']:.2f}")
    print("=" * 80)


def example_with_llm():
    """演示使用 LLM 生成路径主题（需要配置 LLM）"""
    print("\n" + "=" * 80)
    print("Example: Generate Path Themes with LLM (Optional)")
    print("=" * 80)

    print("\nTo use LLM for intelligent theme generation:")
    print("""
    from openai import OpenAI

    # Configure LLM client
    llm_client = OpenAI(
        api_key="your-api-key",
        base_url="https://api.openai.com/v1"  # or other compatible endpoint
    )

    # Create path generator with LLM
    path_generator = PathGenerator(llm_client=llm_client)

    # Generate paths (LLM will create themes)
    paths = path_generator.generate_paths(
        topology_data=topology_data,
        max_paths=10,
        max_path_length=6,
        min_path_length=2
    )
    """)

    print("\n核心逻辑（对着答案编题目）：")
    print("  1. 系统从拓扑中发现可能的 API 路径")
    print("  2. LLM 分析每条路径中的 API 功能")
    print("  3. LLM 为路径生成合适的测试主题和描述")
    print("  4. 例如：路径 [login, list_orders, cancel_order]")
    print("     -> LLM 生成主题：'测试用户取消订单流程'")
    print("     -> 描述：'验证用户登录后查询订单并成功取消'")

    print("\nLLM 的优势：")
    print("  [OK] 理解 API 的业务含义")
    print("  [OK] 生成更准确的测试主题")
    print("  [OK] 创建更详细的测试描述")
    print("  [OK] 识别路径的测试价值")
    print("  [OK] Fallback to heuristic if LLM fails")


def example_integration_with_topology_service():
    """演示与 TopologyService 的完整集成"""
    print("\n" + "=" * 80)
    print("Example: Full Integration with TopologyService")
    print("=" * 80)

    print("\n完整工作流程（对着答案编题目）:")
    print("""
    # Step 1: Normalize APIs
    from api_normalization import NormalizationService
    norm_service = NormalizationService(use_entity_clustering=True)
    norm_result = norm_service.normalize_swagger('your-swagger.json')

    # Step 2: Build topology graph
    from api_topology import TopologyService
    topology_service = TopologyService(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        llm_client=llm_client,  # Optional
        use_entity_inference=True
    )
    build_result = topology_service.build_graph(norm_result['capabilities'])

    # Step 3: Extract topology data for path generation
    # Query Neo4j to get APIs, dependencies, and entities
    with topology_service.builder.driver.session() as session:
        # Get APIs
        apis_result = session.run(\"\"\"
            MATCH (a:API)
            RETURN a.operation_id as operation_id,
                   a.method as method,
                   a.path as path,
                   a.summary as summary,
                   a.parameters as parameters,
                   a.responses as responses
        \"\"\")
        apis = [dict(record) for record in apis_result]

        # Get dependencies
        deps_result = session.run(\"\"\"
            MATCH (a1:API)-[r:DEPENDS_ON]->(a2:API)
            RETURN a1.operation_id as from,
                   a2.operation_id as to,
                   r.score as score
        \"\"\")
        dependencies = [dict(record) for record in deps_result]

        # Get entities
        entities_result = session.run(\"\"\"
            MATCH (e:Entity)
            OPTIONAL MATCH (a:API)-[:BELONGS_TO]->(e)
            RETURN e.name as name,
                   collect(a.operation_id) as apis
        \"\"\")
        entities = [dict(record) for record in entities_result]

    topology_data = {
        'apis': apis,
        'dependencies': dependencies,
        'entities': entities
    }

    # Step 4: 从拓扑中发现路径并生成测试主题
    # 核心：不是先有主题再找路径，而是先发现路径再生成主题
    from scenario_generation.path_generator import PathGenerator
    path_generator = PathGenerator(llm_client=llm_client)

    paths = path_generator.generate_paths(
        topology_data=topology_data,
        max_paths=10,
        max_path_length=6,
        min_path_length=2
    )

    # 每条路径都有 LLM 生成的测试主题：
    # {
    #   "path": ["login", "list_orders", "cancel_order"],
    #   "test_objective": "测试用户取消订单流程",  # LLM 生成
    #   "description": "验证用户登录后查询订单并成功取消",  # LLM 生成
    #   "scenario_type": "normal",
    #   "parameter_flow": {...}
    # }

    # Step 5: Generate test scenarios
    from scenario_generation import ScenarioGenerationService
    scenario_service = ScenarioGenerationService()

    all_scenarios = []
    for path_info in paths:
        api_details = {api['operation_id']: api for api in topology_data['apis']}
        scenarios = scenario_service.generate_scenarios(
            api_path=path_info['path'],
            api_details=api_details,
            parameter_flow=path_info.get('parameter_flow', {}),
            scenario_types=['normal', 'exception'],
            count_per_type=2
        )
        all_scenarios.extend(scenarios)

    # Step 6: Save results
    import json
    with open('test_scenarios.json', 'w', encoding='utf-8') as f:
        json.dump(all_scenarios, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(all_scenarios)} test scenarios!")
    """)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("API Topology to Scenario Generation - Examples")
    print("=" * 80)

    # 选择运行哪个示例
    print("\nAvailable examples:")
    print("  1. Mock topology data (quick demo)")
    print("  2. Real topology from Neo4j (requires Neo4j and erp-server.json)")
    print("  3. Show LLM usage example")
    print("  4. Show full integration workflow")

    # 默认运行模拟数据示例
    # print("\nRunning Example 1: Mock topology data...")
    # example_with_topology_data()

    # 如果需要运行真实拓扑示例，取消下面的注释
    # print("\nRunning Example 2: Real topology from Neo4j...")
    # example_with_real_topology()

    # Show additional examples
    example_with_llm()
    example_integration_with_topology_service()

    print("\n" + "=" * 80)
    print("All Examples Completed!")
    print("=" * 80)
    print("\nTo run the real topology example:")
    print("  1. Ensure Neo4j is running")
    print("  2. Ensure erp-server.json exists in project root")
    print("  3. Uncomment the example_with_real_topology() call in __main__")
    print("=" * 80)

