import requests
import json
import uuid

# 生成唯一的session_id和user_id
user_id = str(uuid.uuid4())
session_id = str(uuid.uuid4())

# 测试带有历史信息的流式接口1
url2 = "http://127.0.0.1:8000/api/agent/chat/stream"
data2 = {
    "messages": [
        {"role": "user", "content": "你好，介绍一下OGE平台的整体情况"}
    ],
    "user_id": user_id,
    "session_id": session_id
}

print("测试带有历史信息的流式接口1:")
try:
    response = requests.post(url2, json=data2, stream=True)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("响应内容:")
        full_response = ""
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                full_response += chunk
        # 检查是否包含最终答案
        if "OGE开放地球引擎平台" in full_response:
            print("✅ 成功返回最终答案")
        else:
            print("⚠️ 可能只返回了思考过程")
        print(full_response)
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"请求失败: {e}")

print("\n" + "="*50 + "\n")

# 测试带有历史信息的流式接口2
data3 = {
    "messages": [
        {"role": "user", "content": "我刚才问了你什么问题"}
    ],
    "user_id": user_id,
    "session_id": session_id
}
print("测试带有历史信息的流式接口2:")
try:
    response = requests.post(url2, json=data3, stream=True)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("响应内容:")
        full_response2 = ""
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                full_response2 += chunk
        print(full_response2)
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"请求失败: {e}")