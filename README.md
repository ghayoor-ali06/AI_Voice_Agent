# AI Voice Agent

A complete real-time voice agent powered by OpenAI's GPT-4o Realtime API. This application enables natural voice conversations with AI, featuring automatic interruption handling, web search capabilities, and a clean, modern interface.

## ✨ Features

- **Real-time Voice Conversations**: Sub-second latency for natural dialogue
- **Intelligent Interruption Handling**: Automatically detects when you start speaking
- **Web Search Integration**: Agent can search the web when it doesn't know the answer
- **Echo Cancellation**: Browser-native echo cancellation for clear audio
- **Clean Architecture**: Well-organized, production-ready codebase
- **Easy to Extend**: Simple tool system for adding new capabilities

## 🏗️ Architecture

```
┌─────────────┐          ┌──────────────┐          ┌─────────────────┐
│   Browser   │ ←─WS───→ │ FastAPI      │ ←─WS───→ │ OpenAI Realtime │
│  (Frontend) │          │  (Backend)   │          │      API        │
└─────────────┘          └──────────────┘          └─────────────────┘
                                 ↓
                         ┌──────────────┐
                         │  Web Search  │
                         │   (Serper/   │
                         │  DuckDuckGo) │
                         └──────────────┘
```

### Data Flow

1. User speaks into microphone
2. Browser captures audio (Float32 → Int16 PCM → Base64)
3. WebSocket sends audio to FastAPI backend
4. Backend forwards to OpenAI Realtime API
5. OpenAI processes speech, generates response
6. If agent needs information, it calls web_search tool
7. Backend executes tool and returns result
8. OpenAI incorporates result and continues response
9. Audio response streams back through WebSocket
10. Browser plays audio to user

## 📋 Prerequisites

- Python 3.9 or higher
- OpenAI API key with access to GPT-4o Realtime
- Modern web browser (Chrome, Firefox, Edge)
- (Optional) Serper API key for enhanced web search

## 🚀 Quick Start

### 1. Set Up Backend

```bash
# Navigate to backend directory
cd "voice agents/backend"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Edit .env and add your OpenAI API key
# Required: OPENAI_API_KEY
# Optional: SERPER_API_KEY (for better web search)
nano .env  # or use your preferred editor
```

### 2. Start the Server

```bash
# Run the FastAPI server
python -m app.main

# Or use uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

### 3. Open the Frontend

Simply open the HTML file in your browser:

```bash
# Navigate to frontend directory
cd ../frontend

# Open index.html in your default browser
# On Linux:
xdg-open index.html

# On Mac:
open index.html

# On Windows:
start index.html

# Or just drag and drop index.html into your browser
```

### 4. Start Talking!

1. Click the microphone button to start
2. Allow microphone access when prompted
3. Start speaking naturally
4. The agent will respond with voice
5. You can interrupt the agent at any time by speaking

## 📁 Project Structure

```
voice agents/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application
│   │   ├── config.py                  # Configuration management
│   │   ├── websocket/
│   │   │   ├── manager.py             # WebSocket connection manager
│   │   │   └── handlers.py            # Message routing logic
│   │   ├── openai_client/
│   │   │   ├── realtime_client.py     # OpenAI Realtime API client
│   │   │   ├── session_manager.py     # Session lifecycle
│   │   │   └── prompts.py             # System prompts
│   │   ├── audio/
│   │   │   ├── encoder.py             # Audio encoding utilities
│   │   │   └── processor.py           # Audio processing
│   │   ├── tools/
│   │   │   ├── base.py                # Tool interface
│   │   │   ├── registry.py            # Tool management
│   │   │   └── web_search.py          # Web search tool
│   │   └── utils/
│   │       ├── logger.py              # Logging configuration
│   │       └── exceptions.py          # Custom exceptions
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   └── index.html                     # Single-page application
├── .gitignore
└── README.md
```

## ⚙️ Configuration

Edit `backend/.env` to configure:

```env
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-realtime-preview-2024-12-17

# Search API (Optional - falls back to DuckDuckGo)
SERPER_API_KEY=your_serper_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO

# CORS Settings
ALLOWED_ORIGINS=*

# Audio Configuration
AUDIO_SAMPLE_RATE=24000
AUDIO_CHANNELS=1
AUDIO_CHUNK_SIZE=480

# Session Configuration
SESSION_TIMEOUT_MINUTES=60
MAX_CONCURRENT_SESSIONS=10
```

## 🔧 Adding New Tools

The system is designed to be easily extensible. Here's how to add a new tool:

### 1. Create Tool Class

Create a new file in `backend/app/tools/`, for example `my_tool.py`:

```python
from .base import BaseTool
from typing import Dict, Any

