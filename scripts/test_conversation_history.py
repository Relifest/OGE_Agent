#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多轮对话功能和Redis历史记录
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time


def test_chat_history():
    """测试多轮对话历史功能"""
    base_url = "http://localhost:8000/api/agent"

    # 测试数据
    user_id = "test_user_123"
    session_id = "test_session_456"

    # 第一轮对话
    print("=== 第一轮对话 ===")
    first_message = {
        "messages": [
            {"role": "user", "content": "你好，能介绍一下OGE平台吗？"}
        ],
        "user_id": user_id,
        "session_id": session_id,
        "stream": False
    }

    response = requests.post(f"{base_url}/chat", json=first_message)
    if response.status_code == 200:
        result = response.json()
        print(f"响应: {result['data']['response'][:200]}...")
    else:
        print(f"错误: {response.status_code} - {response.text}")
        return

    time.sleep(2)

    # 第二轮对话（包含历史）
    print("\n=== 第二轮对话（包含历史）===")
    second_message = {
        "messages": [
            {"role": "user", "content": "你好，能介绍一下OGE平台吗？"},
            {"role": "assistant", "content": "当然可以！OGE是一个..."},  # 实际上这里应该用第一轮的真实响应
            {"role": "user", "content": "那OGE平台有哪些主要功能？"}
        ],
        "user_id": user_id,
        "session_id": session_id,
        "stream": False
    }

    # 实际测试时，第二轮的assistant消息应该是第一轮的真实响应
    # 这里为了演示简化处理
    second_message["messages"][1]["content"] = "OGE平台是一个地理信息服务平台。"

    response = requests.post(f"{base_url}/chat", json=second_message)
    if response.status_code == 200:
        result = response.json()
        print(f"响应: {result['data']['response'][:200]}...")
    else:
        print(f"错误: {response.status_code} - {response.text}")


def test_redis_storage():
    """测试Redis存储功能"""
    from utils.redis_history import RedisChatMessageHistory

    # 创建测试历史记录
    history = RedisChatMessageHistory(
        session_id="test_session_789",
        user_id="test_user_456",
        ttl=60  # 1分钟过期，便于测试
    )

    # 添加消息
    from langchain_core.messages import HumanMessage, AIMessage
    history.add_message(HumanMessage(content="测试用户消息"))
    history.add_message(AIMessage(content="测试AI响应"))

    # 读取消息
    messages = history.messages
    print(f"\n=== Redis存储测试 ===")
    print(f"存储的消息数量: {len(messages)}")
    for i, msg in enumerate(messages):
        print(f"消息 {i+1}: {msg.type} - {msg.content}")

    # 清空测试数据
    history.clear()
    print("测试数据已清理")


if __name__ == "__main__":
    print("开始测试多轮对话功能...")
    test_redis_storage()
    # test_chat_history()  # 需要先启动服务才能测试