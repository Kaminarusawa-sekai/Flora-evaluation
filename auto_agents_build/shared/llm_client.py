"""
LLM 客户端封装 - 统一的 LLM 调用接口
"""
import time
import json
import os
from typing import Dict, Any, List, Optional, Union
from .logger import get_logger
from .config_loader import get_config

logger = get_logger(__name__)


class LLMClient:
    """LLM 客户端，支持多种后端"""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.config = get_config()
        self.provider = provider or self.config.get('llm.provider', 'openai')
        self.model = model or self.config.get('llm.model', 'gpt-4')
        self.temperature = self.config.get('llm.temperature', 0.3)
        self.max_tokens = self.config.get('llm.max_tokens', 2000)
        self.api_key = self.config.get('llm.api_key')

        self._init_client()

    def _init_client(self):
        """初始化具体的 LLM 客户端"""
        if self.provider == 'openai':
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                logger.error("OpenAI library not installed. Run: pip install openai")
                raise
        elif self.provider == 'claude':
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                logger.error("Anthropic library not installed. Run: pip install anthropic")
                raise
        elif self.provider == 'qwen':
            try:
                from openai import OpenAI
                # Qwen 使用 OpenAI 兼容接口
                if "DASHSCOPE_API_KEY" in self.api_key:
                    self.client = OpenAI(
                        api_key=os.getenv(self.api_key),
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
                    )
                else:
                    self.client = OpenAI(
                        api_key=self.api_key,
                        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
                    )
            except ImportError:
                logger.error("OpenAI library not installed. Run: pip install openai")
                raise
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
        retry: int = 3
    ) -> str:
        """
        发送聊天请求

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大 token 数
            response_format: 响应格式，如 {"type": "json_object"}
            retry: 重试次数

        Returns:
            LLM 响应内容
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        for attempt in range(retry):
            try:
                if self.provider == 'openai' or self.provider == 'qwen':
                    kwargs = {
                        "model": self.model,
                        "messages": messages,
                        "temperature": temp,
                        "max_tokens": max_tok
                    }
                    if response_format:
                        kwargs["response_format"] = response_format

                    response = self.client.chat.completions.create(**kwargs)
                    return response.choices[0].message.content

                elif self.provider == 'claude':
                    # Claude API 格式略有不同
                    system_msg = None
                    user_messages = []

                    for msg in messages:
                        if msg['role'] == 'system':
                            system_msg = msg['content']
                        else:
                            user_messages.append(msg)

                    kwargs = {
                        "model": self.model,
                        "messages": user_messages,
                        "temperature": temp,
                        "max_tokens": max_tok
                    }
                    if system_msg:
                        kwargs["system"] = system_msg

                    response = self.client.messages.create(**kwargs)
                    return response.content[0].text

            except Exception as e:
                logger.warning(f"LLM call failed (attempt {attempt + 1}/{retry}): {e}")
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    raise

    def chat_with_json(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        retry: int = 3
    ) -> Dict[str, Any]:
        """
        发送聊天请求并解析 JSON 响应

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            retry: 重试次数

        Returns:
            解析后的 JSON 对象
        """
        # 添加 JSON 格式要求
        if messages and messages[-1]['role'] == 'user':
            messages[-1]['content'] += "\n\nPlease respond with valid JSON only."

        response_format = {"type": "json_object"} if self.provider == 'openai' else None

        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            retry=retry
        )

        # 解析 JSON
        try:
            # 尝试提取 JSON 代码块
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response}")
            raise ValueError(f"Invalid JSON response: {e}")

    def generate_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """
        生成文本的 embedding

        Args:
            text: 输入文本
            model: embedding 模型

        Returns:
            embedding 向量
        """
        if self.provider == 'openai':
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
        elif self.provider == 'qwen':
            if model == "text-embedding-ada-002":
                model = "text-embedding-v3"
            response =self.client.embeddings.create(
                model=model,
                input=text
            )
            
            return response.data[0].embedding
        else:
            raise NotImplementedError(f"Embedding not supported for provider: {self.provider}")

    def batch_generate_embeddings(self, texts: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
        """
        批量生成 embeddings

        Args:
            texts: 文本列表
            model: embedding 模型

        Returns:
            embedding 向量列表
        """
        if self.provider == 'openai' or self.provider == 'qwen':
            response = self.client.embeddings.create(
                model=model,
                input=texts
            )
            return [item.embedding for item in response.data]
        else:
            raise NotImplementedError(f"Batch embedding not supported for provider: {self.provider}")
