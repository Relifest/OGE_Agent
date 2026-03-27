#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from langchain.agents import create_agent
from model.factory import chat_model
from agent.tools.agent_tools import basic_info_search
from utils.prompt_loader import load_system_prompts

# Import middleware to ensure it's registered
import agent.tools.middleware

tools = [basic_info_search]
system_prompt = load_system_prompts()

print("Creating agent...")
agent = create_agent(
    model=chat_model,
    tools=tools,
    system_prompt=system_prompt,
    debug=True
)
print("Agent created")

print("Invoking agent...")
inputs = {"messages": [{"role": "user", "content": "hello"}]}
result = agent.invoke(inputs)
print("Agent invoke successful!")