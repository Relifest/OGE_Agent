import os
import hashlib
from langchain_community.document_loaders import PyPDFLoader, TextLoader, BSHTMLLoader
from langchain_core.documents import Document
from utils.logger_handler import logger


def get_file_md5_hex(file_path: str):
    """
    获取文件的md5的十六进制字符串
    :param file_path: 文件路径
    :return:
    """
    if not os.path.exists(file_path):
        logger.error(f"[md5计算]文件{file_path}不存在")
        return

    if not os.path.isfile(file_path):
        logger.error(f"[md5计算]路径{file_path}不是文件")
        return

    md5_obj = hashlib.md5()

    chunk_size = 4096
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
                md5_hex = md5_obj.hexdigest()
                return md5_hex
    except Exception as e:
        logger.error(f"计算文件{file_path}md5失败，{str(e)}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):
    """
    返回文件夹内的文件列表（允许的文件后缀）
    :param path: 文件夹路径
    :param allowed_types: 允许的文件类型
    :return: 文件名
    """
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]{path}不是文件夹")
        return allowed_types

    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path, f))

    return tuple(files)


def pdf_loader(file_path: str, passwd=None) -> list[Document]:
    """
    加载 pdf 文件
    :param file_path: 文件路径
    :param passwd: 密码
    :return: 加载结果
    """
    return PyPDFLoader(file_path, passwd).load()


def txt_loader(file_path: str) -> list[Document]:
    """
    加载 txt 文件
    :param file_path: 文件路径
    :return: 加载结果
    """
    return TextLoader(file_path, encoding="utf-8").load()


def html_loader(file_path: str) -> list[Document]:
    """
    加载 html 文件
    :param file_path: 文件路径
    :return: 加载结果
    """
    loader = BSHTMLLoader(
        file_path=file_path,
        open_encoding="utf-8"
    )
    return loader.load()