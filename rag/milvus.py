from pymilvus import MilvusClient

client = MilvusClient(uri="http://192.168.181.134:19530", db_name="test", user="root", password="root")

client.create_collection(
    collection_name="oge", # 集合的名称
    dimension=1024, # 向量的维度
    primary_field_name="id", # 主键字段名称
    id_type="int", # 主键的类型
    vector_field_name="vector", # 向量字段的名称
    metric_type="L2", # 指标类型，用于测量向量嵌入之间的相似性的算法。
    auto_id=True # 主键ID自动递增
)
