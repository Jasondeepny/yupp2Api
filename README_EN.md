# Yupp2API

A powerful API adapter that converts Yupp.ai's API to OpenAI-compatible format, enabling seamless integration with applications that support OpenAI API.

## Features

- **OpenAI Compatible API Interface**: Full compatibility with OpenAI API endpoints
- **Multi-Account Rotation**: Automatic rotation across multiple Yupp accounts for better reliability
- **Streaming Support**: Real-time streaming responses for better user experience
- **Error Handling & Auto-Retry**: Robust error handling with automatic retry mechanisms
- **Reasoning Process Support**: Support for thinking process (reasoning) output
- **Comprehensive Debug Logging**: Detailed logging system for troubleshooting
- **Smart Content Filtering**: Intelligent content filtering and deduplication mechanisms
- **Modern FastAPI Lifespan Management**: Optimized application lifecycle management
- **Optimized Network Configuration**: Enhanced network request configurations

## Tech Stack

- **FastAPI**: Modern Python web framework
- **Pydantic v2**: Data validation and serialization
- **Requests**: HTTP client library
- **Uvicorn**: ASGI server
- **Python 3.8+**: Async programming support

## Configuration

The project uses environment variables for configuration, simplifying deployment and management.

### Environment Variables

Copy the `env.example` file to `.env` and fill in the actual values:

```bash
cp env.example .env
```

### Proxy Configuration

If you need to use a proxy, configure it in the `.env` file:

```bash
# HTTP/HTTPS Proxy
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
NO_PROXY=localhost,127.0.0.1

# Or SOCKS Proxy
HTTP_PROXY=socks5://proxy.example.com:1080
HTTPS_PROXY=socks5://proxy.example.com:1080
NO_PROXY=localhost,127.0.0.1
```

**Note**: If no proxy is configured, the system disables all proxies by default (`NO_PROXY=*`).

### Model Configuration File

Model configuration must use file-based approach. The default filename is `model.json`, which can be customized via environment variables:

**Environment Variables**:

- `MODEL_FILE`: Model configuration filename (default: `model.json`)
- `MODEL_FILE_PATH`: File path for Docker mounting (default: `./model.json`)

**File Content**:

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

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example configuration file
cp env.example .env

# Edit configuration file with actual API keys and tokens
nano .env
```

### 3. Start the Service

```bash
python yyapi.py
```

The service will start at `http://localhost:${PORT:-8001}`.

### 4. Verify the Service

```bash
# Check model list
curl http://localhost:${PORT:-8001}/models

# Test chat interface
curl -X POST http://localhost:${PORT:-8001}/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-api-key" \
  -d '{
    "model": "claude-3.7-sonnet:thinking",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Docker Deployment

### 1. Configure Environment Variables

```bash
# Copy example configuration file
cp env.example .env

# Edit configuration file with actual API keys and tokens
vi .env
```

### 2. Start the Service

```bash
# Build and start container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

### 3. Verify the Service

```bash
# Check container status
docker-compose ps

# Check model list
curl http://localhost:${PORT:-8001}/models
```

## Model Data Fetching Tool

The project includes an independent model data fetching tool `model.py` for retrieving the latest model list from Yupp.ai API:

```bash
# Set environment variables
export YUPP_TOKENS="your_yupp_token_here"

# Run model data fetching tool
python model.py
```

This tool will:

- Fetch the latest model list from Yupp.ai API
- Filter and process model data
- Save to `model.json` file
- Support environment variable configuration without dependency on `yupp.json` file

## Configuration Testing

Verify environment variable configuration:

```bash
# Test main application configuration
python -c "from yyapi import main; print('Configuration correct')"

# Test model fetching tool configuration
python -c "from model import YuppConfig; print('Model tool configuration correct')"
```

## API Endpoints

### Authentication Required Endpoints

- `GET /v1/models` - List available models (requires client API key)
- `POST /v1/chat/completions` - Create chat completions (requires client API key)

### Public Endpoints

- `GET /models` - List available models (no authentication required)

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CLIENT_API_KEYS` | Client API keys (comma-separated) | - | Yes |
| `YUPP_TOKENS` | Yupp.ai tokens (comma-separated) | - | Yes |
| `HOST` | Server host | `0.0.0.0` | No |
| `PORT` | Server port | `8001` | No |
| `DEBUG_MODE` | Enable debug mode | `false` | No |
| `MAX_ERROR_COUNT` | Max error count per account | `3` | No |
| `ERROR_COOLDOWN` | Error cooldown time (seconds) | `300` | No |
| `MODEL_FILE` | Model configuration filename | `model.json` | No |
| `MODEL_FILE_PATH` | Model file path for Docker | `./model.json` | No |
| `HTTP_PROXY` | HTTP proxy URL | - | No |
| `HTTPS_PROXY` | HTTPS proxy URL | - | No |
| `NO_PROXY` | No proxy list | `*` | No |

## Error Handling

The system includes comprehensive error handling:

- **Account Rotation**: Automatically switches between multiple Yupp accounts
- **Error Tracking**: Tracks error counts per account
- **Cooldown Period**: Temporarily disables accounts with too many errors
- **Retry Logic**: Automatic retry for transient failures
- **Graceful Degradation**: Continues operation even if some accounts fail

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please:

1. Check the debug logs (enable `DEBUG_MODE=true`)
2. Verify your environment variable configuration
3. Ensure your Yupp.ai tokens are valid
4. Check the model configuration file
