"""
RAG 融合服务模块
整合所有 RAG 组件，提供统一的接口
"""
from typing import Iterator, List, Dict, Optional
from loguru import logger


class RAGService:
    """RAG 融合服务"""

    def __init__(
        self,
        embedding_handler,
        chroma_handler,
        deepseek_client,
        top_k: int = 5,
    ):
        """
        初始化 RAG 服务

        Args:
            embedding_handler: BGE 向量化处理器
            chroma_handler: ChromaDB 知识库管理器
            deepseek_client: DeepSeek API 客户端
            top_k: 检索的文档数量
        """
        self.embedding_handler = embedding_handler
        self.chroma_handler = chroma_handler
        self.deepseek_client = deepseek_client
        self.top_k = top_k

        logger.info("RAG Service initialized")

    def generate_response_with_rag(
        self,
        user_query: str,
        chat_history: List[Dict[str, str]],
        use_rag: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Iterator[str]:
        """
        使用 RAG 生成响应

        Args:
            user_query: 用户问题
            chat_history: 聊天历史（不包括当前问题）
            use_rag: 是否使用 RAG 增强
            temperature: 温度参数
            max_tokens: 最大 token 数

        Yields:
            AI 回复的文本块
        """
        try:
            # 第一步：检索相关文档（如果启用 RAG）
            context = ""
            if use_rag:
                context = self._retrieve_context(user_query)
                logger.debug(f"Retrieved context for query: {user_query[:50]}...")

            # 第二步：构建增强的消息列表
            messages = self._build_enhanced_messages(user_query, chat_history, context)

            # 第三步：调用 DeepSeek API 获取流式响应
            logger.debug(f"Calling DeepSeek API with {len(messages)} messages")
            yield from self.deepseek_client.chat_stream(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        except Exception as e:
            logger.error(f"Error in generate_response_with_rag: {str(e)}")
            raise

    def _retrieve_context(self, query: str) -> str:
        """
        检索相关文档作为上下文

        Args:
            query: 查询文本

        Returns:
            格式化的上下文字符串
        """
        try:
            # 检查知识库是否为空
            doc_count = self.chroma_handler.get_document_count()
            if doc_count == 0:
                logger.debug("Knowledge base is empty, skipping retrieval")
                return ""

            # 检索相关文档
            results = self.chroma_handler.retrieve(query, top_k=self.top_k)

            if not results["documents"]:
                logger.debug("No relevant documents found")
                return ""

            # 格式化上下文
            context_parts = ["以下是相关的参考文档：\n"]
            for i, (doc, distance) in enumerate(
                zip(results["documents"], results["distances"]), 1
            ):
                # distance 越小，相关性越高
                relevance = max(0, 1 - distance)
                context_parts.append(f"\n【文档 {i}】（相关度: {relevance:.2%}）\n{doc}\n")

            context = "".join(context_parts)
            logger.debug(f"Context retrieved with {len(results['documents'])} documents")
            return context

        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return ""

    def _build_enhanced_messages(
        self,
        user_query: str,
        chat_history: List[Dict[str, str]],
        context: str,
    ) -> List[Dict[str, str]]:
        """
        构建融合 RAG 上下文的消息列表

        Args:
            user_query: 用户问题
            chat_history: 聊天历史
            context: RAG 上下文

        Returns:
            消息列表
        """
        # 系统提示词
        system_prompt = self._get_system_prompt(context)

        messages = [{"role": "system", "content": system_prompt}]

        # 添加聊天历史
        messages.extend(chat_history)

        # 添加当前问题
        messages.append({"role": "user", "content": user_query})

        return messages

    def _get_system_prompt(self, context: str) -> str:
        """
        获取系统提示词

        Args:
            context: RAG 上下文

        Returns:
            系统提示词
        """
        base_prompt = """你是一个有帮助的 AI 助手。你的任务是根据用户的问题提供准确、有用的回答。

如果用户的问题与特定主题相关，你可以参考下面提供的参考文档。请根据这些文档提供答案，但也可以使用你的通用知识。

当使用参考文档时，请清楚地表明你是从哪些文档中获取信息的。

如果参考文档中没有相关信息，请使用你的通用知识回答。"""

        if context and context.strip():
            return f"""{base_prompt}

{context}

请基于上述信息以及你的知识回答用户的问题。"""
        else:
            return base_prompt

    def add_documents(self, documents: List[str], metadata: List[Dict] = None) -> None:
        """
        添加文档到知识库

        Args:
            documents: 文档列表
            metadata: 元数据列表（可选）
        """
        try:
            logger.info(f"Adding {len(documents)} documents to knowledge base")
            self.chroma_handler.add_documents(documents, metadata)
            logger.info(f"Successfully added {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def get_knowledge_base_info(self) -> Dict:
        """
        获取知识库信息

        Returns:
            包含知识库统计的字典
        """
        try:
            count = self.chroma_handler.get_document_count()
            return {
                "document_count": count,
                "top_k": self.top_k,
                "status": "ready" if count > 0 else "empty",
            }
        except Exception as e:
            logger.error(f"Error getting knowledge base info: {str(e)}")
            return {
                "document_count": 0,
                "top_k": self.top_k,
                "status": "error",
            }

    def clear_knowledge_base(self) -> None:
        """清空知识库"""
        try:
            logger.warning("Clearing knowledge base")
            self.chroma_handler.clear_collection()
            logger.info("Knowledge base cleared")
        except Exception as e:
            logger.error(f"Error clearing knowledge base: {str(e)}")
            raise
