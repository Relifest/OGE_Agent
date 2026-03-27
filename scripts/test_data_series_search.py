#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试data_series_search函数是否能正确检索产品数据
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = r"D:\Projects\OGE-Agent\OGE-Agent"
sys.path.insert(0, project_root)

from agent.tools.agent_tools import data_series_search

def test_data_series_search():
    """测试data_series_search函数"""
    test_queries = [
        "CN_FCH30_2020",
        "LJ3II_PAN_MSS",
        "Sentinel系列产品",
        "digital-legacy-jiayuguan",
        "GF1_L1_PMS2_EO"
    ]

    print("测试data_series_search函数:")
    print("=" * 50)

    for query in test_queries:
        print(f"\n查询: {query}")
        try:
            result = data_series_search(query)
            print(f"结果: {result}")
        except Exception as e:
            print(f"错误: {str(e)}")

if __name__ == "__main__":
    test_data_series_search()