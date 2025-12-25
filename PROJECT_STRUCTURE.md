# 📁 项目结构和文件说明

## 项目树形结构

```
deepseek-web-app/
├── app.py                       # ⭐ Streamlit 主应用入口
├── config.py                    # ⭐ 配置管理模块
├── requirements.txt             # ⭐ Python 依赖列表
├── .env.example                 # ⭐ 环境变量示例
├── .gitignore                   # Git 忽略配置
├── README.md                    # 项目文档
├── QUICKSTART.md                # 快速启动指南
├── PROJECT_STRUCTURE.md         # 本文件
│
├── src/                         # 源代码目录
│   ├── __init__.py              # Python 包初始化
│   ├── deepseek_client.py       # ⭐ DeepSeek API 客户端
│   ├── embedding_handler.py     # BGE 向量化处理（阶段2）
│   ├── chroma_handler.py        # ChromaDB 知识库（阶段2）
│   ├── document_processor.py    # 文档处理（阶段2）
│   ├── rag_service.py           # RAG 融合服务（阶段2）
│   └── utils.py                 # 工具函数
│
├── data/                        # 数据目录（运行时创建）
│   ├── chroma_db/               # ChromaDB 存储（阶段2）
│   ├── documents/               # 用户文档（阶段2）
│   └── cache/                   # 模型缓存（阶段2）
│
├── logs/                        # 日志目录（运行时创建）
│   └── app.log                  # 应用日志
│
├── prompts/                     # 提示词目录（阶段2计划）
│   └── system_prompts.py        # 系统提示词模板
│
└── .git/                        # Git 版本控制
```

## 文件详细说明

### 🔴 阶段 1 - 已实现

#### `app.py` - Streamlit 主应用
**文件大小：** ~6.5 KB
**行数：** ~220 行
**功能：**
- Streamlit Web UI 界面
- 聊天界面和消息展示
- 侧边栏设置和管理
- 流式响应处理
- 对话历史管理
- 日志记录

**关键类/函数：**
- `initialize_session_state()` - 初始化会话状态
- `display_chat_history()` - 显示聊天历史
- `handle_user_input()` - 处理用户输入
- `main()` - 主函数

**依赖：**
- streamlit
- loguru
- DeepSeekClient

---

#### `config.py` - 配置管理
**文件大小：** ~1.5 KB
**行数：** ~45 行
**功能：**
- 环境变量加载和管理
- 配置验证（使用 Pydantic）
- 项目路径设置
- 日志配置

**关键类：**
- `Settings` - 使用 Pydantic 的配置类

**使用方式：**
```python
from config import settings

# 访问配置
api_key = settings.DEEPSEEK_API_KEY
model = settings.DEEPSEEK_MODEL
log_level = settings.LOG_LEVEL
```

---

#### `src/deepseek_client.py` - API 客户端
**文件大小：** ~3 KB
**行数：** ~110 行
**功能：**
- DeepSeek API 的 Python 封装
- 同步对话（非流式）
- 异步对话（流式）
- Token 估算功能
- 错误处理和日志

**关键类：**
- `DeepSeekClient` - API 客户端类

**关键方法：**
- `__init__()` - 初始化客户端
- `chat()` - 同步对话
- `chat_stream()` - 流式对话（返回 Generator）
- `count_tokens_estimate()` - 估算 token 数
- `count_messages_tokens()` - 估算消息列表的 token 数

**使用示例：**
```python
from src.deepseek_client import DeepSeekClient

# 初始化客户端
client = DeepSeekClient()

# 流式对话
messages = [{"role": "user", "content": "你好"}]
for chunk in client.chat_stream(messages):
    print(chunk, end="", flush=True)

# 同步对话
response = client.chat(messages)
print(response)

# 估算 token
tokens = client.count_tokens_estimate("Hello world")
```

---

#### `requirements.txt` - 依赖管理
**内容：**
```
streamlit>=1.28.0              # Web 框架
openai>=1.3.0                  # DeepSeek API（兼容 OpenAI 格式）
python-dotenv>=1.0.0           # 环境变量
requests>=2.31.0               # HTTP 请求
pydantic>=2.0.0                # 数据验证
loguru>=0.7.0                  # 日志记录
```

**安装方式：**
```bash
pip install -r requirements.txt
```

---

#### `.env.example` - 环境变量示例
**内容示例：**
```ini
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
MAX_CHAT_HISTORY=20
LOG_LEVEL=INFO
DEBUG_MODE=False
```

**使用方式：**
1. 复制：`cp .env.example .env`
2. 编辑：填入你的实际配置
3. 应用：自动由 `config.py` 加载

---

### 🟡 阶段 2 - 规划中（RAG 知识库）

#### `src/embedding_handler.py` - BGE 向量化（待开发）
**计划功能：**
- 加载 BGE-Small-zh-v1.5 模型
- 单文本向量化
- 批量向量化
- GPU/CPU 自动选择
- 模型缓存管理

**计划接口：**
```python
class BGEEmbeddingHandler:
    def __init__(self)
    def embed_texts(self, texts: List[str]) -> np.ndarray
    def embed_query(self, query: str) -> np.ndarray
```

---

#### `src/chroma_handler.py` - ChromaDB 管理（待开发）
**计划功能：**
- ChromaDB 初始化
- 文档添加/删除/更新
- 相似度检索
- 知识库持久化

