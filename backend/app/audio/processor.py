"""
Audio processing utilities for validation and quality checks.
"""
import numpy as np
from typing import Dict, Any
from .encoder import pcm16_to_float32, validate_pcm16_data


def calculate_audio_level(pcm_data: bytes) -> float:
    """
    Calculate RMS audio level from PCM16 data.

    Args:
        pcm_data: Raw PCM16 bytes

    Returns:
        RMS level as a float between 0.0 and 1.0
    """
    try:
        validate_pcm16_data(pcm_data)
        float_data = pcm16_to_float32(pcm_data)
        rms = np.sqrt(np.mean(float_data ** 2))
        return float(rms)
    except Exception:
        return 0.0


def detect_silence(pcm_data: bytes, threshold: float = 0.01) -> bool:
    """
    Detect if audio chunk is silence.

    Args:
        pcm_data: Raw PCM16 bytes
        threshold: RMS threshold below which audio is considered silent

    Returns:
        True if audio is silent
    """
    level = calculate_audio_level(pcm_data)
    return level < threshold


def get_audio_stats(pcm_data: bytes) -> Dict[str, Any]:
    """
    Get statistics about audio chunk.

    Args:
        pcm_data: Raw PCM16 bytes

    Returns:
        Dictionary with audio statistics
    """
    try:
        validate_pcm16_data(pcm_data)
        float_data = pcm16_to_float32(pcm_data)

        return {
            "size_bytes": len(pcm_data),
            "size_samples": len(float_data),
            "duration_ms": (len(float_data) / 24000.0) * 1000,  # Assuming 24kHz
            "rms_level": float(np.sqrt(np.mean(float_data ** 2))),
            "peak_level": float(np.max(np.abs(float_data))),
            "is_silent": detect_silence(pcm_data),
        }
    except Exception as e:
        return {
            "error": str(e),
            "size_bytes": len(pcm_data),
        }


def validate_audio_format(
    pcm_data: bytes,
    expected_chunk_size: int = 960,  # 480 samples * 2 bytes
    tolerance: float = 0.1
) -> bool:
    """
    Validate audio format matches expected parameters.

    Args:
        pcm_data: Raw PCM16 bytes
        expected_chunk_size: Expected size in bytes
        tolerance: Acceptable deviation (0.1 = 10%)

    Returns:
        True if format is valid
    """
    try:
        validate_pcm16_data(pcm_data)

        size = len(pcm_data)
        min_size = expected_chunk_size * (1 - tolerance)
        max_size = expected_chunk_size * (1 + tolerance)

        if not (min_size <= size <= max_size):
            return False

        return True
    except ValueError:
        return False
