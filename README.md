# DeepSeek AI Chat + RAG 知识库应用

一个集成了 DeepSeek AI API 和 RAG（检索增强生成）功能的 Streamlit 应用，支持中文对话和知识库文档管理。

## 功能概述

### 阶段 1 - 基础聊天功能
- ✅ DeepSeek API 集成（OpenAI 兼容接口）
- ✅ 流式响应显示（实时 Token 输出）
- ✅ 对话历史管理
- ✅ 参数调整（温度、最大 Token 数）

### 阶段 2 - RAG 知识库集成
- ✅ 多格式文档支持（PDF、Word、TXT）
- ✅ 智能文本分块（基于中文标点符号）
- ✅ BGE-Small-zh-v1.5 中文向量化
- ✅ 内存知识库存储（无数据库依赖）
- ✅ 相似度检索（余弦相似度）
- ✅ RAG 增强回复（动态注入文档上下文）

## 技术栈

- **前端框架**: Streamlit 1.28+
- **LLM 模型**: DeepSeek API
- **向量化模型**: BGE-Small-zh-v1.5 (384-dim)
- **向量存储**: 内存式 MemoryKBHandler
- **文本处理**: LangChain RecursiveCharacterTextSplitter
- **文档格式**: PyPDF2 (PDF), python-docx (Word), 原生 (TXT)
- **相似度计算**: scikit-learn cosine_similarity

## 快速开始

### 1. 环境配置

创建 `.env` 文件：
```ini
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
HTTP_PROXY=http://127.0.0.1:10808
HTTPS_PROXY=http://127.0.0.1:10808
LOG_LEVEL=INFO
```

### 2. 安装依赖

```bash
pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

### 3. 启动应用

**Windows**:
```bash
run.bat
```

**Linux/macOS**:
```bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
python -m streamlit run app.py
```

应用将在 `http://localhost:8501` 启动

## 使用指南

### 对话标签页（💬 对话）
- 在底部输入框输入问题，按 Enter 发送
- 启用/禁用 RAG 知识库增强（侧边栏开关）
- 调整参数：温度、最大 Token 数

### 知识库管理标签页（📚 知识库管理）
- 上传文档：选择或拖拽 PDF/Word/TXT 文件
- 查看统计：文档数量、检索数量、状态
- 清空知识库：清除所有文档

## 工作流程

```
用户问题 → BGE 向量化 → 计算相似度 → 检索 Top-K 文档
                                       ↓
                              构建增强消息列表
                                       ↓
                              DeepSeek API 调用
                                       ↓
                           实时流式显示 Token
                                       ↓
                              保存回复到历史
```

## 文件结构

```
D:\projects\rag\
├── app.py                          # 主应用 (Streamlit UI)
├── config.py                       # 配置管理
├── requirements.txt                # 依赖列表
├── run.bat                         # Windows 启动脚本
├── README.md                       # 本文档
├── .env                           # 环境变量
├── logs/
│   └── app.log
├── data/
│   └── temp/
└── src/
    ├── deepseek_client.py        # DeepSeek API 客户端
    ├── embedding_handler.py      # BGE 向量化
    ├── document_processor.py     # 文档处理
    ├── memory_kb_handler.py      # 内存知识库
    └── rag_service.py            # RAG 服务
```

## 常见问题

| 问题 | 解决方案 |
|------|--------|
| API 连接失败 | 检查 .env 文件，配置代理（如需要） |
| BGE 模型加载慢 | 首次需下载 ~350MB，请耐心等待 |
| 上传文档失败 | 检查文件格式，查看 logs/app.log |
| RAG 效果不好 | 确保文档相关，尝试调整参数 |
| 重启后知识库清空 | 正常行为（内存式存储），后续可考虑持久化 |

## 性能指标

- 应用启动：8-10 秒
- 向量化：~1000 字/秒
- 检索：<100ms
- API 响应：3-10 秒/完整回复

## 已知限制

1. 大量文档（>10000）可能占用内存
2. 针对中文优化
3. 应用重启后知识库清空
4. 受 DeepSeek API 上下文限制

---

**版本**: 0.2.0 | **状态**: ✅ 生产就绪 | **最后更新**: 2025-12-25
