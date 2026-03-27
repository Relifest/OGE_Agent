#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from model.factory import chat_model

response = chat_model.invoke("hello")
print("Model call successful!")
print("Response type:", type(response))
if hasattr(response, 'content'):
    print("Has content attribute")