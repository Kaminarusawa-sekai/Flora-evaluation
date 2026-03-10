"""
完整流程示例 - 从 Swagger 到优化的完整流程
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.pipeline_orchestrator import PipelineOrchestrator
from adapters import *


def main():
    """运行完整流程示例"""

    print("=" * 70)
    print("Flora-Evaluation Pipeline - Full Example")
    print("=" * 70)

    # 设置环境变量（示例）
    os.environ.setdefault('NEO4J_URI', 'bolt://localhost:7687')
    os.environ.setdefault('NEO4J_USER', 'neo4j')
    os.environ.setdefault('NEO4J_PASSWORD', 'password')
    os.environ.setdefault('DASHSCOPE_API_KEY', 'your-api-key')
    os.environ.setdefault('DATABASE_URL', 'mysql://user:pass@localhost:3306/db')

    # 创建编排器
    config_path = 'config/pipeline_config.yaml'
    orchestrator = PipelineOrchestrator(config_path)

    # 注册所有模块
    print("\n注册模块...")
    orchestrator.register_module('normalization', NormalizationAdapter())
    orchestrator.register_module('topology', TopologyAdapter())
    orchestrator.register_module('database_mapping', EntiMapAdapter())
    orchestrator.register_module('scenario_generation', ScenarioAdapter())
    orchestrator.register_module('agent_build', AgentBuildAdapter())
    orchestrator.register_module('mock_service', MockAdapter())
    orchestrator.register_module('evaluation', EvaluationAdapter())
    orchestrator.register_module('optimization', OptimizationAdapter())

    # 运行完整流程
    print("\n开始运行流程...")
    try:
        results = orchestrator.run_pipeline()

        # 输出结果摘要
        print("\n" + "=" * 70)
        print("Pipeline Execution Summary")
        print("=" * 70)

        for stage_name, result in results.items():
            print(f"\n[{stage_name}]")
            if hasattr(result, 'metadata'):
                print(f"  Timestamp: {result.timestamp}")
                print(f"  Version: {result.metadata.get('version', 'N/A')}")

            # 输出关键指标
            if stage_name == 'normalization':
                print(f"  Capabilities: {len(result.capabilities)}")
            elif stage_name == 'topology':
                print(f"  APIs: {len(result.apis)}")
                print(f"  Dependencies: {len(result.dependencies)}")
            elif stage_name == 'scenario_generation':
                print(f"  Scenarios: {len(result.scenarios)}")
            elif stage_name == 'evaluation':
                print(f"  Success Rate: {result.success_rate:.2%}")
                print(f"  Avg Execution Time: {result.average_execution_time:.2f}s")
            elif stage_name == 'optimization':
                print(f"  Suggestions: {len(result.suggestions)}")
                print(f"  Should Rebuild: {result.should_rebuild}")

        # 如果需要重新构建，触发优化循环
        if results['optimization'].should_rebuild:
            print("\n" + "=" * 70)
            print("Starting Optimization Loop")
            print("=" * 70)
            run_optimization_loop(orchestrator, results)

        print("\n" + "=" * 70)
        print("✅ Pipeline Completed Successfully!")
        print("=" * 70)

    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ Pipeline Failed!")
        print("=" * 70)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


def run_optimization_loop(orchestrator, initial_results, max_iterations=5):
    """运行优化循环"""
    iteration = 1
    previous_success_rate = initial_results['evaluation'].success_rate

    while iteration <= max_iterations:
        print(f"\n--- Optimization Iteration {iteration}/{max_iterations} ---")

        # 应用优化后的 Prompts
        optimized_prompts = initial_results['optimization'].optimized_prompts
        apply_optimized_prompts(optimized_prompts)

        # 重新运行评估和优化
        results = orchestrator.run_pipeline(
            start_stage='agent_build',
            end_stage='optimization'
        )

        # 检查改进
        current_success_rate = results['evaluation'].success_rate
        improvement = current_success_rate - previous_success_rate

        print(f"Success Rate: {previous_success_rate:.2%} -> {current_success_rate:.2%}")
        print(f"Improvement: {improvement:+.2%}")

        if not results['optimization'].should_rebuild:
            print("✅ Optimization converged!")
            break

        if improvement <= 0:
            print("⚠️  No improvement, stopping optimization")
            break

        previous_success_rate = current_success_rate
        initial_results = results
        iteration += 1


def apply_optimized_prompts(optimized_prompts: dict):
    """
    应用优化后的 Prompts 到 Neo4j
    """
    from neo4j import GraphDatabase
    import os

    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        auth=(os.getenv('NEO4J_USER', 'neo4j'),
              os.getenv('NEO4J_PASSWORD', 'password'))
    )

    with driver.session() as session:
        for agent_id, new_prompt in optimized_prompts.items():
            session.run("""
                MATCH (a:Agent {agent_id: $agent_id})
                SET a.prompt = $new_prompt,
                    a.updated_at = datetime(),
                    a.version = coalesce(a.version, 0) + 1
            """, agent_id=agent_id, new_prompt=new_prompt)

            print(f"  ✓ Updated Agent: {agent_id}")

    driver.close()


if __name__ == '__main__':
    main()
