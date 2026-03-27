from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas import QueryRequest, ChatRequest, ChatResponse
from agent.react_agent import ReactAgent
from utils.logger_handler import logger

router = APIRouter()


@router.post("/query", response_model=ChatResponse)
async def query_endpoint(request: QueryRequest):
    """同步查询接口（兼容旧版本）"""
    try:
        agent = ReactAgent()
        response = ""
        for chunk in agent.execute_stream(request.query):
            response += chunk

        return ChatResponse(
            success=True,
            data={"response": response}
        )
    except Exception as e:
        logger.error(f"Query failed: {str(e)}", exc_info=True)
        return ChatResponse(
            success=False,
            data={},
            message=str(e)
        )


@router.post("/query/stream")
async def query_stream_endpoint(request: QueryRequest):
    """流式查询接口（兼容旧版本）"""
    try:
        agent = ReactAgent()

        async def generate():
            try:
                for chunk in agent.execute_stream(request.query):
                    yield chunk
            except Exception as e:
                logger.error(f"Stream query failed: {str(e)}", exc_info=True)
                yield f"Error: {str(e)}"

        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        logger.error(f"Stream endpoint failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """多轮对话接口（支持历史记录）"""
    try:
        if not request.messages:
            raise ValueError("消息列表不能为空")

        # 验证最后一条消息必须是用户消息
        latest_message = request.messages[-1]
        if latest_message.role != "user":
            raise ValueError("最后一条消息必须是用户消息")

        agent = ReactAgent()
        response = ""

        # 使用新的函数签名：只传入最后一条用户消息的content
        for chunk in agent.execute_stream_with_history(
            latest_message.content,  # 只传入用户query
            request.user_id,
            request.session_id
        ):
            response += chunk

        return ChatResponse(
            success=True,
            data={"response": response}
        )
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}", exc_info=True)
        return ChatResponse(
            success=False,
            data={},
            message=str(e)
        )


@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """多轮对话流式接口（支持历史记录）"""
    try:
        if not request.messages:
            raise ValueError("消息列表不能为空")

        # 验证最后一条消息必须是用户消息
        latest_message = request.messages[-1]
        if latest_message.role != "user":
            raise ValueError("最后一条消息必须是用户消息")

        agent = ReactAgent()

        async def generate():
            try:
                for chunk in agent.execute_stream_with_history(
                    latest_message.content,  # 只传入用户query
                    request.user_id,
                    request.session_id
                ):
                    yield chunk
            except Exception as e:
                logger.error(f"Stream chat failed: {str(e)}", exc_info=True)
                yield f"Error: {str(e)}"

        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        logger.error(f"Stream chat endpoint failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "OGE智能助手"
    }