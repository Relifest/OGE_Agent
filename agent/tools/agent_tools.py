import json
from typing import Optional, Dict, Any
from langchain_community.utilities.requests import TextRequestsWrapper
from langchain_core.tools import tool
from rag.rag_service import RagService
from utils.config_handler import api_config

rag = RagService()
external_data = {}

@tool(description="从向量存储中检索参考资料并回答用户关于OGE平台基本信息的问题")
def basic_info_search(query: str) -> str:
    return rag.basic_info_search(query)


@tool(description="从向量存储中检索参考资料并回答用户关于OGE平台中具体的数据产品系列信息的问题")
def data_series_search(query: str) -> str:
    """
    核心检索函数：根据查询获取产品ID
    :param query: 用户查询词
    :return: 产品详细信息（JSON字符串）
    """
    return rag.data_info_search(query)


@tool(description="从向量存储中检索参考资料并回答用户关于OGE平台中具体的子产品等信息的问题")
def data_search(query: str) -> str:
    """
    核心检索函数：根据查询调用接口返回详细信息
    :param query: 用户查询词
    :return: 产品详细信息（JSON字符串）/ 提示信息
    """
    product_id = eval(rag.data_info_search(query))
    # 调用OGE接口获取详细信息
    product_detail = get_product_detail(product_id)
    if product_detail:
        # 返回格式化的JSON字符串（便于后续处理/展示）
        return json.dumps(product_detail, ensure_ascii=False, indent=2)
    else:
        return f"未查询到productId={product_id}对应的产品详细信息"


def get_product_detail(product_id: int) -> Optional[Dict[str, Any]]:
    """
    调用OGE接口获取指定productId的产品详细信息
    :param product_id: 产品ID（如174）
    :return: 解析后的产品详细信息字典，失败返回None
    """
    # 基础URL + 动态拼接参数
    base_url = api_config["DATA_API_URL"]
    url = f"{base_url}?productId={product_id}&type=0"

    try:
        # 初始化 LangChain 封装的请求工具
        requests_wrapper = TextRequestsWrapper()

        # 发送 GET 请求（返回字符串）
        response_str = requests_wrapper.get(url)

        # 解析 JSON（直接用 json.loads，不要用 eval！）
        result = json.loads(response_str)

        # 校验业务状态码
        if result.get("code") != 20000:
            print(f"接口业务异常：{result.get('msg', '未知错误')}")
            return None

        # 返回产品详情
        return result.get("data")

    except json.JSONDecodeError:
        print("接口返回数据不是合法JSON")
        return None
    except Exception as e:
        print(f"请求/解析失败：{str(e)}")
        return None

