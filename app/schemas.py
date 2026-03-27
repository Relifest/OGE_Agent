from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class QueryRequest(BaseModel):
    query: str


class Message(BaseModel):
    role: str = Field(..., description="消息角色，如 'user' 或 'assistant'")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="完整的消息历史列表")
    user_id: str = Field(..., description="用户唯一标识符")
    session_id: str = Field(..., description="对话唯一标识符")
    stream: bool = Field(default=True, description="是否启用流式响应")


class ChatResponse(BaseModel):
    success: bool = Field(True, description="请求是否成功")
    data: Dict[str, Any] = Field(..., description="响应数据")
    message: Optional[str] = Field(None, description="错误信息（如果失败）")