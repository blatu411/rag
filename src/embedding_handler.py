"""
BGE 向量化处理模块
使用 BGE-Small-zh-v1.5 模型进行文本向量化
"""
import numpy as np
from typing import List, Union
from FlagEmbedding import FlagModel
from loguru import logger


class BGEEmbeddingHandler:
    """BGE 向量化处理器"""

    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        """
        初始化 BGE 模型

        Args:
            model_name: 模型名称，默认为 BGE-Small-zh-v1.5
        """
        self.model_name = model_name
        logger.info(f"Loading BGE model: {model_name}")

        try:
            self.model = FlagModel(
                model_name,
                query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                use_fp16=True,  # 使用 FP16 加速（如果 GPU 支持）
            )
            logger.info(f"BGE model loaded successfully: {model_name}")
        except Exception as e:
            logger.warning(f"Failed to load with FP16, trying without FP16: {str(e)}")
            self.model = FlagModel(model_name)
            logger.info(f"BGE model loaded (without FP16): {model_name}")

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        批量向量化文本

        Args:
            texts: 文本列表

        Returns:
            向量数组，形状为 (n_texts, embedding_dim)
        """
        if not texts:
            logger.warning("Empty text list provided")
            return np.array([])

        try:
            logger.debug(f"Embedding {len(texts)} texts")
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            logger.debug(f"Embedding completed, shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding texts: {str(e)}")
            raise

    def embed_query(self, query: str) -> np.ndarray:
        """
        向量化查询文本

        使用特殊的检索指令来优化查询向量

        Args:
            query: 查询文本

        Returns:
            向量数组，形状为 (embedding_dim,)
        """
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return np.array([])

        try:
            logger.debug(f"Embedding query: {query[:50]}...")
            embeddings = self.model.encode_queries(query, normalize_embeddings=True)
            logger.debug(f"Query embedding completed, shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding query: {str(e)}")
            raise

    def embed_single_text(self, text: str) -> np.ndarray:
        """
        向量化单个文本

        Args:
            text: 文本

        Returns:
            向量数组，形状为 (embedding_dim,)
        """
        embeddings = self.embed_texts([text])
        return embeddings[0] if len(embeddings) > 0 else np.array([])

    def get_embedding_dim(self) -> int:
        """
        获取向量维度

        Returns:
            向量维度，通常为 384
        """
        # BGE-Small-zh-v1.5 的向量维度是 384
        return 384
