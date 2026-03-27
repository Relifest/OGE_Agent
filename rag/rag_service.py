"""
总结服务类：用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型总结回复
"""
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts, load_data_info_search_prompts


def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt


class RagService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

        self.retriever_for_data = self.vector_store.get_retriever()
        self.prompt_text_for_data = load_data_info_search_prompts()
        self.prompt_template_for_data = PromptTemplate.from_template(self.prompt_text_for_data)
        self.chain_for_data = self._init_chain_for_data()

    def _init_chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chain

    def _init_chain_for_data(self):
        chain = self.prompt_template_for_data | print_prompt | self.model | StrOutputParser()
        return chain

    def retriever_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)

    def retriever_docs_for_data(self, query: str) -> list[Document]:
        return self.retriever_for_data.invoke(query)

    def basic_info_search(self, query: str) -> str:
        context_docs = self.retriever_docs(query)
        context = ""
        counter = 0

        for doc in context_docs:
            counter += 1
            context += f"【参考资料{counter}】：参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"

        return self.chain.invoke(
            {
                "input": query,
                "context": context
            }
        )

    def data_info_search(self, query: str) -> str:
        context_docs = self.retriever_docs_for_data(query)
        context = ""

        for doc in context_docs:
            context += f"参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"

        return self.chain_for_data.invoke(
            {
                "input": query,
                "context": context
            }
        )


# if __name__ == '__main__':
#     rag = RagService()
#     print(rag.data_info_search("Landsat系列产品具体有哪些产品？"))
