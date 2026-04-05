"""
CLI 工具 - Flora-Evaluation Pipeline
"""

import click
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.pipeline_orchestrator import PipelineOrchestrator
from adapters import *


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Flora-Evaluation Pipeline CLI"""
    pass


@cli.command()
@click.option('--config', '-c', default='config/pipeline_config.yaml', help='配置文件路径')
@click.option('--env', '-e', default='development', help='运行环境 (development/production)')
@click.option('--start', '-s', default=None, help='起始阶段')
@click.option('--end', '-E', default=None, help='结束阶段')
def run(config, env, start, end):
    """运行完整流程或部分流程"""

    # 设置环境
    os.environ['FLORA_ENV'] = env

    click.echo(f"🚀 Starting Flora-Evaluation Pipeline")
    click.echo(f"   Environment: {env}")
    click.echo(f"   Config: {config}")

    if start or end:
        click.echo(f"   Range: {start or 'start'} -> {end or 'end'}")

    # 创建编排器
    orchestrator = PipelineOrchestrator(config)

    # 注册所有模块
    _register_modules(orchestrator)

    # 运行流程
    try:
        results = orchestrator.run_pipeline(start_stage=start, end_stage=end)

        click.echo("\n✅ Pipeline completed successfully!")
        click.echo(f"   Total stages: {len(results)}")

    except Exception as e:
        click.echo(f"\n❌ Pipeline failed: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('stage_name')
@click.option('--config', '-c', default='config/pipeline_config.yaml', help='配置文件路径')
def run_stage(stage_name, config):
    """运行单个阶段"""

    click.echo(f"🔧 Running stage: {stage_name}")

    orchestrator = PipelineOrchestrator(config)
    _register_modules(orchestrator)

    try:
        results = orchestrator.run_pipeline(start_stage=stage_name, end_stage=stage_name)
        click.echo(f"✅ Stage '{stage_name}' completed!")

    except Exception as e:
        click.echo(f"❌ Stage '{stage_name}' failed: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--config', '-c', default='config/pipeline_config.yaml', help='配置文件路径')
def list_stages(config):
    """列出所有可用阶段"""

    from core.config_manager import ConfigManager

    config_manager = ConfigManager()
    pipeline_config = config_manager.load_config('pipeline_config')

    click.echo("📋 Available stages:\n")

    for stage_name, stage_config in pipeline_config['stages'].items():
        enabled = "✓" if stage_config.get('enabled', True) else "✗"
        module = stage_config['module']

        click.echo(f"  [{enabled}] {stage_name}")
        click.echo(f"      Module: {module}")
        click.echo(f"      Input: {stage_config['input']['type']}")
        click.echo(f"      Output: {stage_config['output']['type']}")
        click.echo()


@cli.command()
@click.option('--output', '-o', default='output/status.json', help='输出状态文件')
def status(output):
    """查看流程状态"""

    import json

    click.echo("📊 Pipeline Status:\n")

    # 检查各阶段的输出文件
    stages = [
        ('normalization', 'output/stage1/capabilities.json'),
        ('topology', 'output/stage2/topology.json'),
        ('database_mapping', 'output/stage3a/entity_mapping.json'),
        ('scenario_generation', 'output/stage3b/scenarios.json'),
        ('agent_build', 'output/stage4a/agent_system.json'),
        ('mock_service', 'output/stage4b/service_info.json'),
        ('evaluation', 'output/stage5/evaluation_results.json'),
        ('optimization', 'output/stage6/optimization.json')
    ]

    status_info = {}

    for stage_name, output_path in stages:
        if Path(output_path).exists():
            click.echo(f"  ✓ {stage_name}: Completed")
            status_info[stage_name] = 'completed'
        else:
            click.echo(f"  ○ {stage_name}: Not started")
            status_info[stage_name] = 'not_started'

    # 保存状态
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(status_info, f, indent=2)

    click.echo(f"\n📄 Status saved to: {output}")


@cli.command()
@click.argument('input_file')
def validate(input_file):
    """验证输入文件格式"""

    import json
    from schemas.schemas import Stage1Output, Stage2Output, Stage3AOutput, Stage3BOutput

    click.echo(f"🔍 Validating: {input_file}")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 尝试识别数据类型并验证
        if 'capabilities' in data:
            Stage1Output(**data)
            click.echo("✅ Valid Stage 1 output (API Normalization)")
        elif 'dependencies' in data:
            Stage2Output(**data)
            click.echo("✅ Valid Stage 2 output (API Topology)")
        elif 'entity_mappings' in data:
            Stage3AOutput(**data)
            click.echo("✅ Valid Stage 3A output (Database Mapping)")
        elif 'scenarios' in data:
            Stage3BOutput(**data)
            click.echo("✅ Valid Stage 3B output (Scenario Generation)")
        else:
            click.echo("⚠️  Unknown data format", err=True)

    except Exception as e:
        click.echo(f"❌ Validation failed: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'markdown']), default='json', help='导出格式')
@click.option('--output', '-o', default='output/export', help='导出目录')
def export(format, output):
    """导出流程结果"""

    import json
    import yaml

    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"📦 Exporting results to: {output_dir}")

    # 收集所有阶段的输出
    stages = {
        'stage1': 'output/stage1/capabilities.json',
        'stage2': 'output/stage2/topology.json',
        'stage3a': 'output/stage3a/entity_mapping.json',
        'stage3b': 'output/stage3b/scenarios.json',
        'stage4a': 'output/stage4a/agent_system.json',
        'stage5': 'output/stage5/evaluation_results.json',
        'stage6': 'output/stage6/optimization.json'
    }

    for stage_name, stage_path in stages.items():
        if Path(stage_path).exists():
            with open(stage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if format == 'json':
                export_path = output_dir / f"{stage_name}.json"
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            elif format == 'yaml':
                export_path = output_dir / f"{stage_name}.yaml"
                with open(export_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True)

            elif format == 'markdown':
                export_path = output_dir / f"{stage_name}.md"
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {stage_name.upper()} Results\n\n")
                    f.write(f"```json\n{json.dumps(data, indent=2, ensure_ascii=False)}\n```\n")

            click.echo(f"  ✓ Exported: {export_path}")

    click.echo("\n✅ Export completed!")


def _register_modules(orchestrator):
    """注册所有模块"""
    orchestrator.register_module('normalization', NormalizationAdapter())
    orchestrator.register_module('topology', TopologyAdapter())
    orchestrator.register_module('database_mapping', EntiMapAdapter())
    orchestrator.register_module('scenario_generation', ScenarioAdapter())
    orchestrator.register_module('agent_build', AgentBuildAdapter())
    orchestrator.register_module('mock_service', MockAdapter())
    orchestrator.register_module('evaluation', EvaluationAdapter())
    orchestrator.register_module('optimization', OptimizationAdapter())


if __name__ == '__main__':
    cli()
