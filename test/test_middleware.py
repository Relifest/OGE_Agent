#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test middleware functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.react_agent import ReactAgent

def test_middleware():
    print("Creating ReactAgent...")
    agent = ReactAgent()
    print("ReactAgent created successfully")

    # Test with a simple query that should trigger tool calls
    print("Testing with simple query...")
    try:
        for i, chunk in enumerate(agent.execute_stream("你好")):
            print(f"Received chunk {i}: {chunk[:50]}...")
            if i >= 2:  # Only get first few chunks
                break
        print("Test completed")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_middleware()