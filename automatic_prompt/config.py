"""
APO配置文件
"""
import os
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

# 尝试加载.env文件（如果存在）
try:
    from dotenv import load_dotenv
    # 获取当前文件所在目录（项目根目录）
    current_dir = Path(__file__).resolve().parent
    dotenv_path = current_dir / '.env'
    load_dotenv(dotenv_path=dotenv_path)
except ImportError:
    pass  # 如果没有安装python-dotenv，继续使用系统环境变量


@dataclass
class APOConfig:
    """自动提示词优化配置"""

    # LLM配置
    llm_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    llm_model: str = os.getenv("QWEN_MODEL", "qwen-max")
    llm_temperature: float = float(os.getenv("QWEN_TEMPERATURE", "0.7"))
    llm_max_tokens: int = int(os.getenv("QWEN_MAX_TOKENS", "500"))

    # 优化配置
    max_iterations: int = 10  # 最大迭代次数
    num_candidates: int = 5  # 每次迭代生成的候选数
    top_k: int = 3  # 保留的最优候选数
    early_stop_threshold: float = 0.95  # 早停阈值

    # 评估配置
    evaluation_metric: str = "accuracy"  # accuracy, f1, bleu, rouge
    use_llm_feedback: bool = True  # 是否使用LLM反馈

    # 生成策略
    generation_strategy: str = "llm_rewrite"  # llm_rewrite, genetic, mutation

    # UCB参数（用于候选选择）
    ucb_c: float = 1.414  # UCB探索参数

    # 其他
    seed: int = 42
    verbose: bool = True


@dataclass
class Task:
    """任务定义"""
    name: str
    description: str
    examples: List[dict]  # [{"input": "...", "output": "..."}, ...]
    validation_data: List[dict]  # 验证集

    # 分层提示词支持（方案4）
    core_instruction: Optional[str] = None  # 核心指令（待优化部分），None则使用description
    context_template: Optional[str] = None  # 上下文模板，如："参考信息：{context}"
    example_template: Optional[str] = None  # 示例模板，如："示例{index}: Q: {input} A: {output}"
    options_template: Optional[str] = None  # 选项模板，如："选项：\n{options}"，支持多选题场景
    prompt_structure: Optional[List[str]] = None  # 提示词结构顺序，默认：["core", "context", "examples", "input", "options"]

    def get_core_instruction(self) -> str:
        """获取核心指令，如果未设置则返回description"""
        return self.core_instruction if self.core_instruction is not None else self.description

    def get_prompt_structure(self) -> List[str]:
        """获取提示词结构顺序"""
        return self.prompt_structure if self.prompt_structure is not None else ["core", "context", "examples", "input", "options"]
