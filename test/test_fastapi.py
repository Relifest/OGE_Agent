#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test FastAPI endpoints directly
"""

import requests
import json

def test_query_endpoint():
    """Test the /query endpoint"""
    url = "http://localhost:8000/api/agent/query"
    payload = {"query": "hello world"}

    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Response JSON: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_health_check():
    """Test the health check endpoint"""
    url = "http://localhost:8000/api/agent/health"

    try:
        response = requests.get(url)
        print(f"Health Check Status Code: {response.status_code}")
        print(f"Health Check Response: {response.text}")
    except Exception as e:
        print(f"Health Check Error: {e}")

if __name__ == "__main__":
    print("Testing Health Check...")
    test_health_check()
    print("\nTesting Query Endpoint...")
    test_query_endpoint()