"""
Configuration management using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-realtime-preview-2024-12-17"

    # Search API Configuration
    serper_api_key: str = ""

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    log_level: str = "INFO"

    # CORS Settings
    allowed_origins: str = "*"

    # Audio Configuration
    audio_sample_rate: int = 24000
    audio_channels: int = 1
    audio_chunk_size: int = 480

    # Session Configuration
    session_timeout_minutes: int = 60
    max_concurrent_sessions: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins string into a list."""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def openai_realtime_url(self) -> str:
        """Get OpenAI Realtime API WebSocket URL."""
        return f"wss://api.openai.com/v1/realtime?model={self.openai_model}"


# Global settings instance
settings = Settings()
