#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RagService的data_info_search方法是否能正确检索产品数据
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = r"D:\Projects\OGE-Agent\OGE-Agent"
sys.path.insert(0, project_root)

from rag.rag_service import RagService

def test_data_info_search():
    """测试data_info_search方法"""
    rag = RagService()

    test_queries = [
        "CN_FCH30_2020",
        "LJ3II_PAN_MSS",
        "Sentinel系列产品",
        "digital-legacy-jiayuguan",
        "GF1_L1_PMS2_EO"
    ]

    print("测试RagService.data_info_search方法:")
    print("=" * 50)

    for query in test_queries:
        print(f"\n查询: {query}")
        try:
            result = rag.data_info_search(query)
            print(f"结果: {result}")
        except Exception as e:
            print(f"错误: {str(e)}")

if __name__ == "__main__":
    test_data_info_search()