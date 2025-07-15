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

## 配置文件说明
### yupp.json

包含Yupp账户信息的JSON数组：

```json
[
  {
    "token": "your_yupp_session_token_here"
  }
]
```

### client_api_keys.json

包含允许访问API的客户端密钥的JSON数组：

```json
[
  "sk-your-api-key-1",
  "sk-your-api-key-2"
]
```

### model.json

包含支持的模型信息的JSON数组：

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