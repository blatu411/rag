"""
DeepSeek API 客户端模块
"""
import os
from typing import Iterator, List, Dict, Any
from openai import OpenAI
from loguru import logger
from config import settings


class DeepSeekClient:
    """DeepSeek API 客户端"""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        初始化 DeepSeek 客户端

        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            model: 模型名称
        """
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = base_url or settings.DEEPSEEK_BASE_URL
        self.model = model or settings.DEEPSEEK_MODEL

        if not self.api_key:
            raise ValueError(
                "DeepSeek API key is not configured. "
                "Please set DEEPSEEK_API_KEY in .env file"
            )

        # 配置代理（如果有环境变量）
        http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
        https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

        client_kwargs = {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": 30.0,
        }

        # 如果配置了代理，添加到客户端
        if http_proxy or https_proxy:
            client_kwargs["http_client"] = None  # 让 OpenAI 自动使用环境变量中的代理
            logger.info(f"使用代理: HTTP={http_proxy}, HTTPS={https_proxy}")

        self.client = OpenAI(**client_kwargs)
        logger.info(f"DeepSeek client initialized with model: {self.model}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        同步对话（非流式）

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            AI 回复文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Iterator[str]:
        """
        流式对话

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        Yields:
            AI 回复的文本块
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in chat_stream: {str(e)}")
            raise

    def count_tokens_estimate(self, text: str) -> int:
        """
        估算文本的 token 数量
        简单估算：1 token ≈ 4 个字符

        Args:
            text: 输入文本

        Returns:
            估算的 token 数
        """
        return len(text) // 4

    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        估算消息列表的总 token 数

        Args:
            messages: 消息列表

        Returns:
            估算的总 token 数
        """
        total_tokens = 0
        for message in messages:
            total_tokens += self.count_tokens_estimate(
                message.get("content", "")
            )
        # 消息头部开销（每条消息约4个token）
        total_tokens += len(messages) * 4
        return total_tokens
