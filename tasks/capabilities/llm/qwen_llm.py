"""Qwen LLM适配器（基于 DashScope SDK）"""
from typing import Dict, Any, List, Optional, Union
import os
import json
from .interface import ILLMCapability


class QwenLLM(ILLMCapability):
    """
    基于 DashScope SDK 的 Qwen 适配器
    支持文本生成、多模态（VL）、JSON 解析、对话历史等
    """

    def __init__(
        self,

    ):

        super().__init__(

        )
        self.model_name = None
        self.vl_model_name = None
        self.dashscope = None
        self.is_initialized = False

    def initialize(self, config: Dict[str, Any]) -> None:
        # 从配置或环境中获取参数（如果提供）
        api_key = config.get("api_key") if config else None
        if not api_key:
            import os
            api_key = os.getenv("DASHSCOPE_API_KEY", "")
        if not api_key:
            try:
                from env import DASHSCOPE_API_KEY
                api_key = DASHSCOPE_API_KEY
            except ImportError:
                pass

        if not api_key:
            raise ValueError("DashScope API key is required. Provide via 'api_key' or DASHSCOPE_API_KEY.")

            # 初始化 DashScope SDK
        import dashscope
        print("DashScope API key loaded")
        dashscope.api_key = api_key
        self.dashscope = dashscope
        if 'model_name' in config:
            self.model_name = config['model_name'] or self.model_name
        else:
            self.model_name="qwen-max"
        if 'vl_model_name' in config:
            self.vl_model_name = config['vl_model_name'] or self.vl_model_name
        else:
            self.vl_model_name="qwen-vl-max"
        self.is_initialized = True

    def shutdown(self) -> None:
        # 清理资源
        self.is_initialized = False

    def get_capability_type(self) -> str:
        return 'qwen_llm'

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
        统一生成接口：自动根据是否含图片选择文本或 VL 模型
        """
        images = images or []
        if images:
            return self._call_vl_model(prompt, images, parse_json, json_schema, max_retries, **kwargs)
        else:
            return self._call_text_model(prompt, parse_json, json_schema, max_retries, **kwargs)

    def _call_text_model(
        self,
        prompt: str,
        parse_json: bool = False,
        json_schema: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        **kwargs
    ) -> Union[str, Dict[str, Any], None]:
        for attempt in range(max_retries):
            try:
                response = self.dashscope.Generation.call(
                    model=self.model_name,
                    prompt=prompt,
                    **kwargs
                )

                # 详细的错误检查
                if response is None:
                    print(f"[QwenLLM] Attempt {attempt+1}: Response is None")
                    continue

                # 检查 API 错误码
                if hasattr(response, 'status_code') and response.status_code != 200:
                    print(f"[QwenLLM] Attempt {attempt+1}: API error {response.status_code} - {getattr(response, 'message', 'Unknown error')}")
                    continue

                if not hasattr(response, 'output'):
                    print(f"[QwenLLM] Attempt {attempt+1}: Response has no 'output' attribute. Response: {response}")
                    continue

                if response.output is None:
                    print(f"[QwenLLM] Attempt {attempt+1}: response.output is None. Code: {getattr(response, 'code', 'N/A')}, Message: {getattr(response, 'message', 'N/A')}")
                    continue

                if not hasattr(response.output, 'text') or response.output.text is None:
                    print(f"[QwenLLM] Attempt {attempt+1}: response.output.text is None. Output: {response.output}")
                    continue

                text = response.output.text.strip()

                # 提取真实的 token 使用量（用于日志或监控）
                usage = getattr(response, 'usage', None)
                if usage:
                    prompt_tokens = getattr(usage, 'input_tokens', None)
                    completion_tokens = getattr(usage, 'output_tokens', None)
                    # 可以在这里记录日志
                    # print(f"Token usage: prompt={prompt_tokens}, completion={completion_tokens}")

                if not parse_json:
                    return text

                json_str = self._extract_json(text)
                if not json_str:
                    continue

                result = json.loads(json_str)
                if json_schema:
                    missing = [k for k in json_schema if k not in result]
                    if missing:
                        print(f"[QwenLLM] JSON 缺少字段: {missing}")
                return result

            except Exception as e:
                print(f"[QwenLLM Text Error] Attempt {attempt+1}: {type(e).__name__}: {e}")
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

                # 提取真实的 token 使用量（用于日志或监控）
                usage = getattr(response, 'usage', None)
                if usage:
                    prompt_tokens = getattr(usage, 'input_tokens', None)
                    completion_tokens = getattr(usage, 'output_tokens', None)
                    # 可以在这里记录日志
                    # print(f"Token usage: prompt={prompt_tokens}, completion={completion_tokens}")

                if not parse_json:
                    return text

                json_str = self._extract_json(text)
                if not json_str:
                    continue

                result = json.loads(json_str)
                if json_schema:
                    missing = [k for k in json_schema if k not in result]
                    if missing:
                        print(f"[QwenLLM] JSON 缺少字段: {missing}")
                return result

            except Exception as e:
                print(f"[QwenLLM VL Error] {e}")
                continue
        return None

    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        支持多轮对话（仅文本，不支持 VL）
        messages 格式: [{"role": "user", "content": "..."}, ...]
        """
        try:
            # DashScope 文本模型支持 messages 格式（需 qwen-turbo/max/plus 等）
            response = self.dashscope.Generation.call(
                model=self.model_name,
                messages=messages,
                **kwargs
            )
            print(f"DashScope response: {response}")
            if response and response.output and response.output.text:
                return {
                    "content": response.output.text.strip(),
                    "model": self.model_name,
                    "usage": getattr(response, 'usage', {}),
                    "id": getattr(response, 'request_id', '')
                }
            else:
                return {"content": "Error: No response", "error": "Empty response"}

        except Exception as e:
            return {"content": f"Error: {str(e)}", "error": str(e)}

    def embedding(self, text: str, model: str = "text-embedding-v1") -> List[float]:
        try:
            response = self.dashscope.TextEmbedding.call(
                model=model,
                input=[text]
            )
            if response and response.output and response.output.embeddings:
                return response.output.embeddings[0].embedding
            else:
                return []
        except Exception as e:
            print(f"[QwenLLM Embedding Error] {e}")
            return []

    def set_api_key(self, api_key: str) -> None:
        self.dashscope.api_key = api_key

    def set_default_model(self, model: str) -> None:
        self.model_name = model

    def get_supported_models(self) -> List[str]:
        return [
            "qwen-max", "qwen-plus", "qwen-turbo", "qwen-max-longcontext",
            "qwen-vl-max", "qwen-vl-plus"
        ]

    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        # 简单串行实现（DashScope SDK 本身不提供 batch 接口）
        return [self.generate(prompt, **kwargs) for prompt in prompts]

    @staticmethod
    def _extract_json(text: str) -> Optional[str]:
        """从文本中提取第一个合法 JSON 对象或数组"""
        if not text or not isinstance(text, str):
            return None

        stack = []
        start = -1
        i = 0
        n = len(text)

        while i < n:
            c = text[i]
            if c in '{[':
                if not stack:
                    start = i
                stack.append(c)
            elif c in '}]':
                if stack:
                    opening = stack.pop()
                    if (opening == '{' and c != '}') or (opening == '[' and c != ']'):
                        stack.clear()
                        start = -1
                    elif not stack and start != -1:
                        candidate = text[start:i+1]
                        try:
                            json.loads(candidate)
                            return candidate
                        except Exception:
                            start = -1
            i += 1
        return None
