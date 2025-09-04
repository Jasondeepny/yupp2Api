# Yupp2API

这个项目是一个API适配器，将Yupp.ai的API转换为OpenAI兼容的API格式，使得可以在支持OpenAI API的应用中使用Yupp.ai的模型。

## 功能特点

- 支持OpenAI兼容的API接口
- 自动轮换多个Yupp账户
- 支持流式输出
- 错误处理和自动重试
- 支持思考过程(reasoning)输出
- 详细的调试日志系统
- 智能内容过滤和去重机制
- 使用现代化的 FastAPI lifespan 管理
- 优化的网络请求配置

## 技术栈

- **FastAPI**: 现代化的 Python Web 框架
- **Pydantic v2**: 数据验证和序列化
- **Requests**: HTTP 客户端库
- **Uvicorn**: ASGI 服务器
- **Python 3.8+**: 支持异步编程

## 配置方式

项目使用环境变量配置，简化部署和管理。

### 环境变量配置

复制 `env.example` 文件为 `.env` 并填入实际值：

```bash
cp env.example .env
```

## 代理配置

如果需要使用代理，在 `.env` 文件中设置：

```bash
# HTTP/HTTPS 代理
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
NO_PROXY=localhost,127.0.0.1

# 或者 SOCKS 代理
HTTP_PROXY=socks5://proxy.example.com:1080
HTTPS_PROXY=socks5://proxy.example.com:1080
NO_PROXY=localhost,127.0.0.1
```

**注意**: 如果不设置代理，系统默认禁用所有代理（`NO_PROXY=*`）。

### 模型配置文件

模型配置文件必须使用文件方式，默认文件名为 `model.json`，可通过环境变量 `MODEL_FILE` 自定义：

**环境变量**:

- `MODEL_FILE`: 模型配置文件名（默认: `model.json`）
- `MODEL_FILE_PATH`: Docker 挂载时的文件路径（默认: `./model.json`）

**文件内容**:

```json
[
  {
    "id": "claude-3.7-sonnet:thinking",
    "name": "anthropic/claude-3.7-sonnet:thinking<>OPR",
    "label": "Claude 3.7 Sonnet (Thinking) (OpenRouter)",
    "publisher": "Anthropic",
    "family": "Claude"
  }
]
```

## 快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制示例配置文件
cp env.example .env

# 编辑配置文件，填入实际的 API 密钥和 token
nano .env
```

### 3. 启动服务

```bash
python yyapi.py
```

服务将在 `http://localhost:${PORT:-8001}` 启动。

### 4. 验证服务

```bash
# 检查模型列表
curl http://localhost:${PORT:-8001}/models

# 测试聊天接口
curl -X POST http://localhost:${PORT:-8001}/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-api-key" \
  -d '{
    "model": "claude-3.7-sonnet:thinking",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Docker 部署

### 1. 配置环境变量

```bash
# 复制示例配置文件
cp env.example .env

# 编辑配置文件，填入实际的 API 密钥和 token
nano .env
```

### 2. 启动服务

```bash
# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 验证服务

```bash
# 检查容器状态
docker-compose ps

# 检查模型列表
curl http://localhost:${PORT:-8001}/models
```

## 模型数据获取工具

项目包含一个独立的模型数据获取工具 `model.py`，用于从 Yupp.ai API 获取最新的模型列表：

```bash
# 设置环境变量
export YUPP_TOKENS="your_yupp_token_here"

# 运行模型数据获取工具
python model.py
```

该工具会：

- 从 Yupp.ai API 获取最新的模型列表
- 过滤和处理模型数据
- 保存到 `model.json` 文件
- 支持环境变量配置，无需依赖 `yupp.json` 文件

## 配置测试

验证环境变量配置：

```bash
# 测试主应用配置
python -c "from yyapi import main; print('配置正确')"

# 测试模型获取工具配置
python -c "from model import YuppConfig; print('模型工具配置正确')"
```
