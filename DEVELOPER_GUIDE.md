# 👨‍💻 开发者指南

## 代码风格和规范

### Python 风格指南
项目遵循 PEP 8 规范：

```python
# ✅ 好的实践

class DeepSeekClient:
    """DeepSeek API 客户端"""

    def __init__(self, api_key: str):
        """初始化客户端"""
        self.api_key = api_key

    def chat(self, messages: List[Dict]) -> str:
        """同步对话"""
        return "response"

# ❌ 不好的实践

class deepseek_client:
    def __init__(self,api_key):
        self.api_key=api_key
```

### 命名规范
- **类名：** `PascalCase` (e.g., `DeepSeekClient`)
- **函数名：** `snake_case` (e.g., `count_tokens_estimate`)
- **常量：** `UPPER_SNAKE_CASE` (e.g., `MAX_TOKENS`)
- **私有方法/变量：** 前缀 `_` (e.g., `_format_context`)

### 类型注解
强制使用类型注解：

```python
from typing import List, Dict, Optional, Iterator

def process_text(
    text: str,
    max_length: Optional[int] = None
) -> List[str]:
    """处理文本"""
    pass
```

### 文档字符串
使用 Google 风格的 docstring：

```python
def chat_stream(
    self,
    messages: List[Dict[str, str]],
    temperature: float = 0.7
) -> Iterator[str]:
    """
    流式对话

    Args:
        messages: 消息列表，每条消息包含 role 和 content
        temperature: 温度参数，范围 0.0-2.0

    Yields:
        AI 回复的文本块

    Raises:
        ValueError: 当 API key 未配置时
        ConnectionError: 当连接失败时
    """
    pass
```

### 日志记录
使用 loguru 库：

```python
from loguru import logger

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")

# 异常日志
try:
    pass
except Exception as e:
    logger.error(f"Error occurred: {str(e)}")
    raise
```

---

## 项目架构设计

### 分层架构

```
┌─────────────────────────────────┐
│    Streamlit UI 层              │ (app.py)
├─────────────────────────────────┤
│    业务逻辑层                   │ (rag_service.py)
├─────────────────────────────────┤
│    数据处理层                   │
│  ├─ embedding_handler.py        │
│  ├─ chroma_handler.py           │
│  ├─ document_processor.py       │
│  └─ deepseek_client.py          │
├─────────────────────────────────┤
│    配置层                       │ (config.py)
├─────────────────────────────────┤
│    外部服务                     │
│  ├─ DeepSeek API               │
│  ├─ ChromaDB                   │
│  └─ BGE 模型                    │
└─────────────────────────────────┘
```

### 依赖注入模式
优先使用依赖注入而非全局变量：

```python
# ✅ 推荐
class RAGService:
    def __init__(self, embedding_handler, chroma_handler):
        self.embedding = embedding_handler
        self.chroma = chroma_handler

# ❌ 不推荐
class RAGService:
    def __init__(self):
        self.embedding = BGEEmbeddingHandler()  # 紧耦合
        self.chroma = ChromaHandler()            # 难以测试
```

---

## 开发工作流

### 1. 新功能开发

#### 第一步：创建新模块
```bash
# 创建新文件
touch src/new_feature.py

# 添加基础框架
cat > src/new_feature.py << 'EOF'
"""
新功能模块说明
"""
from typing import Optional
from loguru import logger


class NewFeature:
    """新功能类"""

    def __init__(self):
        """初始化"""
        logger.info("NewFeature initialized")

    def process(self, data: str) -> str:
        """处理数据"""
        return data
EOF
```

#### 第二步：添加到配置
如果需要配置，在 `config.py` 中添加：

```python
class Settings(BaseSettings):
    # ... 现有配置 ...
    NEW_FEATURE_ENABLED: bool = os.getenv("NEW_FEATURE_ENABLED", "False").lower() == "true"
```

#### 第三步：集成到应用
在 `app.py` 中导入和使用：

```python
from src.new_feature import NewFeature

def main():
    # ... 初始化 ...
    if settings.NEW_FEATURE_ENABLED:
        new_feature = NewFeature()
        result = new_feature.process("data")
```

### 2. 错误处理

#### 自定义异常
```python
class DeepSeekError(Exception):
    """DeepSeek API 异常"""
    pass

class ConfigError(Exception):
    """配置异常"""
    pass
```

#### 错误处理模式
```python
try:
    response = client.chat(messages)
except ConfigError as e:
    logger.error(f"Configuration error: {str(e)}")
    st.error("配置错误，请检查环境变量")
except DeepSeekError as e:
    logger.error(f"API error: {str(e)}")
    st.error("API 错误，请检查网络连接")
except Exception as e:
    logger.exception(f"Unexpected error: {str(e)}")
    st.error("发生意外错误")
```

### 3. 性能优化

#### 缓存策略
```python
from functools import lru_cache

class EmbeddingHandler:
    @lru_cache(maxsize=1000)
    def embed_text(self, text: str) -> List[float]:
        """缓存向量化结果"""
        return self.model.encode(text)
```

#### 批处理
```python
def embed_texts_batch(self, texts: List[str], batch_size: int = 32):
    """批量向量化，减少 API 调用"""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_results = self.model.encode(batch)
        results.extend(batch_results)
    return results
```

#### 异步处理（未来）
```python
import asyncio

async def chat_async(self, messages: List[Dict]) -> str:
    """异步对话"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, self.chat, messages)
```

---

## 测试指南

### 单元测试示例

