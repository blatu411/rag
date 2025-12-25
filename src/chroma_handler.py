"""
ChromaDB 知识库管理模块
"""
import chromadb
from typing import List, Dict, Optional
from loguru import logger
from pathlib import Path


class ChromaHandler:
    """ChromaDB 知识库管理器"""

    def __init__(
        self,
        embedding_handler,
        persist_directory: str = "./data/chroma_db",
        collection_name: str = "deepseek_knowledge_base",
    ):
        """
        初始化 ChromaDB

        Args:
            embedding_handler: BGE 向量化处理器
            persist_directory: 持久化存储目录
            collection_name: 集合名称
        """
        self.embedding_handler = embedding_handler
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # 创建存储目录
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing ChromaDB at {persist_directory}")

        try:
            # 创建持久化客户端
            self.client = chromadb.PersistentClient(path=persist_directory)

            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},  # 使用余弦相似度
            )

            logger.info(f"ChromaDB initialized successfully")
            logger.info(f"Collection '{collection_name}' contains {self.collection.count()} documents")

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise

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
            metadata: 元数据列表（可选），每个元数据对应一个文档
            ids: 文档 ID 列表（可选），如果不提供会自动生成

        Raises:
            ValueError: 参数验证失败
            Exception: ChromaDB 操作失败
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")

        if metadata is None:
            metadata = [{} for _ in documents]

        if ids is None:
            ids = [f"doc_{i}_{hash(doc)}" for i, doc in enumerate(documents)]

        if len(documents) != len(metadata):
            raise ValueError("documents and metadata must have the same length")

        try:
            logger.info(f"Adding {len(documents)} documents to knowledge base")

            # 向量化文档
            embeddings = self.embedding_handler.embed_texts(documents)

            # 添加到 ChromaDB
            self.collection.add(
                embeddings=embeddings.tolist(),
                metadatas=metadata,
                documents=documents,
                ids=ids,
            )

            logger.info(f"Successfully added {len(documents)} documents")
            logger.info(f"Collection now contains {self.collection.count()} documents")

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
            包含检索结果的字典，包含：
            - ids: 文档 ID 列表
            - documents: 文档内容列表
            - metadatas: 元数据列表
            - distances: 距离值列表（越小越相关）
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        try:
            logger.debug(f"Retrieving top {top_k} documents for query: {query[:50]}...")

            # 向量化查询
            query_embedding = self.embedding_handler.embed_query(query)

            # 在 ChromaDB 中搜索
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )

            logger.debug(f"Retrieved {len(results['documents'][0])} documents")

            return {
                "ids": results.get("ids", [[]])[0],
                "documents": results.get("documents", [[]])[0],
                "metadatas": results.get("metadatas", [[]])[0],
                "distances": results.get("distances", [[]])[0],
            }

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
            self.collection.delete(ids=[doc_id])
            logger.info(f"Document deleted. Collection now contains {self.collection.count()} documents")
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise

    def clear_collection(self) -> None:
        """清空整个集合"""
        try:
            logger.warning("Clearing entire collection")
            # 获取所有文档 ID
            all_docs = self.collection.get()
            if all_docs and all_docs["ids"]:
                self.collection.delete(ids=all_docs["ids"])
            logger.info("Collection cleared")
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            raise

    def get_document_count(self) -> int:
        """获取知识库中的文档数量"""
        try:
            count = self.collection.count()
            logger.debug(f"Knowledge base contains {count} documents")
            return count
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return 0

    def get_all_documents(self) -> Dict:
        """获取知识库中的所有文档"""
        try:
            results = self.collection.get(include=["documents", "metadatas"])
            return {
                "ids": results.get("ids", []),
                "documents": results.get("documents", []),
                "metadatas": results.get("metadatas", []),
            }
        except Exception as e:
            logger.error(f"Error getting all documents: {str(e)}")
            raise
