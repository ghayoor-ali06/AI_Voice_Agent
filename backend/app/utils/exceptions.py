"""
Custom exceptions for the voice agent application.
"""


class VoiceAgentException(Exception):
    """Base exception for voice agent errors."""
    pass


class AudioException(VoiceAgentException):
    """Exception raised for audio processing errors."""
    pass


class WebSocketException(VoiceAgentException):
    """Exception raised for WebSocket communication errors."""
    pass


class OpenAIException(VoiceAgentException):
    """Exception raised for OpenAI API errors."""
    pass


class ToolException(VoiceAgentException):
    """Exception raised for tool execution errors."""
    pass


class SessionException(VoiceAgentException):
    """Exception raised for session management errors."""
    pass


class ConfigurationException(VoiceAgentException):
    """Exception raised for configuration errors."""
    pass
