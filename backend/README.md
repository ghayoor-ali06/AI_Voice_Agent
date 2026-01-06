# AI Voice Agent - Backend

FastAPI-based backend for the AI Voice Agent, providing WebSocket communication with OpenAI's Realtime API.

## Installation

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Required configuration:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Optional configuration:

```env
SERPER_API_KEY=your_serper_api_key  # For enhanced web search
```

## Running the Server

### Development Mode

```bash
# Using Python module
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Architecture

### Core Components

- **FastAPI Application** (`app/main.py`): Main application with WebSocket endpoint
- **WebSocket Manager** (`websocket/manager.py`): Manages client connections
- **WebSocket Handlers** (`websocket/handlers.py`): Routes messages between client and OpenAI
- **OpenAI Realtime Client** (`openai_client/realtime_client.py`): Communicates with OpenAI API
- **Session Manager** (`openai_client/session_manager.py`): Manages active sessions
- **Tool Registry** (`tools/registry.py`): Manages and executes tools
- **Audio Utilities** (`audio/`): Handles audio encoding/decoding

### Message Flow

```
Client Audio → WebSocket Handler → OpenAI Client → OpenAI API
                                    ↓
                              Tool Registry (if function call)
                                    ↓
OpenAI Response → WebSocket Handler → Client
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

### Adding New Tools

1. Create a new tool in `app/tools/` inheriting from `BaseTool`
2. Implement required methods: `name`, `description`, `parameters`, `execute`
3. Register in `app/tools/registry.py` in the `setup_tools()` function

Example:

```python
from .base import BaseTool

class MyTool(BaseTool):
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "What this tool does"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            },
            "required": ["param"]
        }

    async def execute(self, param: str) -> dict:
        return {"result": f"Processed: {param}"}
```

### Testing

```bash
# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

## Logging

Logs are output to stdout with configurable levels:

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## Troubleshooting

### Connection Issues

Check if OpenAI API key is valid:

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### WebSocket Issues

Test WebSocket endpoint:

```bash
wscat -c ws://localhost:8000/ws/voice
```

### Audio Issues

Verify audio configuration matches frontend:

- Sample rate: 24000 Hz
- Channels: 1 (mono)
- Format: PCM16
- Encoding: Base64

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-realtime-preview-2024-12-17` | Model to use |
| `SERPER_API_KEY` | `""` | Serper API key for web search |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `true` | Debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins |
| `AUDIO_SAMPLE_RATE` | `24000` | Audio sample rate |
| `AUDIO_CHANNELS` | `1` | Audio channels |
| `AUDIO_CHUNK_SIZE` | `480` | Audio chunk size (samples) |
| `SESSION_TIMEOUT_MINUTES` | `60` | Session timeout |
| `MAX_CONCURRENT_SESSIONS` | `10` | Max concurrent sessions |

## Performance

- Handles up to 10 concurrent sessions by default
- Automatic session cleanup after 60 minutes
- Efficient audio streaming with minimal buffering
- Async/await throughout for non-blocking I/O

## Security

- API keys never exposed to frontend
- CORS properly configured
- Input validation on all tools
- Session timeout enforcement
- Comprehensive error handling
