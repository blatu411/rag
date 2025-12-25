# 🚀 快速启动指南

## 5分钟内启动应用

### 步骤 1：安装依赖
```bash
pip install -r requirements.txt
```

### 步骤 2：配置 API Key
```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，填入你的 DeepSeek API Key
# 使用你喜欢的编辑器打开 .env
# DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

**如何获取 DeepSeek API Key？**
1. 访问 https://www.deepseek.com/
2. 注册账号（免费）
3. 进入开发者后台
4. 创建 API Key
5. 复制到 .env 文件中的 `DEEPSEEK_API_KEY` 字段

### 步骤 3：运行应用
```bash
streamlit run app.py
```

**应用会自动打开浏览器：** `http://localhost:8501`

### 步骤 4：开始对话
1. 在下方输入框输入你的问题，例如：
   - "你好，请自我介绍一下"
   - "用 Python 写一个 hello world 程序"
   - "解释一下什么是 AI"
2. 按 Enter 或点击发送按钮
3. 观看 AI 实时流式回复

## 📊 应用功能

### 侧边栏控制

| 功能 | 说明 |
|------|------|
| **🟢 API 状态** | 显示 API 连接状态 |
| **温度** | 调整 AI 的创意程度（0.0-2.0） |
| **最大 Token 数** | 控制回复长度（256-4096） |
| **消息数量** | 统计当前对话轮数 |
| **估计 Token** | 显示本次对话的 token 消耗 |
| **清空历史** | 清除所有对话记录 |

## 🔧 常见问题

### "API 配置错误" 怎么办？

1. **检查 .env 文件是否存在**
   ```bash
   ls -la .env  # 应该存在
   ```

2. **检查 API Key 是否正确**
   ```bash
   cat .env
   # 应该看到类似：DEEPSEEK_API_KEY=sk-...
   ```

3. **重启应用**
   ```bash
   # 关闭当前应用（Ctrl+C）
   # 重新运行
   streamlit run app.py
   ```

### 流式输出很慢？

- 检查网络连接
- 降低 `max_tokens` 参数（在侧边栏调整）
- 确认 DeepSeek 服务正常

### 对话历史会保存吗？

- **当前版本（v0.1.0）：** 对话仅保存在内存中
- 刷新页面或重启应用会丢失历史
- **未来版本：** 会添加数据库持久化功能

## 💡 使用技巧

### 获得更好的回复

1. **调整温度参数**
   - 0.0-0.5：更稳定、准确的回复（适合问答）
   - 0.5-1.0：平衡的创意和准确性
   - 1.0-2.0：更有创意的回复（适合创意写作）

2. **提供清晰的提示**
   ```
   不好：写一个程序
   更好：用 Python 写一个程序，功能是读取 CSV 文件并计算平均值
   ```

3. **利用多轮对话**
   ```
   第一轮：解释什么是 API
   第二轮：给我一个 REST API 的例子
   第三轮：用 Python 实现这个 API
   ```

## 🎓 学习资源

- [Streamlit 官方文档](https://docs.streamlit.io/)
- [DeepSeek API 文档](https://www.deepseek.com/api/)
- [OpenAI API 参考](https://platform.openai.com/docs/api-reference)

## 📱 系统要求

- Python 3.8 或更高版本
- 互联网连接
- 有效的 DeepSeek API Key

## 🔄 下一步

学习项目结构，为阶段 2（RAG 知识库）做准备：

1. 了解项目结构（查看 README.md）
2. 阅读 `src/deepseek_client.py` 了解 API 调用方式
3. 了解 `config.py` 的配置管理
4. 准备好 DeepSeek API Key，准备集成 RAG

## 📞 需要帮助？

- 查看应用内的"📖 使用说明"
- 阅读完整的 README.md
- 检查应用日志：`logs/app.log`

---

**祝你使用愉快！🎉**
