from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model


prompt = PromptTemplate.from_template("你是一个智能对话助手，请回答我的问题：{input}")
chain = prompt | chat_model | StrOutputParser()
print(chain.invoke({"input": "你的功能是什么"}))
