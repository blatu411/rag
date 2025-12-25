"""
DeepSeek AI 对话助手 - Streamlit 应用
"""
import streamlit as st
from datetime import datetime
from loguru import logger
from src.deepseek_client import DeepSeekClient
from config import settings

# 配置日志
logger.add(
    settings.LOGS_DIR / "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    level=settings.LOG_LEVEL,
)

# 页面配置
st.set_page_config(
    page_title="DeepSeek AI Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义 CSS
st.markdown(
    """
    <style>
    .main {
        max-width: 1000px;
        margin: 0 auto;
    }

    .stChatMessage {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }

    .user-message {
        background-color: #e3f2fd;
    }

    .assistant-message {
        background-color: #f5f5f5;
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


def display_chat_history():
    """显示聊天历史"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(user_input: str):
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
            # 构建消息列表（只包含内容，不包含时间戳）
            messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.messages[:-1]  # 排除当前用户消息
            ]
            messages.append({"role": "user", "content": user_input})

            # 流式获取响应
            for chunk in st.session_state.deepseek_client.chat_stream(
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
            ):
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

            logger.info(f"Generated response, tokens estimate: {st.session_state.deepseek_client.count_tokens_estimate(full_response)}")

        except Exception as e:
            error_msg = f"❌ 发生错误: {str(e)}"
            message_placeholder.error(error_msg)
            logger.error(f"Error generating response: {str(e)}")


def main():
    """主函数"""
    # 初始化 session state
    initialize_session_state()

    # 页面标题
    st.title("💬 DeepSeek AI 对话助手")
    st.markdown("基于 DeepSeek API 的 AI 对话应用 | 阶段 1 - 基础对话")

    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 应用设置")

        # 显示 API 状态
        if st.session_state.deepseek_client is not None:
            st.success("✅ API 已连接")
            st.caption(f"模型: {st.session_state.deepseek_client.model}")
        else:
            st.error("❌ API 未连接")
            if hasattr(st.session_state, "api_error"):
                st.caption(st.session_state.api_error)

        st.divider()

        # 对话设置
        st.subheader("💭 对话参数")
        temperature = st.slider(
            "温度 (Temperature)",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="更高的温度会导致更多的创意响应，但可能不够准确",
        )

        max_tokens = st.slider(
            "最大 Token 数",
            min_value=256,
            max_value=4096,
            value=2048,
            step=256,
            help="限制 AI 响应的长度",
        )

        st.divider()

        # 对话管理
        st.subheader("📋 对话管理")
        col1, col2 = st.columns(2)

        with col1:
            message_count = len(
                [m for m in st.session_state.messages if m["role"] == "user"]
            )
            st.metric("消息数量", message_count)

        with col2:
            total_tokens = st.session_state.deepseek_client.count_messages_tokens(
                [{"role": m["role"], "content": m["content"]}
                 for m in st.session_state.messages]
            ) if st.session_state.deepseek_client else 0
            st.metric("估计 Token", total_tokens)

        if st.button("🗑️ 清空对话历史", use_container_width=True):
            st.session_state.messages = []
            st.success("✅ 对话历史已清空")
            st.rerun()

        st.divider()

        # 帮助信息
        st.subheader("📖 使用说明")
        st.markdown(
            """
        1. 在下方输入框输入你的问题
        2. 点击发送或按 Enter 键
        3. AI 会流式返回回复
        4. 支持多轮对话
        5. 使用左侧菜单管理设置

        **技术特点：**
        - 使用 DeepSeek API
        - Streamlit 实时流式输出
        - 完整的对话历史记录
        - 对话内容本地存储
        """
        )

    # 主区域
    col1, col2 = st.columns([1, 0.3])
    with col1:
        st.subheader("💬 对话")
    with col2:
        if st.button("↻", help="刷新"):
            st.rerun()

    # 显示对话历史
    display_chat_history()

    # 输入框
    if user_input := st.chat_input(
        "输入你的问题... (按 Ctrl+Enter 发送)",
        key="chat_input",
    ):
        handle_user_input(user_input)

    # 底部信息
    st.divider()
    st.caption(
        f"版本: 0.1.0 | 阶段 1 - 基础对话功能 | 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    main()