class MyTool(BaseTool):
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "Description of what this tool does"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of parameter"
                }
            },
            "required": ["param1"]
        }

    async def execute(self, param1: str) -> Dict[str, Any]:
        # Your tool logic here
        result = f"Processed: {param1}"
        return {
            "success": True,
            "result": result
        }
```

### 2. Register Tool

Edit `backend/app/tools/registry.py` and add:

```python
def setup_tools() -> ToolRegistry:
    from .web_search import WebSearchTool
    from .my_tool import MyTool  # Add this import

    tool_registry.register(WebSearchTool())
    tool_registry.register(MyTool())  # Add this line

    return tool_registry
```

That's it! The agent will now be able to use your tool.

## 🎯 API Endpoints

### WebSocket: `/ws/voice`

Main endpoint for voice communication.

**Client → Server Messages:**

```json
// Send audio data
{
    "type": "audio",
    "data": "<base64-encoded-pcm16>"
}

// Control messages
{
    "type": "control",
    "action": "commit_audio" | "cancel_response" | "interrupt"
}
```

**Server → Client Messages:**

```json
// Session ready
{"type": "session.ready", "session_id": "uuid"}

// Audio response
{"type": "audio", "data": "<base64-encoded-pcm16>"}

// Tool execution
{"type": "tool_call", "name": "web_search", "arguments": {...}}
{"type": "tool_result", "name": "web_search", "result": {...}}

// Status updates
{"type": "agent.interrupted"}
{"type": "agent.listening"}
{"type": "audio.done"}
{"type": "response.done"}

// Errors
{"type": "error", "error": "error message"}
```

### HTTP: `/health`

Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "model": "gpt-4o-realtime-preview-2024-12-17",
    "audio_config": {
        "sample_rate": 24000,
        "channels": 1,
        "chunk_size": 480
    },
    "active_sessions": 0
}
```

### HTTP: `/`

API information endpoint.

## 🐛 Troubleshooting

### Microphone Not Working

- **Check browser permissions**: Ensure microphone access is allowed
- **HTTPS requirement**: Some browsers require HTTPS for microphone access (use localhost for development)
- **Check audio input**: Test your microphone in system settings

### Connection Issues

- **Firewall**: Ensure port 8000 is not blocked
- **WebSocket URL**: Verify the URL in the frontend matches your server address
- **CORS**: If using a different origin, update `ALLOWED_ORIGINS` in `.env`

### Audio Quality Issues

- **Sample rate**: Ensure your microphone supports 24kHz (most do)
- **Network**: WebSocket audio streaming requires stable connection
- **Browser**: Chrome and Edge have best Web Audio API support

### Agent Not Responding

- **API Key**: Verify OpenAI API key is valid and has Realtime API access
- **Logs**: Check backend logs for errors: `tail -f backend/app.log`
- **Tool Errors**: Check if web search is failing (needs API key or internet)

## 📊 Performance

- **Latency**: Typically 500-800ms for first response
- **Audio Quality**: 24kHz PCM16 for clear voice
- **Session Duration**: Up to 60 minutes per session
- **Concurrent Users**: Configurable (default: 10)

## 🔒 Security Considerations

- **API Keys**: Never expose OpenAI API key to frontend
- **CORS**: Configure `ALLOWED_ORIGINS` appropriately for production
- **Rate Limiting**: Consider adding rate limiting for production
- **Input Validation**: All tool inputs are validated
- **Session Timeout**: Automatic cleanup after 60 minutes

## 📈 Monitoring

The application includes comprehensive logging:

```python
# View logs in real-time
tail -f backend/app.log

# Log levels: DEBUG, INFO, WARNING, ERROR
# Configure in .env: LOG_LEVEL=INFO
```

Key metrics logged:
- Session creation/cleanup
- Tool execution times
- WebSocket connection events
- OpenAI API interactions
- Error rates and types

## 🚢 Production Deployment

For production deployment:

1. **Environment Variables**: Use secure secret management
2. **HTTPS**: Enable HTTPS for WebSocket security (WSS)
3. **Load Balancing**: Use sticky sessions for WebSocket connections
4. **Monitoring**: Add application monitoring (e.g., Sentry)
5. **Scaling**: Consider Redis for session state if running multiple instances
6. **Cost Management**: Monitor OpenAI API usage and set limits

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional tools (calendar, email, database queries)
- Enhanced error recovery
- Better audio visualization
- Conversation history
- Multi-language support
- WebRTC upgrade for better network handling

## 📄 License

MIT License - feel free to use this project for any purpose.

## 🙏 Acknowledgments

- Built with [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- Web search via [Serper API](https://serper.dev/) or [DuckDuckGo](https://duckduckgo.com/)

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all prerequisites are met
4. Verify API keys are valid

---

**Happy Voice Chatting! 🎤🤖**
