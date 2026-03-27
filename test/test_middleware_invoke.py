#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test middleware with non-streaming call
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.react_agent import ReactAgent

def test_middleware_non_streaming():
    print("Creating ReactAgent...")
    agent = ReactAgent()
    print("ReactAgent created successfully")

    # Test with a simple query using invoke instead of stream
    print("Testing with non-streaming invoke...")
    try:
        inputs = {"messages": [{"role": "user", "content": "你好"}]}
        result = agent.agent.invoke(inputs)
        print(f"Non-streaming result: {result}")
        print("Test completed")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_middleware_non_streaming()