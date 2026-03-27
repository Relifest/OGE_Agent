# 运行说明

## 安装依赖
```bash
pip install -r requirements.txt
```

## 启动服务
```bash
python app/main.py
```

或者使用 uvicorn 直接启动:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API 接口文档
服务启动后，访问以下地址查看 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口说明

### 1. 同步查询接口
```http
POST /api/agent/query
Content-Type: application/json

{
  "query": "平台内的Landsat系列产品有哪些子产品？大致介绍一下"
}
```

响应：
```json
{
  "success": true,
  "data": {
    "response": "Landsat系列产品包括..."
  }
}
```

### 2. 流式查询接口
```http
POST /api/agent/query/stream
Content-Type: application/json

{
  "query": "平台内的Landsat系列产品有哪些子产品？大致介绍一下"
}
```

响应为流式文本内容。

### 3. 健康检查接口
```http
GET /api/agent/health
```

响应：
```json
{
  "status": "healthy",
  "service": "OGE智能助手"
}
```

## 配置说明
- 服务配置: `config/server.yml`
- API配置: `config/api.yml`
- Agent配置: `config/agent.yml`

## 目录结构
```
OGE-Agent/
├── app/                    # FastAPI应用
│   ├── __init__.py
│   ├── main.py            # 主应用入口
│   ├── routers/           # 路由模块
│   │   ├── __init__.py
│   │   └── agent.py       # Agent相关路由
│   └── schemas.py         # Pydantic模型
├── agent/                 # Agent核心代码
│   ├── __init__.py
│   ├── react_agent.py     # ReactAgent类
│   └── tools/             # 工具模块
├── model/                 # 模型工厂
├── utils/                 # 工具类
│   └── config_handler.py  # 配置加载
├── config/                # 配置文件
│   ├── server.yml         # 服务配置
│   ├── api.yml            # API配置
│   ├── agent.yml          # Agent配置
│   └── ...
├── requirements.txt       # 依赖文件
└── README_API.md          # API文档
```
