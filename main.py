"""
主入口 - Flora-Evaluation Pipeline
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.pipeline_orchestrator import PipelineOrchestrator
from adapters import (
    NormalizationAdapter,
    TopologyAdapter,
    EntiMapAdapter,
    ScenarioAdapter,
    AgentBuildAdapter,
    MockAdapter,
    EvaluationAdapter,
    OptimizationAdapter
)


def main():
    """主函数"""
    print("=" * 70)
    print("Flora-Evaluation Pipeline")
    print("=" * 70)

    # 检查环境变量
    required_env_vars = [
        'NEO4J_URI',
        'NEO4J_USER',
        'NEO4J_PASSWORD',
        'DASHSCOPE_API_KEY',
        'DATABASE_URL'
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"\n⚠️  警告: 以下环境变量未设置: {', '.join(missing_vars)}")
        print("请在 .env 文件中配置或通过环境变量设置\n")

    # 创建输出目录
    output_dirs = [
        'output/stage1',
        'output/stage2',
        'output/stage3a',
        'output/stage3b',
        'output/stage4a',
        'output/stage4b',
        'output/stage5',
        'output/stage6'
    ]

    for dir_path in output_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

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
    try:
        results = orchestrator.run_pipeline()

        # 输出结果摘要
        print("\n" + "=" * 70)
        print("Pipeline Execution Summary")
        print("=" * 70)

        for stage_name, result in results.items():
            print(f"\n[{stage_name}]")
            if hasattr(result, 'metadata'):
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
        sys.exit(1)


if __name__ == '__main__':
    main()
