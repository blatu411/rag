# DeepSeek AI 对话助手 + RAG 知识库

一个基于 Python + Streamlit 的 DeepSeek AI 对话应用，支持流式对话和 RAG 知识库集成。

## 📋 项目特性

### 阶段 1 - 基础对话功能（已完成）
✅ Streamlit Web 界面
✅ DeepSeek API 集成
✅ 流式实时回复
✅ 完整对话历史管理
✅ Token 估算
✅ 对话参数调整

### 阶段 2 - RAG 知识库（开发中）
⏳ ChromaDB 向量数据库
⏳ BGE-Small-zh-v1.5 向量模型
⏳ 文档上传和处理
⏳ 相似度检索
⏳ 知识库增强对话

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip

### 1. 克隆项目
```bash
git clone <repo-url>
cd rag
```

### 2. 创建虚拟环境（推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的 DeepSeek API Key
# DEEPSEEK_API_KEY=your_api_key_here
```

**获取 DeepSeek API Key：**
1. 访问 [DeepSeek 官网](https://www.deepseek.com/)
2. 注册账号
3. 获取 API Key
4. 粘贴到 .env 文件

### 5. 运行应用
```bash
streamlit run app.py
```

应用会自动打开：`http://localhost:8501`

## 📁 项目结构

```
deepseek-web-app/
├── app.py                    # Streamlit 主应用入口
├── config.py                 # 配置管理
├── requirements.txt          # Python 依赖
├── .env.example              # 环境变量示例
├── .gitignore
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── deepseek_client.py    # DeepSeek API 客户端
│   ├── embedding_handler.py  # BGE 向量化（阶段2）
│   ├── chroma_handler.py     # ChromaDB 管理（阶段2）
│   ├── document_processor.py # 文档处理（阶段2）
│   ├── rag_service.py        # RAG 服务（阶段2）
│   └── utils.py              # 工具函数
│
├── data/
│   ├── chroma_db/            # ChromaDB 数据库（阶段2）
│   ├── documents/            # 用户文档（阶段2）
│   └── cache/                # 模型缓存（阶段2）
│
├── logs/
│   └── app.log               # 应用日志
│
└── prompts/
    └── system_prompts.py     # 系统提示词（阶段2）
```

## 🎯 使用说明

### 基础对话（阶段1）

1. **输入问题**：在下方输入框输入你的问题
2. **发送消息**：点击发送或按 Enter 键
3. **实时回复**：AI 会流式返回回复，可以看到打字过程
4. **多轮对话**：支持完整的对话历史

### 侧边栏功能

- **💭 对话参数**
  - 温度 (Temperature)：控制回复的创意程度
  - 最大 Token 数：限制回复长度

- **📋 对话管理**
  - 消息数量统计
  - Token 估计
  - 清空对话历史

- **📖 使用说明**：应用内帮助文档

## 🔧 配置说明

### config.py

所有配置都在 `config.py` 中管理，从 `.env` 文件自动加载：

```python
DEEPSEEK_API_KEY      # DeepSeek API 密钥（必需）
DEEPSEEK_BASE_URL     # API 基础 URL
DEEPSEEK_MODEL        # 使用的模型名称
MAX_CHAT_HISTORY      # 保留最近的对话数
LOG_LEVEL             # 日志级别
DEBUG_MODE            # 调试模式
```

## 📊 API 配额和成本

DeepSeek API 计费基于 token 数量。应用会估算每次对话的 token 使用量。

**Token 估算规则：**
- 输入文本：约 1 token/4 字符
- 每条消息：额外 4 token 开销
- 完整估算显示在侧边栏

## 🐛 常见问题

### 1. "API 配置错误" 错误
**解决方案：**
- 检查 `.env` 文件是否存在
- 确认 `DEEPSEEK_API_KEY` 已正确填入
- API Key 是否有效且未过期

### 2. 流式输出很慢
**解决方案：**
- 检查网络连接
- 降低 `max_tokens` 参数
- 确认 DeepSeek 服务状态

### 3. 对话历史丢失
**说明：**
- 当前阶段对话仅保存在内存中
- 刷新页面或重启应用会丢失历史
- 后续版本可添加数据库持久化

## 📈 后续开发计划

### 阶段 2：RAG 知识库（预计2周）
- [ ] ChromaDB 集成
- [ ] BGE 向量模型集成
- [ ] 文档上传和处理
- [ ] 知识库管理 UI
- [ ] RAG 融合对话

### 阶段 3：优化和增强（预计1周）
- [ ] 性能优化
- [ ] 数据持久化
- [ ] 更多文档格式支持
- [ ] UI 美化

## 📝 版本历史

### v0.1.0 (2024-12-25)
- 初始发布
- 基础对话功能
- Streamlit UI
- DeepSeek API 集成

## 📜 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，欢迎通过以下方式联系：
- 提交 Issue
- 发送邮件

---

**开发工具：** Claude Code + Streamlit + DeepSeek API