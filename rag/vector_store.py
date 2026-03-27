# # -*- coding: utf-8 -*-
# import os.path
# import json
# from pymilvus import MilvusClient
# from langchain_core.documents import Document
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from utils.config_handler import milvus_conf
# from model.factory import embed_model
# from utils.file_handler import txt_loader, pdf_loader, listdir_with_allowed_type, get_file_md5_hex, html_loader
# from utils.logger_handler import logger
# from utils.path_tool import get_abs_path
#
#
# class VectorStoreService:
#     def __init__(self):
#         # 使用 PyMilvus Client 直接连接
#         connection_args = milvus_conf["connection_args"]
#         self.client = MilvusClient(
#             uri=connection_args["uri"],
#             db_name=connection_args["db_name"],
#             user=connection_args["user"],
#             password=connection_args["password"]
#         )
#
#         self.collection_name = milvus_conf["collection_name"]
#         self.vector_dim = milvus_conf.get("vector_dim", 1024)
#         self.metric_type = milvus_conf.get("metric_type", "L2")
#
#         # 确保集合存在
#         self._ensure_collection_exists()
#
#         self.spliter = RecursiveCharacterTextSplitter(
#             chunk_size=milvus_conf["chunk_size"],
#             chunk_overlap=milvus_conf["chunk_overlap"],
#             separators=milvus_conf["separators"],
#             length_function=len
#         )
#
#     def _ensure_collection_exists(self):
#         """确保集合存在，如果不存在则创建"""
#         collections = self.client.list_collections()
#         if self.collection_name not in collections:
#             logger.info(f"Creating collection: {self.collection_name}")
#             # 创建集合时只定义基本字段
#             self.client.create_collection(
#                 collection_name=self.collection_name,
#                 dimension=self.vector_dim,
#                 metric_type=self.metric_type,
#                 auto_id=True,
#                 enable_dynamic_field=True  # 启用动态字段以支持metadata
#             )
#
#             # 创建索引（IVF_FLAT 或 HNSW）
#             index_params = {
#                 "metric_type": self.metric_type,
#                 "index_type": "IVF_FLAT",
#                 "params": {"nlist": 128}
#             }
#             self.client.create_index(
#                 collection_name=self.collection_name,
#                 index_params=index_params
#             )
#             logger.info(f"Collection {self.collection_name} created with index and dynamic fields enabled")
#
#     def get_retriever(self):
#         """返回检索器对象"""
#         return self
#
#     def invoke(self, query: str, k: int = None):
#         """执行相似性搜索"""
#         if k is None:
#             k = milvus_conf["k"]
#
#         # 获取查询向量
#         query_vector = embed_model.embed_query(query)
#
#         # 执行搜索
#         results = self.client.search(
#             collection_name=self.collection_name,
#             data=[query_vector],
#             limit=k,
#             output_fields=["text", "source", "metadata_json"]
#         )
#
#         # 转换为 Document 对象
#         documents = []
#         for result in results[0]:  # results[0] because we searched with one query
#             metadata = {}
#             if "metadata_json" in result["entity"]:
#                 try:
#                     metadata = json.loads(result["entity"]["metadata_json"])
#                 except (json.JSONDecodeError, TypeError):
#                     metadata = {}
#
#             # 添加source信息
#             if "source" in result["entity"]:
#                 metadata["source"] = result["entity"]["source"]
#
#             doc = Document(
#                 page_content=result["entity"]["text"],
#                 metadata=metadata
#             )
#             documents.append(doc)
#
#         return documents
#
#     def load_document(self):
#         """
#         从数据文件夹内读取数据文件，转为向量存入向量库
#         要计算文件的MD5做去重
#         :return: None
#         """
#
#         def check_md5_hex(md5_for_check: str):
#             file_path = get_abs_path(milvus_conf.get("md5_hex_store", "data/milvus_md5.txt"))
#             if not os.path.exists(file_path):
#                 # 创建文件
#                 open(file_path, "w", encoding="utf-8").close()
#                 return False
#
#             with open(file_path, "r", encoding="utf-8") as f:
#                 for line in f.readlines():
#                     line = line.strip()
#                     if line == md5_for_check:
#                         return True
#
#                 return False
#
#         def save_md5_hex(md5_for_check: str):
#             file_path = get_abs_path(milvus_conf.get("md5_hex_store", "data/milvus_md5.txt"))
#             with open(file_path, "a", encoding="utf-8") as f:
#                 f.write(md5_for_check + "\n")
#
#         def get_file_documents(read_path: str):
#             if read_path.endswith("txt"):
#                 return txt_loader(read_path)
#
#             if read_path.endswith("pdf"):
#                 return pdf_loader(read_path)
#
#             if read_path.endswith("html"):
#                 return html_loader(read_path)
#
#             return []
#
#         allowed_files_path = listdir_with_allowed_type(
#             get_abs_path(milvus_conf["data_path"]),
#             tuple(milvus_conf["allow_knowledge_file_type"])
#         )
#
#         for path in allowed_files_path:
#             # 获取文件的 md5
#             md5_hex = get_file_md5_hex(path)
#
#             if check_md5_hex(md5_hex):
#                 logger.info(f"[加载知识库]{path}内容已经存在在知识库内，跳过")
#                 continue
#
#             try:
#                 documents = get_file_documents(path)
#
#                 if not documents:
#                     logger.warning(f"[加载知识库]{path}内没有有效文本内容，跳过")
#                     continue
#
#                 split_document = self.spliter.split_documents(documents)
#
#                 if not split_document:
#                     logger.warning(f"[加载知识库]{path}分片后没有有效文本内容，跳过")
#                     continue
#
#                 # 将内容转换为向量并存入向量库
#                 self._add_documents_to_milvus(split_document, path)
#
#                 # 记录这个已经处理好的文件的 md5，避免下次重复加载
#                 save_md5_hex(md5_hex)
#
#                 logger.info(f"[加载知识库]{path}内容加载成功")
#
#             except Exception as e:
#                 # exc_info为True会记录详细的报错堆栈
#                 logger.error(f"[加载知识库]{path}加载失败：{str(e)}", exc_info=True)
#                 continue
#
#     def _add_documents_to_milvus(self, documents, source_path):
#         """将文档添加到Milvus向量库"""
#         data = []
#         for doc in documents:
#             # 获取文本向量
#             vector = embed_model.embed_query(doc.page_content)
#
#             # 准备metadata（转换为JSON字符串以确保兼容性）
#             metadata_json = json.dumps(doc.metadata, ensure_ascii=False, default=str)
#
#             # 准备数据
#             entity = {
#                 "vector": vector,
#                 "text": doc.page_content,
#                 "source": source_path,
#                 "metadata_json": metadata_json
#             }
#             data.append(entity)
#
#         # 批量插入
#         self.client.insert(
#             collection_name=self.collection_name,
#             data=data
#         )
#
#
# if __name__ == '__main__':
#     vs = VectorStoreService()
#     retriever = vs.get_retriever()
#     res = retriever.invoke("oge总体介绍")
#     for r in res:
#         print(r.page_content)
#         print("=" * 20)

