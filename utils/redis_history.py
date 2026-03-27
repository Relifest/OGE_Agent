#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis会话历史管理模块
用于存储和检索用户的对话历史
"""

import json
from typing import List, Optional
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict, messages_to_dict
from redis import Redis
from utils.config_handler import redis_conf


class RedisChatMessageHistory(BaseChatMessageHistory):
    """基于Redis的聊天消息历史存储"""

    def __init__(
        self,
        session_id: str,
        user_id: str,
        url: str = None,
        ttl: Optional[int] = None,
    ):
        """
        初始化Redis聊天历史

        Args:
            session_id: 对话会话ID
            user_id: 用户ID
            url: Redis连接URL
            ttl: 消息过期时间（秒）
        """
        if url is None:
            url = redis_conf.get("REDIS_URL", "redis://localhost:6379/0")

        self.redis_client = Redis.from_url(url, decode_responses=True)
        self.session_id = session_id
        self.user_id = user_id
        self.ttl = ttl
        # 使用 user_id:session_id 作为Redis键，实现双层隔离
        self.key = f"chat_history:{user_id}:{session_id}"

    def add_message(self, message: BaseMessage) -> None:
        """添加消息到历史记录"""
        messages = messages_to_dict(self.messages)
        messages.append(messages_to_dict([message])[0])

        # 将消息列表序列化为JSON并存储到Redis
        self.redis_client.rpush(self.key, json.dumps(messages[-1]))

        # 设置过期时间（如果配置了ttl）
        if self.ttl:
            self.redis_client.expire(self.key, self.ttl)

    def clear(self) -> None:
        """清空历史记录"""
        self.redis_client.delete(self.key)

    @property
    def messages(self) -> List[BaseMessage]:
        """获取所有历史消息"""
        raw_messages = self.redis_client.lrange(self.key, 0, -1)
        if not raw_messages:
            return []

        # 反序列化所有消息
        message_dicts = [json.loads(msg) for msg in raw_messages]
        return messages_from_dict(message_dicts)


def get_session_history(user_id: str, session_id: str) -> RedisChatMessageHistory:
    """
    获取会话历史工厂函数
    用于LangChain的RunnableWithMessageHistory

    Args:
        user_id: 用户ID
        session_id: 会话ID

    Returns:
        RedisChatMessageHistory实例
    """
    return RedisChatMessageHistory(
        session_id=session_id,
        user_id=user_id,
        url=redis_conf.get("REDIS_URL"),
        ttl=3600  # 1小时过期
    )