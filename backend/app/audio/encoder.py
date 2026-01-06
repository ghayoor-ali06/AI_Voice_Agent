"""
Audio encoding/decoding utilities for PCM16 and Base64 conversion.
"""
import base64
import numpy as np
from typing import Optional


def base64_to_pcm16(base64_data: str) -> bytes:
    """
    Decode base64 string to PCM16 bytes.

    Args:
        base64_data: Base64 encoded audio data

    Returns:
        Raw PCM16 bytes
    """
    return base64.b64decode(base64_data)


def pcm16_to_base64(pcm_data: bytes) -> str:
    """
    Encode PCM16 bytes to base64 string.

    Args:
        pcm_data: Raw PCM16 bytes

    Returns:
        Base64 encoded string
    """
    return base64.b64encode(pcm_data).decode('utf-8')


def validate_pcm16_data(data: bytes) -> bool:
    """
    Validate PCM16 audio data.

    Args:
        data: Audio data to validate

    Returns:
        True if valid, raises ValueError otherwise
    """
    if len(data) == 0:
        raise ValueError("Empty audio chunk")
    if len(data) % 2 != 0:
        raise ValueError("Invalid PCM16 data (odd byte count)")
    return True


def pcm16_to_float32(pcm_data: bytes) -> np.ndarray:
    """
    Convert PCM16 bytes to float32 numpy array.

    Args:
        pcm_data: Raw PCM16 bytes

    Returns:
        Float32 numpy array normalized to [-1.0, 1.0]
    """
    int16_array = np.frombuffer(pcm_data, dtype=np.int16)
    float32_array = int16_array.astype(np.float32) / 32768.0
    return float32_array


def float32_to_pcm16(float_data: np.ndarray) -> bytes:
    """
    Convert float32 numpy array to PCM16 bytes.

    Args:
        float_data: Float32 array in range [-1.0, 1.0]

    Returns:
        Raw PCM16 bytes
    """
    # Clip values to valid range
    clipped = np.clip(float_data, -1.0, 1.0)
    # Convert to int16
    int16_array = (clipped * 32767).astype(np.int16)
    return int16_array.tobytes()


class AudioBuffer:
    """
    Buffer for accumulating audio chunks until reaching desired size.
    """

    def __init__(self, chunk_size: int = 480):
        """
        Initialize audio buffer.

        Args:
            chunk_size: Target chunk size in samples (default 480 = 20ms at 24kHz)
        """
        self.chunk_size = chunk_size * 2  # *2 for int16 (2 bytes per sample)
        self.buffer = bytearray()

    def add(self, data: bytes) -> list[bytes]:
        """
        Add data to buffer and return complete chunks.

        Args:
            data: Audio data to add

        Returns:
            List of complete chunks ready for processing
        """
        self.buffer.extend(data)
        chunks = []

        while len(self.buffer) >= self.chunk_size:
            chunks.append(bytes(self.buffer[:self.chunk_size]))
            self.buffer = self.buffer[self.chunk_size:]

        return chunks

    def flush(self) -> Optional[bytes]:
        """
        Flush remaining data in buffer.

        Returns:
            Remaining data or None if buffer is empty
        """
        if len(self.buffer) > 0:
            data = bytes(self.buffer)
            self.buffer.clear()
            return data
        return None

    def clear(self):
        """Clear the buffer."""
        self.buffer.clear()

    @property
    def size(self) -> int:
        """Get current buffer size in bytes."""
        return len(self.buffer)
