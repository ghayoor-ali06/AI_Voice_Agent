"""
WebSocket message handlers for voice agent communication.
"""
import json
import uuid
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any

from .manager import connection_manager
from ..openai_client.realtime_client import RealtimeClient
from ..openai_client.session_manager import session_manager
from ..tools.registry import tool_registry
from ..config import settings
from ..utils.logger import logger
from ..utils.exceptions import WebSocketException


class VoiceAgentHandler:
    """
    Handles WebSocket communication between client and OpenAI Realtime API.
    """

    def __init__(self, websocket: WebSocket, session_id: str):
        """
        Initialize voice agent handler.

        Args:
            websocket: Client WebSocket connection
            session_id: Unique session identifier
        """
        self.websocket = websocket
        self.session_id = session_id
        self.openai_client: RealtimeClient = None
        self.session = None

    async def handle_connection(self):
        """
        Main handler for WebSocket connection lifecycle.
        """
        try:
            # Connect client
            await connection_manager.connect(self.websocket, self.session_id)

            # Create session
            self.session = session_manager.create_session(self.session_id)

            # Initialize OpenAI client
            tool_definitions = tool_registry.get_all_definitions()
            self.openai_client = RealtimeClient(
                api_key=settings.openai_api_key,
                tools=tool_definitions
            )

            # Register OpenAI event handlers
            self._register_openai_handlers()

            # Connect to OpenAI
            await self.openai_client.connect()

            # Store OpenAI client in session
            self.session.openai_ws = self.openai_client
            self.session.client_ws = self.websocket

            # Send ready message to client
            await self.send_to_client({
                "type": "session.ready",
                "session_id": self.session_id
            })

            # Start handling client messages
            await self._handle_client_messages()

        except WebSocketDisconnect:
            logger.info(f"Client disconnected: {self.session_id}")
        except Exception as e:
            logger.error(f"Error in connection handler: {e}", exc_info=True)
            await self.send_error_to_client(f"Connection error: {str(e)}")
        finally:
            await self.cleanup()

    async def _handle_client_messages(self):
        """Handle incoming messages from client."""
        try:
            while True:
                # Receive message from client
                message = await self.websocket.receive_json()
                message_type = message.get("type")

                logger.debug(f"Received from client: {message_type}")

                # Update session activity
                if self.session:
                    self.session.update_activity()

                # Route message
                if message_type == "audio":
                    await self._handle_client_audio(message)
                elif message_type == "control":
                    await self._handle_control_message(message)
                else:
                    logger.warning(f"Unknown message type from client: {message_type}")

        except WebSocketDisconnect:
            raise
        except Exception as e:
            logger.error(f"Error handling client message: {e}", exc_info=True)
            raise

    async def _handle_client_audio(self, message: Dict[str, Any]):
        """
        Handle audio data from client.

        Args:
            message: Message with audio data
        """
        audio_data = message.get("data")
        if not audio_data:
            logger.warning("Received audio message without data")
            return

        try:
            # Send audio to OpenAI
            await self.openai_client.send_audio(audio_data)

        except Exception as e:
            logger.error(f"Error sending audio to OpenAI: {e}")
            await self.send_error_to_client("Failed to process audio")

    async def _handle_control_message(self, message: Dict[str, Any]):
        """
        Handle control messages from client.

        Args:
            message: Control message
        """
        action = message.get("action")

        if action == "commit_audio":
            await self.openai_client.commit_audio_buffer()
        elif action == "cancel_response":
            await self.openai_client.cancel_response()
        elif action == "interrupt":
            await self.openai_client.cancel_response()
            await self.send_to_client({"type": "agent.interrupted"})
        else:
            logger.warning(f"Unknown control action: {action}")

    def _register_openai_handlers(self):
        """Register event handlers for OpenAI events."""

        # Session events
        self.openai_client.on("session.created", self._on_session_created)
        self.openai_client.on("session.updated", self._on_session_updated)

        # Audio response events
        self.openai_client.on("response.audio.delta", self._on_audio_delta)
        self.openai_client.on("response.audio.done", self._on_audio_done)

        # Function calling events
        self.openai_client.on("response.function_call_arguments.done", self._on_function_call)

        # Interruption events
        self.openai_client.on("input_audio_buffer.speech_started", self._on_speech_started)
        self.openai_client.on("input_audio_buffer.speech_stopped", self._on_speech_stopped)

        # Response events
        self.openai_client.on("response.done", self._on_response_done)

        # Error events
        self.openai_client.on("error", self._on_error)

    async def _on_session_created(self, event: Dict[str, Any]):
        """Handle session.created event."""
        logger.info(f"OpenAI session created: {event.get('session', {}).get('id')}")

    async def _on_session_updated(self, event: Dict[str, Any]):
        """Handle session.updated event."""
        logger.info("OpenAI session updated")

    async def _on_audio_delta(self, event: Dict[str, Any]):
        """
        Handle audio response chunks from OpenAI.

        Args:
            event: Audio delta event
        """
        audio_data = event.get("delta")
        if audio_data:
            await self.send_to_client({
                "type": "audio",
                "data": audio_data
            })

    async def _on_audio_done(self, event: Dict[str, Any]):
        """Handle audio response completion."""
        logger.debug("Audio response completed")
        await self.send_to_client({
            "type": "audio.done"
        })

    async def _on_function_call(self, event: Dict[str, Any]):
        """
        Handle function call from OpenAI.

        Args:
            event: Function call event
        """
        call_id = event.get("call_id")
        function_name = event.get("name")
        arguments_str = event.get("arguments")

        logger.info(f"Function call: {function_name}")

        try:
            # Parse arguments
            arguments = json.loads(arguments_str) if arguments_str else {}

            # Notify client
            await self.send_to_client({
                "type": "tool_call",
                "name": function_name,
                "arguments": arguments
            })

            # Execute tool
            result = await tool_registry.execute(function_name, arguments)

            # Send result back to OpenAI
            await self.openai_client.send_function_output(
                call_id=call_id,
                output=json.dumps(result)
            )

            # Notify client of result
            await self.send_to_client({
                "type": "tool_result",
                "name": function_name,
                "result": result
            })

        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}", exc_info=True)

            # Send error back to OpenAI
            error_result = {
                "success": False,
                "error": str(e)
            }
            await self.openai_client.send_function_output(
                call_id=call_id,
                output=json.dumps(error_result)
            )

    async def _on_speech_started(self, event: Dict[str, Any]):
        """Handle user speech started (interruption)."""
        logger.debug("User started speaking - interruption detected")
        await self.send_to_client({
            "type": "agent.interrupted",
            "message": "User started speaking"
        })

    async def _on_speech_stopped(self, event: Dict[str, Any]):
        """Handle user speech stopped."""
        logger.debug("User stopped speaking")
        await self.send_to_client({
            "type": "agent.listening"
        })

    async def _on_response_done(self, event: Dict[str, Any]):
        """Handle response completion."""
        logger.debug("Response completed")
        await self.send_to_client({
            "type": "response.done"
        })

    async def _on_error(self, event: Dict[str, Any]):
        """Handle error from OpenAI."""
        error = event.get("error", {})
        error_message = error.get("message", "Unknown error")
        logger.error(f"OpenAI error: {error_message}")

        await self.send_to_client({
            "type": "error",
            "error": error_message
        })

    async def send_to_client(self, message: Dict[str, Any]):
        """
        Send message to client.

        Args:
            message: Message dictionary
        """
        try:
            await connection_manager.send_message(self.session_id, message)
        except Exception as e:
            logger.error(f"Failed to send to client: {e}")

    async def send_error_to_client(self, error: str):
        """
        Send error message to client.

        Args:
            error: Error message
        """
        await self.send_to_client({
            "type": "error",
            "error": error
        })

    async def cleanup(self):
        """Clean up resources."""
        logger.info(f"Cleaning up handler: {self.session_id}")

        # Disconnect OpenAI client
        if self.openai_client:
            try:
                await self.openai_client.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting OpenAI client: {e}")

        # Remove session
        if self.session:
            try:
                await session_manager.remove_session(self.session_id)
            except Exception as e:
                logger.error(f"Error removing session: {e}")

        # Disconnect client
        try:
            await connection_manager.disconnect(self.session_id)
        except Exception as e:
            logger.error(f"Error disconnecting client: {e}")


async def handle_voice_agent_connection(websocket: WebSocket):
    """
    Handler function for voice agent WebSocket endpoint.

    Args:
        websocket: WebSocket connection
    """
    # Generate unique session ID
    session_id = str(uuid.uuid4())

    # Create and run handler
    handler = VoiceAgentHandler(websocket, session_id)
    await handler.handle_connection()
