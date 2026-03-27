#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理productId.json数据，将每个children元素转换为单独的文本文件，
以便加载到Milvus向量库中供data_series_search函数检索。
"""

import json
import os
from pathlib import Path

def process_product_data():
    """处理产品数据并生成文本文件"""
    # 读取productId.json
    product_file = r"D:\Projects\OGE-Agent\OGE-Agent\data\data_center\productId.json"
    output_dir = r"D:\Projects\OGE-Agent\OGE-Agent\data\data_products"

    with open(product_file, 'r', encoding='utf-8') as f:
        products = json.load(f)

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 处理每个产品类别及其子产品
    for product_category in products:
        category_name = product_category.get('name', '')
        category_name_en = product_category.get('nameEn', '')
        category_id = product_category.get('id', 0)

        children = product_category.get('children', [])

        for child in children:
            child_name = child.get('name', '')
            child_id = child.get('id', 0)

            # 创建文本内容，包含足够的上下文信息用于检索
            content = f"""产品名称: {child_name}
产品ID: {child_id}
所属分类: {category_name} ({category_name_en})
分类ID: {category_id}

这个产品属于{category_name}分类，可以通过产品名称"{child_name}"或相关关键词进行检索。"""

            # 创建文件名（使用产品名称作为文件名）
            safe_filename = "".join(c for c in child_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_filename:
                safe_filename = f"product_{child_id}"

            file_path = os.path.join(output_dir, f"{safe_filename}.txt")

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"已创建文件: {file_path}")

    print(f"\n总共处理了 {sum(len(p.get('children', [])) for p in products)} 个子产品")
    print(f"文件已保存到: {output_dir}")

if __name__ == "__main__":
    process_product_data()