"""
部分流程示例 - 只运行特定阶段
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.pipeline_orchestrator import PipelineOrchestrator
from adapters import *


def run_normalization_only():
    """只运行 API 规范化"""
    print("=" * 70)
    print("Running Normalization Only")
    print("=" * 70)

    orchestrator = PipelineOrchestrator('config/pipeline_config.yaml')
    orchestrator.register_module('normalization', NormalizationAdapter())

    results = orchestrator.run_pipeline(
        start_stage='normalization',
        end_stage='normalization'
    )

    print(f"\n✅ Generated {len(results['normalization'].capabilities)} capabilities")
    return results


def run_testing_branch():
    """只运行测试分支（3B -> 4B -> 5）"""
    print("=" * 70)
    print("Running Testing Branch (3B -> 4B -> 5)")
    print("=" * 70)

    orchestrator = PipelineOrchestrator('config/pipeline_config.yaml')

    # 注册测试分支相关模块
    orchestrator.register_module('scenario_generation', ScenarioAdapter())
    orchestrator.register_module('mock_service', MockAdapter())
    orchestrator.register_module('evaluation', EvaluationAdapter())

    results = orchestrator.run_pipeline(
        start_stage='scenario_generation',
        end_stage='evaluation'
    )

    print(f"\n✅ Testing branch completed")
    print(f"   Scenarios: {len(results['scenario_generation'].scenarios)}")
    print(f"   Success Rate: {results['evaluation'].success_rate:.2%}")

    return results


def run_build_branch():
    """只运行构建分支（3A -> 4A）"""
    print("=" * 70)
    print("Running Build Branch (3A -> 4A)")
    print("=" * 70)

    orchestrator = PipelineOrchestrator('config/pipeline_config.yaml')

    orchestrator.register_module('database_mapping', EntiMapAdapter())
    orchestrator.register_module('agent_build', AgentBuildAdapter())

    results = orchestrator.run_pipeline(
        start_stage='database_mapping',
        end_stage='agent_build'
    )

    print(f"\n✅ Build branch completed")
    print(f"   Entity Mappings: {len(results['database_mapping'].entity_mappings)}")
    print(f"   Agents: {len(results['agent_build'].org_blueprint.get('agents', []))}")

    return results


def run_stages_1_to_3():
    """运行 Stage 1-3（规范化 -> 拓扑 -> 映射/场景）"""
    print("=" * 70)
    print("Running Stages 1-3")
    print("=" * 70)

    orchestrator = PipelineOrchestrator('config/pipeline_config.yaml')

    # 注册前三个阶段的模块
    orchestrator.register_module('normalization', NormalizationAdapter())
    orchestrator.register_module('topology', TopologyAdapter())
    orchestrator.register_module('database_mapping', EntiMapAdapter())
    orchestrator.register_module('scenario_generation', ScenarioAdapter())

    results = orchestrator.run_pipeline(
        start_stage='normalization',
        end_stage='scenario_generation'
    )

    print(f"\n✅ Stages 1-3 completed")
    return results


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1]

        if mode == 'normalization':
            run_normalization_only()
        elif mode == 'testing':
            run_testing_branch()
        elif mode == 'build':
            run_build_branch()
        elif mode == 'stages1-3':
            run_stages_1_to_3()
        else:
            print(f"Unknown mode: {mode}")
            print("Available modes: normalization, testing, build, stages1-3")
    else:
        print("Usage: python partial_pipeline.py <mode>")
        print("Modes:")
        print("  normalization - Run only API normalization")
        print("  testing       - Run testing branch (3B -> 4B -> 5)")
        print("  build         - Run build branch (3A -> 4A)")
        print("  stages1-3     - Run stages 1-3")
