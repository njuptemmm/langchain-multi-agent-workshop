from fastapi import APIRouter
from app.models.schemas import ChatRequest
from fastapi.responses import StreamingResponse
from app.agents.fitness_nutrition import analyze_nutrition, get_messages, clear_messages


router = APIRouter()


@router.post("/nutrition/stream")
async def nutrition_stream(request: ChatRequest):
    """流式营养分析"""
    return StreamingResponse(
        analyze_nutrition(request.message, request.image_url, request.thread_id),
        media_type="text/event-stream"
    )


@router.get("/nutrition/messages")
async def get_nutrition_messages(thread_id: str):
    """获取营养分析历史消息"""
    messages = get_messages(thread_id)
    return {"messages": messages}


@router.delete("/nutrition/messages")
async def clear_nutrition_messages(thread_id: str):
    """清空营养分析历史消息"""
    clear_messages(thread_id)
    return {"success": True}
