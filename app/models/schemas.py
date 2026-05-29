from typing import Optional, List

from pydantic import BaseModel

# --- 2. 数据模型 ---
# 即为返回的数据模型
class ChatRequest(BaseModel):
    message: str
    image_url: Optional[str] = None #给出的是url地址
    thread_id: str # 由前端提交的thread_id，后端base thread_id进行消息关联