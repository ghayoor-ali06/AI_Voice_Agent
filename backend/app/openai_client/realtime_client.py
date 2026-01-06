"""
OpenAI Realtime API WebSocket client.
"""
import json
import asyncio
import aiohttp
from typing import Optional, Callable, Dict, Any

from ..config import settings
from ..utils.logger import logger
from ..utils.exceptions import OpenAIException
from .prompts import get_voice_settings


class RealtimeClient:
    """
    Client for OpenAI Realtime API via WebSocket.
    """

    def __init__(self, api_key: str, model: str = None, tools: list = None):
        """
        Initialize Realtime API client.

        Args:
            api_key: OpenAI API key
            model: Model name (default from settings)
            tools: List of tool definitions
        """
        self.api_key = api_key
        self.model = model or settings.openai_model
        self.tools = tools or []
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self._event_handlers: Dict[str, Callable] = {}
        self._receive_task: Optional[asyncio.Task] = None
        self._connected = False

        logger.info(f"Realtime client initialized (model: {self.model})")

    async def connect(self) -> None:
        """
        Establish WebSocket connection to OpenAI Realtime API.

        Raises:
            OpenAIException: If connection fails
        """
        try:
            url = settings.openai_realtime_url
            logger.info(f"Connecting to OpenAI Realtime API: {url}")

            # Create aiohttp session
            self.session = aiohttp.ClientSession()

            # Create WebSocket connection with custom headers
            self.ws = await self.session.ws_connect(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "OpenAI-Beta": "realtime=v1"
                },
                heartbeat=20
            )

            self._connected = True
            logger.info("Connected to OpenAI Realtime API")

            # Start receiving messages
            self._receive_task = asyncio.create_task(self._receive_loop())

            # Initialize session with configuration
            await self.initialize_session()

        except Exception as e:
            logger.error(f"Failed to connect to OpenAI Realtime API: {e}")
            raise OpenAIException(f"Connection failed: {e}")

    async def initialize_session(self) -> None:
        """Initialize session with voice settings and tools."""
        try:
            settings_config = get_voice_settings(self.tools)
            await self.send_event({
                "type": "session.update",
                "session": settings_config
            })
            logger.info("Session initialized with voice settings and tools")

        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            raise OpenAIException(f"Session initialization failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from OpenAI Realtime API."""
        self._connected = False

        # Cancel receive task
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        # Close WebSocket
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")

        # Close session
        if self.session:
            try:
                await self.session.close()
            except Exception as e:
                logger.error(f"Error closing session: {e}")

        logger.info("Disconnected from OpenAI Realtime API")

    async def send_event(self, event: Dict[str, Any]) -> None:
        """
        Send an event to OpenAI Realtime API.

        Args:
            event: Event dictionary

        Raises:
            OpenAIException: If not connected or send fails
        """
        if not self._connected or not self.ws:
            raise OpenAIException("Not connected to OpenAI Realtime API")

        try:
            await self.ws.send_str(json.dumps(event))
            logger.debug(f"Sent event: {event.get('type')}")

        except Exception as e:
            logger.error(f"Failed to send event: {e}")
            raise OpenAIException(f"Send failed: {e}")

    async def send_audio(self, audio_base64: str) -> None:
        """
        Send audio data to OpenAI.

        Args:
            audio_base64: Base64-encoded PCM16 audio
        """
        await self.send_event({
            "type": "input_audio_buffer.append",
            "audio": audio_base64
        })

    async def commit_audio_buffer(self) -> None:
        """Commit the audio buffer to trigger processing."""
        await self.send_event({
            "type": "input_audio_buffer.commit"
        })

    async def create_response(self) -> None:
        """Trigger response generation."""
        await self.send_event({
            "type": "response.create"
        })

    async def cancel_response(self) -> None:
        """Cancel ongoing response."""
        await self.send_event({
            "type": "response.cancel"
        })

    async def send_function_output(self, call_id: str, output: str) -> None:
        """
        Send function call output back to OpenAI.

        Args:
            call_id: Function call ID
            output: JSON string with function result
        """
        await self.send_event({
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": output
            }
        })

        # Trigger response generation with function result
        await self.create_response()

    async def _receive_loop(self) -> None:
        """Background task for receiving messages from OpenAI."""
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        event = json.loads(msg.data)
                        await self._handle_event(event)

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse event: {e}")
                    except Exception as e:
                        logger.error(f"Error handling event: {e}", exc_info=True)

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {self.ws.exception()}")
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    logger.info("WebSocket closed")
                    break

        except asyncio.CancelledError:
            logger.info("Receive loop cancelled")
        except Exception as e:
            logger.error(f"Receive loop error: {e}", exc_info=True)
        finally:
            self._connected = False

    async def _handle_event(self, event: Dict[str, Any]) -> None:
        """
        Handle incoming event from OpenAI.

        Args:
            event: Event dictionary
        """
        event_type = event.get("type")
        logger.debug(f"Received event: {event_type}")

        # Call registered handler
        handler = self._event_handlers.get(event_type)
        if handler:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}", exc_info=True)

        # Log errors
        if event_type == "error":
            logger.error(f"OpenAI error: {event.get('error')}")

    def on(self, event_type: str, handler: Callable) -> None:
        """
        Register an event handler.

        Args:
            event_type: Event type to handle
            handler: Async callback function
        """
        self._event_handlers[event_type] = handler
        logger.debug(f"Registered handler for event: {event_type}")

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected and self.ws is not None
