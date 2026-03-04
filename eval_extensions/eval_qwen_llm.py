"""评估模式的 Qwen LLM 包装器，添加 token 统计功能"""
import sys
import os
from typing import Dict, Any, List, Optional, Union

# 确保 tasks 目录在路径中
_TASKS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tasks"))
if _TASKS_ROOT not in sys.path:
    sys.path.insert(0, _TASKS_ROOT)

from capabilities.llm.qwen_llm import QwenLLM


def _get_token_tracker():
    """获取 token 统计器"""
    try:
        from coop_eval_actual.utils import token_tracker
        return token_tracker
    except ImportError:
        return None


def _get_current_task_context():
    """获取当前任务上下文（task_id, layer）"""
    try:
        from coop_eval_actual.utils import task_context_manager
        return task_context_manager.get_current_task()
    except ImportError:
        return (None, 0)


class EvalQwenLLM(QwenLLM):
    """
    评估模式的 Qwen LLM 包装器
    在原有功能基础上添加 token 统计
    """

    def __init__(self):
        super().__init__()

    def get_capability_type(self) -> str:
        return 'eval_qwen_llm'

    def generate(
        self,
        prompt: str,
        images: Optional[List[str]] = None,
        parse_json: bool = False,
        json_schema: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        **kwargs
    ) -> Union[str, Dict[str, Any], None]:
        """
        统一生成接口：在调用父类方法后记录 token
        """
        result = super().generate(prompt, images, parse_json, json_schema, max_retries, **kwargs)

        # 注意：父类的 _call_text_model 和 _call_vl_model 已经有 token 统计
        # 但为了确保在 tasks 被替换后仍能工作，这里也可以添加统计
        # 不过要避免重复统计，所以这里不再额外统计

        return result

    def _call_text_model(
        self,
        prompt: str,
        parse_json: bool = False,
        json_schema: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        **kwargs
    ) -> Union[str, Dict[str, Any], None]:
        """重写文本模型调用，添加 token 统计"""
        for attempt in range(max_retries):
            try:
                response = self.dashscope.Generation.call(
                    model=self.model_name,
                    prompt=prompt,
                    **kwargs
                )

                if response is None:
                    continue

                if hasattr(response, 'status_code') and response.status_code != 200:
                    continue

                if not hasattr(response, 'output') or response.output is None:
                    continue

                if not hasattr(response.output, 'text') or response.output.text is None:
                    continue

                text = response.output.text.strip()

                # 提取真实的 token 使用量
                usage = getattr(response, 'usage', None)
                prompt_tokens = None
                completion_tokens = None
                if usage:
                    prompt_tokens = getattr(usage, 'input_tokens', None)
                    completion_tokens = getattr(usage, 'output_tokens', None)

                # 记录 token 消耗（评估模式）
                self._record_token_usage(prompt, text, kwargs.get('agent_id', ''),
                                        prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)

                if not parse_json:
                    return text

                json_str = self._extract_json(text)
                if not json_str:
                    continue

                import json
                result = json.loads(json_str)
                if json_schema:
                    missing = [k for k in json_schema if k not in result]
                    if missing:
                        print(f"[EvalQwenLLM] JSON 缺少字段: {missing}")
                return result

            except Exception as e:
                print(f"[EvalQwenLLM Text Error] Attempt {attempt+1}: {type(e).__name__}: {e}")
                continue
        return None

    def _call_vl_model(
        self,
        prompt: str,
        images: List[str],
        parse_json: bool = False,
        json_schema: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        **kwargs
    ) -> Union[str, Dict[str, Any], None]:
        """重写 VL 模型调用，添加 token 统计"""
        for _ in range(max_retries):
            try:
                response = self.dashscope.MultiModalConversation.call(
                    model=self.vl_model_name,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"image": img} for img in images
                        ] + [{"text": prompt}]
                    }],
                    **kwargs
                )

                if not response or not response.output or not response.output.choices:
                    continue

                text = response.output.choices[0].message.content[0].text.strip()

                # 提取真实的 token 使用量
                usage = getattr(response, 'usage', None)
                prompt_tokens = None
                completion_tokens = None
                if usage:
                    prompt_tokens = getattr(usage, 'input_tokens', None)
                    completion_tokens = getattr(usage, 'output_tokens', None)

                # 记录 token 消耗（评估模式）
                self._record_token_usage(prompt, text, kwargs.get('agent_id', ''),
                                        prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)

                if not parse_json:
                    return text

                json_str = self._extract_json(text)
                if not json_str:
                    continue

                import json
                result = json.loads(json_str)
                if json_schema:
                    missing = [k for k in json_schema if k not in result]
                    if missing:
                        print(f"[EvalQwenLLM] JSON 缺少字段: {missing}")
                return result

            except Exception as e:
                print(f"[EvalQwenLLM VL Error] {e}")
                continue
        return None

    def _record_token_usage(self, prompt: str, completion: str, agent_id: str = "",
                            prompt_tokens: int = None, completion_tokens: int = None) -> None:
        """记录 token 消耗（仅在评估模式下生效）"""
        tracker = _get_token_tracker()
        if tracker:
            task_id, layer = _get_current_task_context()
            if task_id:
                tracker.record_llm_call(
                    task_id=task_id,
                    prompt=prompt,
                    completion=completion,
                    layer=layer,
                    agent_id=agent_id,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens
                )
