"""
LLM客户端模块 - 统一的LLM API调用接口
"""
import logging
import time
from typing import Optional, Callable
from abc import ABC, abstractmethod
from functools import wraps
from config import APOConfig


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    重试装饰器 - 在API调用失败时自动重试

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 延迟倍数（每次重试延迟时间翻倍）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    # 如果返回空字符串，也视为失败（LLM调用应该有响应）
                    if result or attempt == max_retries - 1:
                        return result
                    # 空结果且还有重试机会，继续重试
                    raise Exception("API返回空响应")
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        # 获取logger（从self获取）
                        if args and hasattr(args[0], 'logger'):
                            args[0].logger.warning(
                                f"API调用失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
                            )
                            args[0].logger.info(f"等待 {current_delay:.1f}秒后重试...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        # 最后一次重试也失败
                        if args and hasattr(args[0], 'logger'):
                            args[0].logger.error(
                                f"❌ API调用失败，已重试{max_retries}次: {str(e)}"
                            )

            return ""  # 所有重试都失败，返回空字符串
        return wrapper
    return decorator


class BaseLLMClient(ABC):
    """LLM客户端基类"""

    def __init__(self, config: APOConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def call(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        调用LLM API

        Args:
            prompt: 输入提示词
            temperature: 温度参数（可选，默认使用config中的值）
            max_tokens: 最大token数（可选，默认使用config中的值）

        Returns:
            LLM生成的文本
        """
        pass


class QwenClient(BaseLLMClient):
    """千问（Qwen）API客户端 - 支持自动重试和友好错误提示"""

    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    def call(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        调用千问(Qwen) LLM API

        Args:
            prompt: 输入提示词
            temperature: 温度参数（可选）
            max_tokens: 最大token数（可选）

        Returns:
            LLM生成的文本
        """
        # 使用提供的参数或配置中的默认值
        temp = temperature if temperature is not None else self.config.llm_temperature
        tokens = max_tokens if max_tokens is not None else self.config.llm_max_tokens

        try:
            import dashscope
            from dashscope import Generation

            # 验证API密钥
            if not self.config.llm_api_key:
                error_msg = """
❌ API密钥未设置！

请按以下步骤配置：
1. 复制 .env.example 为 .env
2. 在 .env 文件中填入你的千问API密钥：
   QWEN_API_KEY=your_actual_api_key_here
3. 获取API密钥：https://dashscope.console.aliyun.com/apiKey

提示：确保.env文件在项目根目录
"""
                self.logger.error(error_msg)
                raise ValueError("API密钥未配置")

            # 设置API key
            dashscope.api_key = self.config.llm_api_key

            # 调用千问API（使用messages格式而非prompt）
            response = Generation.call(
                model=self.config.llm_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temp,
                max_tokens=tokens,
            )

            # 检查响应状态
            if response.status_code == 200:
                # 安全地提取响应文本
                try:
                    # 千问API的标准响应格式: response.output.choices[0].message.content
                    if hasattr(response, 'output') and response.output:
                        if hasattr(response.output, 'choices') and response.output.choices:
                            message = response.output.choices[0].message
                            if hasattr(message, 'content') and message.content:
                                return message.content.strip()

                        # 备用：尝试 text 字段（旧版API）
                        if hasattr(response.output, 'text') and response.output.text:
                            return response.output.text.strip()

                    # 调试信息
                    self.logger.error(f"无法从响应中提取文本。")
                    self.logger.error(f"Response有这些属性: {[a for a in dir(response) if not a.startswith('_')]}")
                    if hasattr(response, 'output') and response.output:
                        self.logger.error(f"Output有这些属性: {[a for a in dir(response.output) if not a.startswith('_')]}")
                    return ""
                except Exception as extract_error:
                    self.logger.error(f"提取响应文本失败: {str(extract_error)}")
                    import traceback
                    self.logger.error(traceback.format_exc())
                    return ""
            else:
                error_msg = f"""
❌ API调用失败！

错误代码: {response.code}
错误信息: {response.message}

可能的原因：
1. API密钥无效或已过期
2. 网络连接问题
3. 请求频率超限
4. 账户余额不足

建议：
- 检查API密钥是否正确
- 确认网络连接正常
- 查看控制台：https://dashscope.console.aliyun.com/
"""
                self.logger.error(error_msg)
                raise Exception(f"API调用失败: {response.code} - {response.message}")

        except ImportError:
            error_msg = """
❌ 缺少依赖库！

请执行以下命令安装：
    pip install dashscope

或者安装所有依赖：
    pip install -r requirements.txt
"""
            self.logger.error(error_msg)
            raise ImportError("dashscope库未安装")
        except Exception as e:
            self.logger.error(f"API调用出错: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return ""


class LLMClientFactory:
    """LLM客户端工厂类"""

    @staticmethod
    def create_client(config: APOConfig, provider: str = "qwen") -> BaseLLMClient:
        """
        创建LLM客户端

        Args:
            config: APO配置
            provider: LLM提供商 ('qwen', 'openai', 'anthropic')

        Returns:
            LLM客户端实例

        Raises:
            ValueError: 不支持的provider
        """
        if provider.lower() == "qwen":
            return QwenClient(config)
        # 未来可以添加其他provider
        # elif provider.lower() == "openai":
        #     return OpenAIClient(config)
        # elif provider.lower() == "anthropic":
        #     return AnthropicClient(config)
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")


# 便捷函数
def create_llm_client(config: APOConfig, provider: str = "qwen") -> BaseLLMClient:
    """
    创建LLM客户端的便捷函数

    Args:
        config: APO配置
        provider: LLM提供商

    Returns:
        LLM客户端实例
    """
    return LLMClientFactory.create_client(config, provider)
