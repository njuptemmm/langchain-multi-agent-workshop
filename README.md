# LangChain Multi-Agent Workshop — AI 私厨 & 健身营养分析

基于 [LangChain](https://python.langchain.com/) 与 [LangGraph](https://langchain-ai.github.io/langgraph/) 的多 Agent Web 应用。

- **AI 私人厨师**：上传食材图片，联网搜索并推荐食谱
- **健身营养分析**：识别餐食，统计热量、蛋白质、碳水、脂肪、膳食纤维、钠

## 项目结构

```
├── app/
│   ├── agents/
│   │   ├── personal_chef.py      # 私厨 Agent
│   │   └── fitness_nutrition.py  # 营养分析 Agent
│   ├── api/v1/
│   │   ├── chat.py               # 私厨 API
│   │   ├── nutrition.py          # 营养 API
│   │   └── oss.py                # OSS 图片上传签名
│   ├── static/                   # 前端静态页
│   └── main.py                   # FastAPI 入口
├── db/                           # SQLite 会话库（本地生成，已 gitignore）
├── langgraph.json                # LangSmith / langgraph dev 配置
├── pyproject.toml
└── .env.example                  # 环境变量模板
```

## 环境要求

- Python >= 3.13
- [uv](https://github.com/astral-sh/uv)（推荐）或 pip

## 快速开始

### 1. 克隆并安装依赖

```bash
git clone https://github.com/njuptemmm/langchain-multi-agent-workshop.git
cd langchain-multi-agent-workshop

uv sync
# 或: python -m venv .venv && pip install -e .
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入以下服务的 API Key（按需）：

| 变量 | 用途 | 是否必须 |
|------|------|----------|
| `DASHSCOPE_API_KEY` | 百炼多模态模型 | 是 |
| `TAVILY_API_KEY` | 网页搜索工具 | 是 |
| `OSS_*` | 餐食/食材图片上传 | 上传图片时需要 |
| `LANGSMITH_*` | Agent 调试追踪 | 可选 |

### 3. 启动 Web 服务

```bash
uv run python -m app.main
# 或: python -m app.main
```

| 页面 | 地址 |
|------|------|
| AI 私人厨师 | http://127.0.0.1:8001/ |
| 健身营养分析 | http://127.0.0.1:8001/nutrition.html |
| API 文档 | http://127.0.0.1:8001/docs |

### 4. LangSmith 本地调试（可选）

```bash
uv run langgraph dev
```

在 `langgraph.json` 中已配置两个 Agent：

- `chief_agent` — 私厨
- `fitness_nutrition_agent` — 营养分析

## API 一览

### 私厨

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/chat/stream` | 流式对话 |
| GET | `/api/v1/chat/messages` | 历史消息 |
| DELETE | `/api/v1/chat/messages` | 清空会话 |

### 营养分析

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/nutrition/stream` | 流式营养分析 |
| GET | `/api/v1/nutrition/messages` | 历史消息 |
| DELETE | `/api/v1/nutrition/messages` | 清空会话 |

### 通用

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/oss/presign` | 获取 OSS 预签名上传 URL |

请求体示例：

```json
{
  "message": "午餐吃了200g鸡胸肉和一碗米饭",
  "image_url": null,
  "thread_id": "nutrition-2026-05-29"
}
```

## 安全说明

1. **切勿提交 `.env`**，已写入 `.gitignore`
2. **使用 `.env.example` 作为模板**，不要上传真实密钥
3. 若密钥曾误提交，请立即在对应平台**轮换密钥**，并清理 Git 历史记录

## 技术栈

- LangChain / LangGraph — Agent 编排与记忆
- FastAPI + Uvicorn — Web 服务
- qwen3.5-plus（百炼）— 多模态大模型
- Tavily — 网页搜索
- SQLite（SqliteSaver）— 会话记忆
- 阿里云 OSS — 图片存储

## License

仅供学习交流使用。
