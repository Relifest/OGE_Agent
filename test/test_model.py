#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test model directly with proper encoding
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from model.factory import chat_model

def test_model():
    print("Testing model directly...")
    try:
        response = chat_model.invoke("你好")
        # Safely convert to string and handle encoding
        response_str = str(response).encode('utf-8', errors='ignore').decode('utf-8')
        print(f"Model response: {response_str}")

        # Also check if it has content attribute
        if hasattr(response, 'content'):
            content_str = response.content.encode('utf-8', errors='ignore').decode('utf-8')
            print(f"Content: {content_str}")

    except Exception as e:
        print(f"Model test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_model()