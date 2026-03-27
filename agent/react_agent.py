#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React Agent with message history support and LangChain monitoring
"""

import os
import sys
import io
from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts, load_system_prompts_with_history
from agent.tools.agent_tools import basic_info_search, data_series_search, data_search
from utils.logger_handler import logger


# LangChain tracing configuration - set these environment variables externally
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-api-key"
# os.environ["LANGCHAIN_PROJECT"] = "oge"

# 设置控制台输出编码为UTF-8（Windows兼容）
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except Exception:
        pass  # 如果设置失败，继续使用默认编码


class ReactAgent:
    def __init__(self):
        # 创建工具列表
        tools = [basic_info_search, data_series_search, data_search]
        logger.info(f"初始化ReactAgent，工具列表: {[tool.name for tool in tools]}")

        # 创建无历史记录的系统提示（用于execute_stream）
        system_prompt = load_system_prompts()
        logger.info(f"加载系统提示完成，长度: {len(system_prompt) if system_prompt else 0}")

        # 使用 create_agent 创建无历史记录的 agent（用于execute_stream）
        self.agent = create_agent(
            model=chat_model,
            tools=tools,
            system_prompt=system_prompt
        )
        logger.info("ReactAgent无历史记录agent初始化完成")

        # 创建带历史记录的系统提示（用于execute_stream_with_history）
        system_prompt_with_history = load_system_prompts_with_history()
        # ========== 方案1修正：在execute_stream_with_history方法中手动处理历史记录 ==========
        # 原始实现（注释保留，不删除）
        # # 构建带会话历史占位符的聊天提示词模板
        # prompt_with_history = ChatPromptTemplate.from_messages([
        #     SystemMessage(content=system_prompt_with_history),
        #     MessagesPlaceholder(variable_name="history"),
        #     ("human", "{input}")
        # ])
        #
        # # 创建基础运行链
        # chain_with_history = prompt_with_history | chat_model
        #
        # # 为基础链添加Redis持久化+多用户多会话双层隔离记忆能力
        # self.agent_with_history = RunnableWithMessageHistory(
        #     chain_with_history,
        #     get_session_history=get_session_history,
        #     input_messages_key="input",
        #     history_messages_key="history",
        #     history_factory_config=[
        #         ConfigurableFieldSpec(
        #             id="user_id",
        #             annotation=str,
        #             name="用户id",
        #             description="用户唯一标识符",
        #             default="",
        #             is_shared=True
        #         ),
        #         ConfigurableFieldSpec(
        #             id="session_id",
        #             annotation=str,
        #             name="对话id",
        #             description="对话唯一标识符",
        #             default="",
        #             is_shared=True
        #         )
        #     ]
        # )

        # 新策略：不在__init__中创建复杂的agent，而是在execute_stream_with_history中
        # 手动获取历史记录并调用现有的agent_without_history
        # 这样可以复用现有的完整工具调用能力
        logger.info("ReactAgent带历史记录agent初始化完成（采用手动历史记录处理策略）")
        # ========================================================

    def execute_stream_with_history(
        self,
        query: str,
        user_id: str,
        session_id: str
    ):
        """
        执行流式响应，支持历史消息和Redis持久化
        只需要输入用户query和会话ID，自动处理历史消息
        """
        logger.info(f"execute_stream_with_history 调用 - user_id: {user_id}, session_id: {session_id}, query: {query[:50]}...")

        # 验证输入
        if not query:
            error_msg = "用户查询内容不能为空"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if not user_id or not session_id:
            error_msg = "user_id和session_id不能为空"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 手动获取历史记录并构造包含历史的输入
        from utils.redis_history import get_session_history
        history = get_session_history(user_id, session_id)
        historical_messages = history.messages

        # 构造包含历史消息的输入字典
        # 将历史消息转换为适合agent的格式
        messages_list = []

        # 添加历史消息
        for msg in historical_messages:
            if 'AIMessage' in str(type(msg)):
                messages_list.append({
                    "role": "assistant",
                    "content": msg.content
                })
            elif 'HumanMessage' in str(type(msg)):
                messages_list.append({
                    "role": "user",
                    "content": msg.content
                })

        # 添加当前用户消息
        messages_list.append({
            "role": "user",
            "content": query
        })

        input_dict = {
            "messages": messages_list
        }

        response_content = ""
        try:
            # 使用现有的完整Agent处理包含历史的输入
            for chunk in self.agent.stream(input_dict, stream_mode="values"):
                latest_message = chunk["messages"][-1]
                if latest_message.content:
                    content = latest_message.content.strip() + "\n"
                    response_content += content
                    yield content

            # 将AI的响应保存到历史记录中
            if response_content.strip():
                history.add_ai_message(response_content.strip())

        except Exception as e:
            logger.error(f"execute_stream_with_history执行过程中出现错误: {e}")
            raise e

        logger.info(f"execute_stream_with_history 完成，响应长度: {len(response_content)}")


    def execute_stream(self, query: str):
        """
        兼容旧的单次查询接口（不使用历史记录）
        """
        logger.info(f"execute_stream 调用 - 查询: {query[:50]}...")

        input_dict = {
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        }

        response_content = ""
        for chunk in self.agent.stream(input_dict, stream_mode="values"):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                content = latest_message.content.strip() + "\n"
                response_content += content
                yield content


if __name__ == '__main__':
    agent = ReactAgent()
    # 测试2: 完整的Redis历史功能测试（新接口）
    print("=== 测试 execute_stream_with_history (带Redis历史记录) ===")

    # 测试参数
    user_id = "test_user_002"
    session_id = "test_session_002"

    # 清理测试数据
    from utils.redis_history import get_session_history
    history = get_session_history(user_id, session_id)
    history.clear()

    # 第一轮对话：发送第一条消息
    print(f"\n--- 第一轮对话 (user_id: {user_id}, session_id: {session_id}) ---")
    query1 = "你好，请介绍一下OGE平台的总体情况"

    try:
        response_parts = []
        for chunk in agent.execute_stream_with_history(query1, user_id, session_id):
            # 过滤特殊字符避免编码问题
            safe_chunk = chunk.encode('utf-8', errors='replace').decode('utf-8')
            print(safe_chunk, end="", flush=True)
            response_parts.append(safe_chunk)

        full_response1 = "".join(response_parts)
        print(f"\n第一轮响应完成，长度: {len(full_response1)}")

        # 第二轮对话：发送第二条消息，应该包含历史
        print(f"\n--- 第二轮对话 (使用相同 user_id 和 session_id) ---")
        query2 = "你能记住我刚才问的问题吗？"

        response_parts2 = []
        for chunk in agent.execute_stream_with_history(query2, user_id, session_id):
            safe_chunk = chunk.encode('utf-8', errors='replace').decode('utf-8')
            print(safe_chunk, end="", flush=True)
            response_parts2.append(safe_chunk)

        full_response2 = "".join(response_parts2)
        print(f"\n第二轮响应完成，长度: {len(full_response2)}")

        # 验证历史消息是否正确存储
        print(f"\n--- 验证Redis历史消息 ---")
        test_history = get_session_history(user_id, session_id)
        historical_messages = test_history.messages
        print(f"从Redis获取到 {len(historical_messages)} 条历史消息:")
        for i, msg in enumerate(historical_messages):
            msg_type = "AI" if 'AIMessage' in str(type(msg)) else "Human"
            content_preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
            print(f"  {i+1}. [{msg_type}] {content_preview}")

        # 清理测试数据
        test_history.clear()

    except Exception as e:
        print(f"\n测试2过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*50)
    print("所有测试完成！")
