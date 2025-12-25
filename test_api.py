"""
测试 DeepSeek API 连接的脚本
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件
load_dotenv()

# 获取配置
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

print(f"API Key: {api_key[:20]}..." if api_key else "API Key: 未找到")
print(f"Base URL: {base_url}")
print()

# 测试连接
try:
    print("正在尝试连接 DeepSeek API...")
    client = OpenAI(api_key=api_key, base_url=base_url)

    print("发送测试请求...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "你好"}],
        max_tokens=100
    )

    print("\n✅ 连接成功！")
    print(f"回复: {response.choices[0].message.content}")

except Exception as e:
    print(f"\n❌ 连接失败！")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {str(e)}")
