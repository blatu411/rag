"""
DeepSeek AI 对话助手 + RAG 知识库 - Streamlit 应用
阶段 1 + 阶段 2 完整版本
"""
import streamlit as st
from datetime import datetime
import os
from loguru import logger

from src.deepseek_client import DeepSeekClient
from src.embedding_handler import BGEEmbeddingHandler
from src.memory_kb_handler import MemoryKBHandler
from src.document_processor import DocumentProcessor
from src.rag_service import RAGService
from config import settings

# 配置日志
logger.add(
    settings.LOGS_DIR / "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level=settings.LOG_LEVEL,
)

# 页面配置
st.set_page_config(
    page_title="DeepSeek AI Chat + RAG",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义 CSS
st.markdown(
    """
    <style>
    .main {
        max-width: 1200px;
    }
    .stTabs [data-baseweb="tab-list"] button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_session_state():
    """初始化 session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "deepseek_client" not in st.session_state:
        try:
            st.session_state.deepseek_client = DeepSeekClient()
        except ValueError as e:
            st.session_state.deepseek_client = None
            st.session_state.api_error = str(e)

    if "embedding_handler" not in st.session_state:
        try:
            logger.info("Loading BGE embedding model...")
            st.session_state.embedding_handler = BGEEmbeddingHandler()
            logger.info("BGE model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load BGE model: {str(e)}")
            st.session_state.embedding_handler = None
            st.session_state.embedding_error = str(e)

    if "kb_handler" not in st.session_state:
        try:
            if st.session_state.get("embedding_handler"):
                st.session_state.kb_handler = MemoryKBHandler(
                    st.session_state.embedding_handler
                )
            else:
                st.session_state.kb_handler = None
        except Exception as e:
            logger.error(f"Failed to initialize Knowledge Base: {str(e)}")
            st.session_state.kb_handler = None

    if "rag_service" not in st.session_state:
        try:
            if (
                st.session_state.get("embedding_handler")
                and st.session_state.get("kb_handler")
                and st.session_state.get("deepseek_client")
            ):
                st.session_state.rag_service = RAGService(
                    st.session_state.embedding_handler,
                    st.session_state.kb_handler,
                    st.session_state.deepseek_client,
                    top_k=5,
                )
            else:
                st.session_state.rag_service = None
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}")
            st.session_state.rag_service = None

    if "document_processor" not in st.session_state:
        try:
            st.session_state.document_processor = DocumentProcessor(
                chunk_size=800, chunk_overlap=100
            )
        except Exception as e:
            logger.error(f"Failed to initialize document processor: {str(e)}")
            st.session_state.document_processor = None


def display_chat_history():
    """显示聊天历史"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(user_input: str, use_rag: bool):
    """处理用户输入"""
    # 添加用户消息到历史
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat(),
        }
    )

    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(user_input)

    # 处理 AI 响应
    if st.session_state.deepseek_client is None:
        st.error("❌ API 配置错误，请检查 .env 文件")
        return

    # 显示 AI 响应（流式）
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # 构建消息列表
            messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.messages[:-1]
            ]
            messages.append({"role": "user", "content": user_input})

            # 获取响应
            if use_rag and st.session_state.get("rag_service"):
                logger.info(f"Using RAG for query: {user_input[:50]}...")
                response_generator = st.session_state.rag_service.generate_response_with_rag(
                    user_input,
                    messages[:-1],
                    use_rag=True,
                    temperature=st.session_state.get("temperature", 0.7),
                    max_tokens=st.session_state.get("max_tokens", 2048),
                )
            else:
                logger.info(f"Using standard chat for query: {user_input[:50]}...")
                response_generator = st.session_state.deepseek_client.chat_stream(
                    messages=messages,
                    temperature=st.session_state.get("temperature", 0.7),
                    max_tokens=st.session_state.get("max_tokens", 2048),
                )

            # 流式显示响应
            for chunk in response_generator:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

            # 移除光标
            message_placeholder.markdown(full_response)

            # 添加 AI 消息到历史
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.info(f"Response generated, estimated tokens: {st.session_state.deepseek_client.count_tokens_estimate(full_response)}")

        except Exception as e:
            error_msg = f"❌ 发生错误: {str(e)}"
            message_placeholder.error(error_msg)
            logger.error(f"Error generating response: {str(e)}")


def upload_documents_to_knowledge_base(uploaded_files):
    """上传文档到知识库"""
    if not uploaded_files:
        return

    if not st.session_state.get("rag_service"):
        st.error("❌ RAG 服务未初始化")
        return

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        all_chunks = []
        all_metadata = []

        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"处理文件 {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")

            # 保存临时文件
            temp_path = settings.DATA_DIR / "temp" / uploaded_file.name
            temp_path.parent.mkdir(parents=True, exist_ok=True)

            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 处理文档
            chunks, metadata = st.session_state.document_processor.process_file(str(temp_path))

            # 添加源文件名到元数据
            for m in metadata:
                m["filename"] = uploaded_file.name

            all_chunks.extend(chunks)
            all_metadata.extend([{**m, "chunk_index": i} for i, _ in enumerate(chunks)])

            # 删除临时文件
            os.remove(temp_path)

            progress_bar.progress((idx + 1) / len(uploaded_files))

        # 添加到知识库
        if all_chunks:
            status_text.text(f"添加 {len(all_chunks)} 个文本块到知识库...")
            st.session_state.rag_service.add_documents(all_chunks, all_metadata)
            status_text.text(f"✅ 成功添加 {len(all_chunks)} 个文本块")
            logger.info(f"Successfully added {len(all_chunks)} chunks to knowledge base")
        else:
            status_text.text("❌ 未能从文件中提取内容")

    except Exception as e:
        status_text.error(f"❌ 错误: {str(e)}")
        logger.error(f"Error uploading documents: {str(e)}")


def main():
    """主函数"""
    initialize_session_state()

    # 页面标题
    st.title("💬 DeepSeek AI 对话助手 + RAG 知识库")
    st.markdown("基于 DeepSeek API 和 RAG 的 AI 对话应用 | 阶段 1 + 阶段 2")

    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 应用设置")

        # API 状态
        if st.session_state.deepseek_client is not None:
            st.success("✅ DeepSeek API 已连接")
            st.caption(f"模型: {st.session_state.deepseek_client.model}")
        else:
            st.error("❌ DeepSeek API 未连接")

        # RAG 状态
        if st.session_state.get("rag_service"):
            st.success("✅ RAG 服务已就绪")
            kb_info = st.session_state.rag_service.get_knowledge_base_info()
            st.caption(f"知识库文档数: {kb_info['document_count']}")
        else:
            st.warning("⚠️ RAG 服务未初始化")

        st.divider()

        # 对话参数
        st.subheader("💭 对话参数")
        st.session_state.temperature = st.slider(
            "温度 (Temperature)",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="更高的温度会导致更多的创意响应",
        )

        st.session_state.max_tokens = st.slider(
            "最大 Token 数",
            min_value=256,
            max_value=4096,
            value=2048,
            step=256,
        )

        # RAG 开关
        st.divider()
        st.subheader("🔍 RAG 知识库")
        use_rag = st.toggle(
            "启用 RAG 知识库",
            value=True,
            help="启用后将使用知识库中的文档来增强 AI 回复",
        )

        st.session_state.use_rag = use_rag

        st.divider()

        # 对话管理
        st.subheader("📋 对话管理")
        col1, col2 = st.columns(2)

        with col1:
            message_count = len([m for m in st.session_state.messages if m["role"] == "user"])
            st.metric("消息数量", message_count)

        with col2:
            if st.session_state.get("deepseek_client"):
                total_tokens = st.session_state.deepseek_client.count_messages_tokens(
                    [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                )
                st.metric("估计 Token", total_tokens)

        if st.button("🗑️ 清空对话历史", use_container_width=True):
            st.session_state.messages = []
            st.success("✅ 对话历史已清空")
            st.rerun()

    # 主区域使用 Tab
    tab1, tab2 = st.tabs(["💬 对话", "📚 知识库管理"])

    # Tab 1: 对话
    with tab1:
        # 显示对话历史
        display_chat_history()

        # 用户输入
        if user_input := st.chat_input(
            "输入你的问题... (按 Enter 发送)",
            key="chat_input",
        ):
            handle_user_input(user_input, use_rag=st.session_state.get("use_rag", True))

    # Tab 2: 知识库管理
    with tab2:
        st.subheader("📚 知识库管理")

        if not st.session_state.get("rag_service"):
            st.error("❌ RAG 服务未初始化，无法管理知识库")
        else:
            # 知识库信息
            kb_info = st.session_state.rag_service.get_knowledge_base_info()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("文档数量", kb_info["document_count"])
            with col2:
                st.metric("检索 Top-K", kb_info["top_k"])
            with col3:
                st.metric("状态", kb_info["status"])

            st.divider()

            # 上传文档
            st.subheader("📄 上传文档")
            uploaded_files = st.file_uploader(
                "选择文件（支持 PDF、Word、TXT）",
                accept_multiple_files=True,
                type=["pdf", "docx", "doc", "txt"],
                help="支持的格式: PDF, Word (.docx, .doc), Text (.txt)",
            )

            if st.button("添加到知识库", use_container_width=True):
                if uploaded_files:
                    upload_documents_to_knowledge_base(uploaded_files)
                else:
                    st.warning("请先选择文件")

            st.divider()

            # 清空知识库
            st.subheader("⚠️ 危险操作")
            if st.button("🗑️ 清空知识库", use_container_width=True, type="secondary"):
                try:
                    st.session_state.rag_service.clear_knowledge_base()
                    st.success("✅ 知识库已清空")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 错误: {str(e)}")

    # 底部信息
    st.divider()
    st.caption(
        f"版本: 0.2.0 | 阶段 1 + 阶段 2 | 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    main()
