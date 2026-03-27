#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门用于将data_products目录中的产品数据加载到Milvus向量库中
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = r"D:\Projects\OGE-Agent\OGE-Agent"
sys.path.insert(0, project_root)

from rag.vector_store import VectorStoreService
from utils.file_handler import txt_loader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.config_handler import milvus_conf
import json


def load_product_data_to_milvus():
    """将产品数据加载到Milvus向量库"""
    print("初始化Milvus向量库服务...")
    vector_store = VectorStoreService()

    # 配置文本分割器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=milvus_conf["chunk_size"],
        chunk_overlap=milvus_conf["chunk_overlap"],
        separators=milvus_conf["separators"],
        length_function=len
    )

    # 产品数据目录
    product_data_dir = r"D:\Projects\OGE-Agent\OGE-Agent\data\data_products"

    if not os.path.exists(product_data_dir):
        print(f"错误: 产品数据目录不存在: {product_data_dir}")
        return

    # 获取所有txt文件
    txt_files = [f for f in os.listdir(product_data_dir) if f.endswith('.txt')]

    if not txt_files:
        print("警告: 产品数据目录中没有找到txt文件")
        return

    print(f"找到 {len(txt_files)} 个产品数据文件，开始加载到Milvus...")

    success_count = 0
    error_count = 0

    for filename in txt_files:
        file_path = os.path.join(product_data_dir, filename)
        try:
            # 加载文档
            documents = txt_loader(file_path)
            if not documents:
                print(f"警告: {filename} 没有有效内容")
                error_count += 1
                continue

            # 分割文档
            split_documents = splitter.split_documents(documents)
            if not split_documents:
                print(f"警告: {filename} 分割后没有有效内容")
                error_count += 1
                continue

            # 添加到Milvus
            vector_store._add_documents_to_milvus(split_documents, file_path)
            print(f"成功: {filename}")
            success_count += 1

        except Exception as e:
            print(f"错误: 处理 {filename} 时出错 - {str(e)}")
            error_count += 1
            continue

    print(f"\n加载完成!")
    print(f"成功: {success_count} 个文件")
    print(f"失败: {error_count} 个文件")
    print(f"总文件数: {len(txt_files)} 个")


if __name__ == "__main__":
    load_product_data_to_milvus()