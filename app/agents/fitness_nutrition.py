from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
import os
from app.common.logger import logger
from langchain.messages import HumanMessage, AIMessage, AIMessageChunk
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from pathlib import Path

# 1.加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 2.web搜索工具，使用tavily作为web搜索工具
web_search = TavilySearch(
    max_results=5,
    topic="general"
)

# 3.多模态模型
model = init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    api_key=os.getenv("DASHSCOPE_API_KEY")
)

# 4.初始化checkpointer
_db_dir = Path(__file__).resolve().parent.parent.parent / "db"
_db_dir.mkdir(parents=True, exist_ok=True)
connection = sqlite3.connect(_db_dir / "fitness_nutrition.db", check_same_thread=False)
checkpointer = SqliteSaver(connection)
checkpointer.setup()

# 5.Agent系统提示词
system_prompt = """
你是一名面向健身人群的专业营养分析师。用户会通过文字描述或餐食照片记录饮食，请按以下流程操作：

1.识别餐食内容：若用户提供照片，辨识所有可见食物、烹饪方式及估算份量；若为文字描述，提取食物名称与份量。份量不明确时主动合理假设并注明。

2.营养数据检索：优先调用 web_search 工具，以「食物名称 + 营养成分 / 每100g / calories protein carbs」等为关键词，查询可靠营养数据（可参考中国食物成分表、品牌包装标注、常见健身营养数据库等）。对多种食物分别检索后再汇总。

3.计算本餐营养：基于识别结果与检索数据，计算本餐总量（不是每100g），必须给出以下六项及单位：
   - 总热量（kcal）
   - 蛋白质（g）
   - 碳水化合物（g）
   - 脂肪（g）
   - 膳食纤维（g）
   - 钠（mg）

4.结合会话历史汇总：若本次对话中用户已记录多餐，汇总【今日累计】上述六项，避免重复计入同一餐。

5.健身视角简评：结合增肌/减脂/维持等常见健身目标（用户未说明时可简要询问或给出通用建议），点评本餐蛋白质是否充足、碳水脂肪比例、钠是否偏高、纤维是否足够。

6.结构化输出：每次回复末尾用以下 Markdown 表格呈现（本餐一行，若有多餐则加今日累计一行）：

| 项目 | 热量(kcal) | 蛋白质(g) | 碳水(g) | 脂肪(g) | 膳食纤维(g) | 钠(mg) |
|------|-----------|----------|--------|--------|------------|--------|
| 本餐 | ... | ... | ... | ... | ... | ... |
| 今日累计 | ... | ... | ... | ... | ... | ... |

请严格优先调用 web_search 查询营养数据；检索不到时再基于专业知识合理估算，并标注「估算值」。
"""

# 6.创建Agent
agent = create_agent(
    model=model,
    tools=[web_search],
    checkpointer=checkpointer,
    system_prompt=system_prompt
)

# 流式对话
async def analyze_nutrition(prompt: str, image: str, thread_id: str):
    """调用 agent 分析餐食营养"""
    logger.info(f"[营养分析]: {prompt}, image: {image}, thread_id: {thread_id}")
    try:
        if not image or image.strip() == "":
            message = HumanMessage(content=prompt)
        else:
            message = HumanMessage(content=[
                {"type": "image", "url": image},
                {"type": "text", "text": prompt}
            ])

        for chunk, metadata in agent.stream(
            {"messages": [message]},
            {"configurable": {"thread_id": thread_id}},
            stream_mode="messages"
        ):
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                yield chunk.content

    except Exception as e:
        logger.error(f"\n[错误]: {str(e)}")
        yield "营养分析失败，请尝试用文字描述餐食内容，或重新上传更清晰的照片。"

# 清空会话
def clear_messages(thread_id: str):
    """清空会话"""
    logger.info(f"清空历史消息，thread_id: {thread_id}")
    checkpointer.delete_thread(thread_id)

# 查询会话历史
def get_messages(thread_id: str) -> list[dict[str, str]]:
    """获取会话历史"""
    logger.info(f"获取历史消息，thread_id: {thread_id}")

    checkpoint = checkpointer.get({"configurable": {"thread_id": thread_id}})

    if not checkpoint:
        return []

    channel_values = checkpoint.get("channel_values")
    if not channel_values:
        return []

    messages = channel_values.get("messages", [])
    if not messages:
        return []

    result = []
    for msg in messages:
        if not msg.content:
            continue

        if isinstance(msg, HumanMessage):
            result.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            result.append({"role": "assistant", "content": msg.content})

    return result
