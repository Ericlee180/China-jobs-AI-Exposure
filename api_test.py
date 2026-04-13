import requests
import json

API_KEY = "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"
API_URL = "https://openrouter.ai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# 测试一个模型
model = "google/gemini-2.0-flash-lite-preview"
print(f"\n测试模型: {model}")

payload = {
    "model": model,
    "messages": [{"role": "user", "content": "Say 'OK'"}],
    "max_tokens": 5,
}

try:
    response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
    print(f"状态码: {response.status_code}")
    
    # 先打印原始响应文本
    print(f"原始响应: {repr(response.text)}")  # repr() 会显示转义字符，帮助调试
    
    if response.status_code == 200:
        # 尝试解析 JSON
        try:
            data = response.json()
            print(f"✅ 解析成功！")
            print(f"响应内容: {data['choices'][0]['message']['content']}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
            print(f"响应文本前200字符: {response.text[:200]}")
    else:
        print(f"❌ HTTP 错误: {response.status_code}")
        print(f"错误详情: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")