import os.path
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.config_handler import chroma_conf
from model.factory import embed_model
from utils.file_handler import txt_loader, pdf_loader, listdir_with_allowed_type, get_file_md5_hex, html_loader
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=get_abs_path(chroma_conf["persist_directory"])
        )

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size_data"],
            chunk_overlap=chroma_conf["chunk_overlap_data"],
            separators=chroma_conf["separators"],
            length_function=len
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwags={"k": chroma_conf["k"]})

    def load_document(self):
        """
        从数据文件夹内读取数据文件，转为向量存入向量库
        要计算文件的MD5做去重
        :return: None
        """

        def check_md5_hex(md5_for_check: str):
            file_path = get_abs_path(chroma_conf["md5_hex_store"])
            if not os.path.exists(file_path):
                # 创建文件
                open(file_path, "w", encoding="utf-8").close()
                return False

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True

                return False

        def save_md5_hex(md5_for_check: str):
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(read_path: str):
            if read_path.endswith("txt"):
                return txt_loader(read_path)

            if read_path.endswith("pdf"):
                return pdf_loader(read_path)

            if read_path.endswith("html"):
                return html_loader(read_path)

            return []

        allowed_files_path = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"])
        )

        for path in allowed_files_path:
            # 获取文件的 md5
            md5_hex = get_file_md5_hex(path)

            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{path}内容已经存在在知识库内，跳过")
                continue

            try:
                documents = get_file_documents(path)

                if not documents:
                    logger.warning(f"[加载知识库]{path}内没有有效文本内容，跳过")
                    continue
                split_document = self.spliter.split_documents(documents)

                if not split_document:
                    logger.warningf(f"[加载知识库]{path}分片后没有有效文本内容，跳过")
                    continue

                # 将内容存入向量库
                self.vector_store.add_documents(split_document)

                # 记录这个已经处理好的文件的 md5，避免下次重复加载
                save_md5_hex(md5_hex)

                logger.info(f"[加载知识库]{path}内容加载成功")

            except Exception as e:
                # exc_info为True会记录详细的报错堆栈
                logger.error(f"[加载知识库]{path}加载失败：{str(e)}", exc_info=True)
                continue


# if __name__ == '__main__':
#     vs = VectorStoreService()
#     # vs.load_document()
#
#     retriever = vs.get_retriever()
#     res = retriever.invoke("landsat产品")
#     for r in res:
#         print(r.page_content)
#         print("=" * 20)