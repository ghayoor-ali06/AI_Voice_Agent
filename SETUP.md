# Quick Setup Guide

Follow these steps to get your AI Voice Agent running in minutes!

## Step 1: Install Dependencies

Open a terminal and navigate to the backend directory:

```bash
cd "/home/ghayoor-ali/Desktop/voice agents/backend"
```

Create a virtual environment and install packages:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment

Create your configuration file:

```bash
cp .env.example .env
```

Edit the `.env` file and add your OpenAI API key:

```bash
nano .env  # or use any text editor
```

**Required:**
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

**Optional (for better web search):**
```env
SERPER_API_KEY=your-serper-api-key-here
```

Get a Serper API key (free): https://serper.dev

## Step 3: Start the Backend Server

From the backend directory with venv activated:

```bash
python -m app.main
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!**

## Step 4: Open the Frontend

Open a new terminal or file manager and navigate to:

```bash
cd "/home/ghayoor-ali/Desktop/voice agents/frontend"
```

Then open `index.html` in your browser:

- **Double-click** `index.html`, or
- Right-click → Open with → Your Browser, or
- Drag and drop into browser window

## Step 5: Start Talking!

1. **Click the microphone button** 🎤
2. **Allow microphone access** when your browser asks
3. **Start speaking!** The agent will respond with voice
4. **Try asking:**
   - "What's the weather like in London?"
   - "Search for the latest news about AI"
   - "What time is it in Tokyo?"
   - "Tell me about the OpenAI Realtime API"

## Troubleshooting

### "Microphone access denied"
- Click the lock icon in your browser's address bar
- Allow microphone permissions
- Refresh the page

### "Failed to connect"
- Make sure the backend server is running (Step 3)
- Check the WebSocket URL in the frontend: `ws://localhost:8000/ws/voice`
- Check firewall isn't blocking port 8000

### "OpenAI error" or "API key invalid"
- Verify your OpenAI API key in `.env`
- Make sure you have access to GPT-4o Realtime API
- Check your OpenAI account has credits

### Audio not working
- Use Chrome or Edge (best Web Audio API support)
- Check your microphone works in other apps
- Make sure volume isn't muted

## Testing the Connection

### Test 1: Backend Health Check

Open in your browser: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "model": "gpt-4o-realtime-preview-2024-12-17",
  ...
}
```

### Test 2: API Documentation

Visit: http://localhost:8000/docs

You should see FastAPI's interactive documentation.

### Test 3: Frontend Connection

Open the frontend HTML file. The status should show:
- Connection: **Connected** (green dot)
- Agent Status: **Idle**

## What to Try

### Basic Conversation
- "Hello, how are you?"
- "What can you help me with?"
- "Tell me a joke"

### Web Search Queries
- "What's the current temperature in Paris?"
- "Who won the latest Super Bowl?"
- "What are the top news stories today?"
- "Search for information about FastAPI"

### Interruptions
- Start asking a question
- While the agent is responding, interrupt by speaking
- The agent should stop and listen to you

## Next Steps

### Customize the Agent

Edit `backend/app/openai_client/prompts.py` to change:
- Agent personality
- Voice style (alloy, echo, shimmer)
- Response length
- Interaction style

### Add More Tools

See `backend/README.md` for how to add custom tools like:
- Database queries
- Calendar integration
- Email sending
- Custom APIs

### Deploy to Production

See the main `README.md` for production deployment considerations.

## Need Help?

Check the main README.md for:
- Detailed troubleshooting
- Architecture explanation
- API documentation
- Performance tuning

---

**That's it! You're ready to chat with your AI voice agent! 🎉**
