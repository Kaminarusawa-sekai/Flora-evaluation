"""
流程编排器 - 负责协调所有模块的执行
"""

from typing import Dict, List, Optional
import yaml
import json
import logging
from pathlib import Path


class PipelineOrchestrator:
    """
    流程编排器 - 负责协调所有模块的执行
    """

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.modules = {}
        self.results = {}
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("PipelineOrchestrator")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def register_module(self, stage_name: str, module_instance):
        """注册模块"""
        self.modules[stage_name] = module_instance
        self.logger.info(f"Registered module: {stage_name}")

    def run_pipeline(self, start_stage: Optional[str] = None,
                     end_stage: Optional[str] = None):
        """
        运行完整流程或部分流程
        Args:
            start_stage: 起始阶段（None 表示从头开始）
            end_stage: 结束阶段（None 表示运行到最后）
        """
        stages = self.config['stages']
        stage_names = list(stages.keys())

        # 确定执行范围
        start_idx = stage_names.index(start_stage) if start_stage else 0
        end_idx = stage_names.index(end_stage) + 1 if end_stage else len(stage_names)

        self.logger.info("=" * 70)
        self.logger.info(f"Starting Pipeline: {self.config['pipeline']['name']}")
        self.logger.info(f"Version: {self.config['pipeline']['version']}")
        self.logger.info(f"Stages: {stage_names[start_idx:end_idx]}")
        self.logger.info("=" * 70)

        # 执行各阶段
        for stage_name in stage_names[start_idx:end_idx]:
            stage_config = stages[stage_name]

            if not stage_config.get('enabled', True):
                self.logger.info(f"[SKIP] Stage {stage_name} is disabled")
                continue

            self.logger.info(f"\n[RUN] Stage: {stage_name}")
            result = self._execute_stage(stage_name, stage_config)
            self.results[stage_name] = result

        self.logger.info("\n" + "=" * 70)
        self.logger.info("Pipeline Completed Successfully!")
        self.logger.info("=" * 70)

        return self.results

    def _execute_stage(self, stage_name: str, stage_config: Dict):
        """执行单个阶段"""
        # 加载输入数据
        self.logger.info(f"  Loading input...")
        input_data = self._load_input(stage_config['input'])

        # 获取模块实例
        module = self.modules.get(stage_name)
        if not module:
            raise ValueError(f"Module not registered: {stage_name}")

        # 验证输入
        if not module.validate_input(input_data):
            raise ValueError(f"Invalid input for stage: {stage_name}")

        # 执行处理
        self.logger.info(f"  Processing...")
        result = module.process(input_data, stage_config['config'])

        # 保存输出
        self.logger.info(f"  Saving output...")
        self._save_output(result, stage_config['output'])

        self.logger.info(f"  ✓ Stage {stage_name} completed")

        return result

    def _load_input(self, input_config: Dict):
        """加载输入数据"""
        input_type = input_config['type']

        if input_type == 'file':
            return self._load_from_file(input_config['path'])
        elif input_type == 'neo4j':
            return self._load_from_neo4j(input_config['database'])
        elif input_type == 'multiple':
            return {
                src: self._load_input({'type': 'file', 'path': src})
                for src in input_config['sources']
            }
        else:
            raise ValueError(f"Unknown input type: {input_type}")

    def _load_from_file(self, file_path: str):
        """从文件加载数据"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_from_neo4j(self, database: str):
        """从 Neo4j 加载数据"""
        # TODO: 实现 Neo4j 数据加载
        return {'database': database}

    def _save_output(self, result, output_config: Dict):
        """保存输出数据"""
        output_type = output_config['type']

        if output_type == 'file':
            self._save_to_file(result, output_config['path'])
        elif output_type == 'neo4j':
            self._save_to_neo4j(result, output_config['database'])
        elif output_type == 'service':
            # 服务类型不需要保存
            pass
        elif output_type == 'feedback':
            # 反馈到指定阶段
            self._send_feedback(result, output_config['target_stage'])

    def _save_to_file(self, result, file_path: str):
        """保存到文件"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # 如果是 Pydantic 模型，转换为字典
        if hasattr(result, 'model_dump'):
            result = result.model_dump()

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)

    def _save_to_neo4j(self, result, database: str):
        """保存到 Neo4j"""
        # TODO: 实现 Neo4j 数据保存
        pass

    def _send_feedback(self, result, target_stage: str):
        """发送反馈到指定阶段"""
        # TODO: 实现反馈机制
        pass