**计划接口：**
```python
class ChromaHandler:
    def __init__(self, embedding_handler)
    def add_documents(self, documents: List[str], metadata: List[dict])
    def retrieve(self, query: str, top_k: int) -> List[dict]
    def delete(self, ids: List[str])
```

---

#### `src/document_processor.py` - 文档处理（待开发）
**计划功能：**
- PDF/Word/TXT 加载
- 文本分割（中文友好）
- 元数据提取
- 多种编码支持

**计划接口：**
```python
class DocumentProcessor:
    def __init__(self, chunk_size: int, chunk_overlap: int)
    def load_document(self, file_path: str) -> str
    def split_text(self, text: str) -> List[str]
```

---

#### `src/rag_service.py` - RAG 融合服务（待开发）
**计划功能：**
- 整合 RAG 工作流
- 融合检索结果和对话
- 提示词工程
- 流式 RAG 对话

**计划接口：**
```python
class RAGService:
    def __init__(self, embedding_handler, chroma_handler, deepseek_client)
    def generate_response_with_rag(
        self,
        user_query: str,
        chat_history: List[dict],
        use_rag: bool = True
    ) -> Iterator[str]
```

---

#### `prompts/system_prompts.py` - 系统提示词（待开发）
**计划内容：**
- 基础对话提示词
- RAG 模式提示词
- 各种场景的定制提示词

---

### 📁 数据目录结构（运行时创建）

#### `data/chroma_db/` - 向量数据库（阶段2）
```
data/chroma_db/
├── chroma.db              # 元数据数据库
├── embeddings/            # 向量存储
└── ...
```

#### `data/documents/` - 用户文档（阶段2）
```
data/documents/
├── pdf/                   # PDF 文件
├── docx/                  # Word 文件
└── txt/                   # 文本文件
```

#### `data/cache/` - 模型缓存（阶段2）
```
data/cache/
└── BAAI_bge-small-zh-v1.5/  # BGE 模型缓存
```

---

### 📋 日志目录结构

#### `logs/app.log` - 应用日志
```
2024-12-25 10:30:45 | INFO     | DeepSeek client initialized with model: deepseek-chat
2024-12-25 10:30:46 | INFO     | Generated response, tokens estimate: 125
2024-12-25 10:30:47 | ERROR    | Error in chat: Connection timeout
```

---

## 文件大小汇总

| 文件 | 大小 | 行数 | 状态 |
|------|------|------|------|
| app.py | ~6.5 KB | ~220 | ✅ 完成 |
| config.py | ~1.5 KB | ~45 | ✅ 完成 |
| src/deepseek_client.py | ~3 KB | ~110 | ✅ 完成 |
| requirements.txt | ~0.3 KB | 7 | ✅ 完成 |
| .env.example | ~0.2 KB | 7 | ✅ 完成 |
| README.md | ~10 KB | ~250 | ✅ 完成 |
| QUICKSTART.md | ~4 KB | ~120 | ✅ 完成 |
| **总计** | **~25.5 KB** | **~759** | **阶段1** |

---

## 代码统计

### 阶段 1 完成度
- ✅ 项目初始化：100%
- ✅ 配置管理：100%
- ✅ API 客户端：100%
- ✅ Streamlit UI：100%
- ✅ 文档编写：100%

### 总行数（阶段1）
- Python 代码：~375 行
- 配置和初始化：~52 行
- 文档：~700+ 行
- **总计：**~1127 行

---

## 导入依赖关系

```
app.py
  ├─ streamlit
  ├─ datetime
  ├─ loguru
  ├─ src.deepseek_client (DeepSeekClient)
  └─ config (settings)

config.py
  ├─ os
  ├─ pathlib (Path)
  ├─ dotenv (load_dotenv)
  └─ pydantic (BaseSettings)

src/deepseek_client.py
  ├─ typing
  ├─ openai (OpenAI)
  ├─ loguru (logger)
  └─ config (settings)

src/__init__.py
  └─ (no imports)
```

---

## 开发建议

### 添加新的源文件
1. 在 `src/` 目录中创建新文件
2. 添加合适的头部注释
3. 实现主要类/函数
4. 在 `src/__init__.py` 中添加导出（可选）
5. 更新本文档

### 修改配置
1. 在 `.env` 文件中修改值
2. 重启应用以加载新配置
3. 或在 `config.py` 中修改默认值

### 添加日志
```python
from loguru import logger

logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
logger.debug("Debug message")
```

### 调试应用
1. 设置 `DEBUG_MODE=True` 在 `.env`
2. 查看 `logs/app.log` 了解详情
3. 使用 Streamlit 的调试工具

---

## 下一步计划

### 阶段 2（RAG 知识库）文件列表
- [ ] `src/embedding_handler.py` - BGE 向量化
- [ ] `src/chroma_handler.py` - ChromaDB 管理
- [ ] `src/document_processor.py` - 文档处理
- [ ] `src/rag_service.py` - RAG 融合
- [ ] `src/utils.py` - 工具函数
- [ ] `prompts/system_prompts.py` - 提示词模板
- [ ] 更新 `requirements.txt` 添加新依赖
- [ ] 更新 `app.py` 添加 RAG UI

**预计完成时间：** 1-2 周

---

**本文档最后更新于：2024-12-25**
