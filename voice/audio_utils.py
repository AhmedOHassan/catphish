"""
Audio utility functions for format conversion and handling.
"""

import base64
import io
from pathlib import Path
from typing import Union


def base64_to_bytes(base64_str: str) -> bytes:
    """
    Convert base64 string to bytes.
    
    Args:
        base64_str: Base64 encoded audio string
        
    Returns:
        bytes: Decoded audio data
    """
    return base64.b64decode(base64_str)


def bytes_to_wav(audio_bytes: bytes) -> bytes:
    """
    Ensure audio bytes are in WAV format.
    If already WAV, returns as-is. Otherwise attempts conversion.
    
    Args:
        audio_bytes: Raw audio data
        
    Returns:
        bytes: Audio data in WAV format
    """
    # Check if already WAV (starts with RIFF header)
    if audio_bytes[:4] == b'RIFF':
        return audio_bytes
    
    # For MVP, assume input is already WAV
    # In production, could use pydub or similar for format conversion
    return audio_bytes


def save_temp_audio(audio_bytes: bytes, suffix: str = '.wav') -> Path:
    """
    Save audio bytes to temporary file.
    
    Args:
        audio_bytes: Audio data
        suffix: File suffix (default: .wav)
        
    Returns:
        Path: Path to temporary file
    """
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
        tmp_file.write(audio_bytes)
        return Path(tmp_file.name)