#### 创建测试文件
```bash
mkdir tests
touch tests/__init__.py
touch tests/test_deepseek_client.py
```

#### 编写测试
```python
# tests/test_deepseek_client.py
import pytest
from src.deepseek_client import DeepSeekClient
from unittest.mock import patch, MagicMock


class TestDeepSeekClient:
    """DeepSeekClient 测试"""

    def setup_method(self):
        """测试前准备"""
        self.api_key = "test-key"

    @patch('src.deepseek_client.OpenAI')
    def test_init(self, mock_openai):
        """测试初始化"""
        client = DeepSeekClient(api_key=self.api_key)
        assert client.api_key == self.api_key

    def test_count_tokens_estimate(self):
        """测试 token 估算"""
        client = DeepSeekClient(api_key=self.api_key)
        tokens = client.count_tokens_estimate("Hello world")
        assert tokens > 0

    def test_missing_api_key(self):
        """测试缺少 API key"""
        with pytest.raises(ValueError):
            DeepSeekClient(api_key="")
```

#### 运行测试
```bash
# 安装 pytest
pip install pytest pytest-mock

# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_deepseek_client.py::TestDeepSeekClient::test_init

# 显示覆盖率
pytest --cov=src tests/
```

---

## 调试技巧

### 1. Streamlit 调试模式
```bash
streamlit run app.py --logger.level=debug
```

### 2. 使用 Python Debugger
```python
import pdb

def process_data(data):
    pdb.set_trace()  # 执行到此处时暂停
    return data
```

### 3. 查看日志
```bash
# 实时查看日志
tail -f logs/app.log

# 搜索特定错误
grep "ERROR" logs/app.log

# 查看最后100行
tail -100 logs/app.log
```

### 4. 环境变量调试
```python
import os
from dotenv import load_dotenv

load_dotenv()

# 检查所有加载的环境变量
for key, value in os.environ.items():
    if key.startswith("DEEPSEEK"):
        print(f"{key}={value}")
```

---

## 版本控制最佳实践

### Git 工作流

#### 功能分支开发
```bash
# 创建功能分支
git checkout -b feature/rag-knowledge-base

# 开发、提交
git add .
git commit -m "feat: add RAG knowledge base integration"

# 推送到远程
git push origin feature/rag-knowledge-base

# 创建 Pull Request
```

### 提交信息规范
```
feat:     新功能
fix:      bug 修复
docs:     文档更新
style:    代码风格（不改变功能）
refactor: 代码重构
perf:     性能优化
test:     测试相关
chore:    构建、依赖相关

示例：
feat: add RAG service with ChromaDB integration
fix: resolve token counting issue
docs: update README with new examples
```

---

## 依赖管理

### 添加新依赖
```bash
# 安装新库
pip install new-library

# 更新 requirements.txt
pip freeze > requirements.txt

# 或手动添加（指定版本范围）
echo "new-library>=1.0.0" >> requirements.txt
```

### 更新现有依赖
```bash
# 升级特定库
pip install --upgrade new-library

# 升级所有库
pip install --upgrade -r requirements.txt

# 检查过时的库
pip list --outdated
```

---

## 部署前检查清单

- [ ] 代码通过 PEP 8 检查
- [ ] 所有函数有类型注解
- [ ] 所有类和函数有 docstring
- [ ] 单元测试通过（>80% 覆盖率）
- [ ] 错误处理完整
- [ ] 日志记录充分
- [ ] 性能测试通过
- [ ] 文档已更新
- [ ] 敏感信息不在代码中（使用环境变量）
- [ ] 依赖项已冻结（requirements.txt）

---

## 常见问题解决

### 问题 1：导入错误
```
ModuleNotFoundError: No module named 'src'
```

**解决方案：**
1. 确保 `src/__init__.py` 存在
2. 确保从项目根目录运行应用
3. 检查 Python 路径

### 问题 2：API 超时
```python
# 增加超时时间
client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=30.0  # 30 秒超时
)
```

### 问题 3：内存不足
```python
# 使用生成器而非列表
def process_large_file(file_path):
    with open(file_path) as f:
        for line in f:  # 逐行处理
            yield process_line(line)
```

---

## 性能基准

### API 响应时间基准

| 操作 | 预期时间 | 备注 |
|------|---------|------|
| API 初始化 | <100ms | 建立连接 |
| 简单问答 | 1-3s | 200 tokens |
| 长回复 | 5-10s | 2000 tokens |
| 批量嵌入 | 100ms/1000 | 向量化 |

### 内存使用基准

| 操作 | 内存使用 |
|------|---------|
| 基础应用 | ~200MB |
| 加载 BGE 模型 | +1.5GB |
| 1000 条消息 | +50MB |

---

## 扩展指南

### 添加新的 LLM 提供商

创建 `src/openai_client.py`（或其他提供商）：

```python
class OpenAIClient:
    """OpenAI API 客户端"""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def chat(self, messages):
        # 实现
        pass

# 在 app.py 中支持多提供商
if provider == "deepseek":
    client = DeepSeekClient()
elif provider == "openai":
    client = OpenAIClient()
```

---

## 资源链接

- [Streamlit 文档](https://docs.streamlit.io/)
- [DeepSeek API 文档](https://www.deepseek.com/api/)
- [Python 类型注解](https://docs.python.org/3/library/typing.html)
- [PEP 8 风格指南](https://www.python.org/dev/peps/pep-0008/)
- [Google Python 风格指南](https://google.github.io/styleguide/pyguide.html)

---

**最后更新：2024-12-25**
