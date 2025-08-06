# Yupp2API

This project is an API adapter that converts the Yupp.ai API into an OpenAI-compatible API format, allowing Yupp.ai's models to be used in applications that support the OpenAI API.
## Features
- Supports OpenAI compatible API interface
- - Automatically rotates multiple Yupp accounts
- Supports streaming output- Error handling and automatic retries
- Supports reasoning output- Detailed debugging log system
- Intelligent content filtering and deduplication mechanism

##Configuration file description
### yupp.json

JSON array containing Yupp account information：

```json
[
  {
    "token": "your_yupp_session_token_here"
  }
]
```

### client_api_keys.json

A JSON array containing the client key that allows access to the API.：

```json
[
  "sk-your-api-key-1",
  "sk-your-api-key-2"
]
```

### model.json

A JSON array containing information about supported models.：

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
