# OGE Agent

一个基于 LangChain 的智能 AI Agent 系统，专为 OGE 平台设计，集成了 RAG（检索增强生成）、Milvus 向量数据库、Redis 长期记忆和 FastAPI 服务网关。

## 功能特性

- **智能问答**：基于 RAG 技术实现 OGE 平台知识库的精准问答
- **长期记忆**：通过 Redis 实现对话历史持久化，支持多用户多会话隔离
- **工具调用**：封装 OGE 数据检索和模型信息查询接口为 Agent 工具
- **流式响应**：支持实时流式输出，提升用户体验
- **API 网关**：基于 FastAPI 提供标准化的 RESTful API 接口
- **意图识别**：自动识别用户意图并选择合适的处理策略

## 技术栈

- **核心框架**：LangChain / LangGraph
- **向量数据库**：Milvus
- **长期记忆**：Redis
- **Web 框架**：FastAPI
- **编程语言**：Python 3.10+
- **监控调试**：LangSmith

## 项目结构

```
OGE-Agent/
├── agent/              # Agent 核心逻辑
│   ├── react_agent.py  # 主要 Agent 实现
│   └── tools/          # 自定义工具集
├── app/                # FastAPI 应用
│   ├── main.py         # 应用入口
│   └── routers/        # API 路由
├── config/             # 配置文件
├── data/               # 原始数据和知识库
├── model/              # LLM 模型工厂
├── prompts/            # 提示词模板
├── rag/                # RAG 相关实现
├── scripts/            # 工具脚本
├── test/               # 测试代码
├── utils/              # 工具函数
└── requirements.txt    # 依赖包列表
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/Relifest/OGE_Agent.git
cd OGE_Agent

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件并配置必要的环境变量：

```env
# LLM 配置
LLM_PROVIDER=openai  # 或其他支持的提供商
OPENAI_API_KEY=your_openai_api_key

# Milvus 配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# LangSmith 配置（可选）
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=oge
```

### 3. 数据准备

运行数据处理脚本加载知识库到 Milvus：

```bash
# 处理产品数据
python scripts/process_product_data.py

# 加载数据到 Milvus
python scripts/load_product_data_to_milvus.py
```

### 4. 启动服务

```bash
# 启动 FastAPI 服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 测试 API

```bash
# 单次查询
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "请介绍一下OGE平台"}'

# 带会话历史的查询
curl -X POST http://localhost:8000/agent/query-with-history \
  -H "Content-Type: application/json" \
  -d '{
    "query": "你能记住我刚才问的问题吗？",
    "user_id": "test_user",
    "session_id": "test_session"
  }'
```

## 核心功能

### RAG 知识库问答

系统通过 Milvus 向量数据库存储 OGE 平台文档，结合嵌入模型实现语义检索，为大模型提供相关上下文信息。

### 长期记忆对话

利用 Redis 实现对话状态管理：
- 支持多用户隔离
- 支持多会话管理
- 自动保存对话历史
- 上下文感知的响应生成

### 工具集成

预置的 Agent 工具包括：
- `basic_info_search`: 基础信息检索
- `data_series_search`: 数据系列查询
- `data_search`: 具体数据检索

## 开发与测试

### 运行测试

```bash
# 基础功能测试
python test/test_simple.py

# Agent 中间件测试
python test/test_agent_middleware.py

# API 接口测试
python test/test_api.py

# 对话历史测试
python scripts/test_conversation_history.py
```

### 调试工具

- 使用 LangSmith 进行 Agent 执行链路追踪
- 查看 `logs/` 目录下的详细日志
- 通过测试脚本验证各模块功能

## 配置说明

所有配置都位于 `config/` 目录下：

- `agent.yml`: Agent 行为配置
- `api.yml`: API 接口配置
- `milvus.yml`: Milvus 连接配置
- `redis.yml`: Redis 连接配置
- `rag.yml`: RAG 相关参数
- `prompts.yml`: 提示词配置

## 贡献指南

1. Fork 本仓库
2. 创建 feature 分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如需了解更多信息，请联系项目维护者。
