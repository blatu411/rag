"""
内存版知识库处理器
不依赖 ChromaDB，使用内存存储
用于避免 SQLite 版本问题
"""
import numpy as np
from typing import List, Dict, Optional
from loguru import logger
from sklearn.metrics.pairwise import cosine_similarity


class MemoryKBHandler:
    """内存版知识库处理器"""

    def __init__(self, embedding_handler):
        """
        初始化内存知识库

        Args:
            embedding_handler: BGE 向量化处理器
        """
        self.embedding_handler = embedding_handler
        self.documents = []  # 存储文档内容
        self.embeddings = []  # 存储向量
        self.metadata = []  # 存储元数据
        self.ids = []  # 存储文档 ID

        logger.info("Memory KB Handler initialized")

    def add_documents(
        self,
        documents: List[str],
        metadata: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        添加文档到知识库

        Args:
            documents: 文档内容列表
            metadata: 元数据列表（可选）
            ids: 文档 ID 列表（可选）
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")

        if metadata is None:
            metadata = [{} for _ in documents]

        if ids is None:
            ids = [f"doc_{i}_{hash(doc)}" for i, doc in enumerate(documents)]

        try:
            logger.info(f"Adding {len(documents)} documents to memory KB")

            # 向量化文档
            embeddings = self.embedding_handler.embed_texts(documents)

            # 添加到内存
            self.documents.extend(documents)
            self.embeddings.extend(embeddings)
            self.metadata.extend(metadata)
            self.ids.extend(ids)

            logger.info(f"Successfully added {len(documents)} documents")
            logger.info(f"Knowledge base now contains {len(self.documents)} documents")

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> Dict:
        """
        检索相关文档

        Args:
            query: 查询文本
            top_k: 返回最相关的 k 个文档

        Returns:
            包含检索结果的字典
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not self.documents:
            logger.debug("Knowledge base is empty")
            return {
                "ids": [],
                "documents": [],
                "metadatas": [],
                "distances": [],
            }

        try:
            logger.debug(f"Retrieving top {top_k} documents for query: {query[:50]}...")

            # 向量化查询
            query_embedding = self.embedding_handler.embed_query(query)

            # 计算相似度
            if len(self.embeddings) == 0:
                return {
                    "ids": [],
                    "documents": [],
                    "metadatas": [],
                    "distances": [],
                }

            embeddings_array = np.array(self.embeddings)
            similarities = cosine_similarity([query_embedding], embeddings_array)[0]

            # 获取 top-k 索引
            top_indices = np.argsort(-similarities)[:top_k]

            # 构建结果
            results = {
                "ids": [self.ids[i] for i in top_indices],
                "documents": [self.documents[i] for i in top_indices],
                "metadatas": [self.metadata[i] for i in top_indices],
                "distances": [1 - similarities[i] for i in top_indices],  # 转换为距离
            }

            logger.debug(f"Retrieved {len(results['documents'])} documents")
            return results

        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise

    def delete_document(self, doc_id: str) -> None:
        """
        删除指定的文档

        Args:
            doc_id: 文档 ID
        """
        try:
            logger.info(f"Deleting document: {doc_id}")

            if doc_id in self.ids:
                idx = self.ids.index(doc_id)
                self.ids.pop(idx)
                self.documents.pop(idx)
                self.embeddings.pop(idx)
                self.metadata.pop(idx)

                logger.info(f"Document deleted. KB now contains {len(self.documents)} documents")
            else:
                logger.warning(f"Document not found: {doc_id}")

        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise

    def clear_collection(self) -> None:
        """清空整个知识库"""
        try:
            logger.warning("Clearing entire knowledge base")
            self.documents = []
            self.embeddings = []
            self.metadata = []
            self.ids = []
            logger.info("Knowledge base cleared")
        except Exception as e:
            logger.error(f"Error clearing knowledge base: {str(e)}")
            raise

    def get_document_count(self) -> int:
        """获取知识库中的文档数量"""
        return len(self.documents)

    def get_all_documents(self) -> Dict:
        """获取知识库中的所有文档"""
        return {
            "ids": self.ids.copy(),
            "documents": self.documents.copy(),
            "metadatas": self.metadata.copy(),
        }
