"""
AI voice detection module.
Detects if audio is AI-generated using spectral flatness heuristic.
"""

import numpy as np
from pathlib import Path
import tempfile
from typing import Union


def detect_ai(
    audio_data: Union[bytes, str, Path],
    threshold: float = 0.5
) -> dict:
    """
    Detect if voice is AI-generated using spectral flatness analysis.
    
    Args:
        audio_data: Audio as bytes, file path (str), or Path object
        threshold: AI probability threshold (default 0.5)
        
    Returns:
        dict: {
            'ai_probability': float (0-1),
            'threshold': float,
            'is_ai': bool,
            'confidence': float (0-1),
            'method': str
        }
    """
    audio_path = _prepare_audio_path(audio_data)
    
    try:
        result = _detect_with_heuristic(audio_path)
        result['threshold'] = threshold
        result['is_ai'] = result['ai_probability'] > threshold
        return result
    except Exception as e:
        return {
            'ai_probability': 0.0,
            'threshold': threshold,
            'is_ai': False,
            'confidence': 0.0,
            'method': 'failed',
            'error': str(e)
        }
    finally:
        if isinstance(audio_data, bytes):
            Path(audio_path).unlink(missing_ok=True)


def _prepare_audio_path(audio_data: Union[bytes, str, Path]) -> str:
    """Convert audio data to file path, creating temp file if needed."""
    if isinstance(audio_data, bytes):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_data)
            return tmp_file.name
    else:
        return str(audio_data)


def _detect_with_heuristic(audio_path: str) -> dict:
    """
    AI detection using spectral flatness heuristic.
    AI voices tend to have more uniform spectral characteristics.
    """
    import librosa
    
    y, sr = librosa.load(audio_path, sr=16000)
    
    spectral_flatness = librosa.feature.spectral_flatness(y=y)
    avg_flatness = float(np.mean(spectral_flatness))
    
    # Higher flatness = more likely AI
    # avg_flatness ~0.0-0.3: typical human voice (low AI probability)
    # avg_flatness ~0.5+: more uniform spectrum, possibly AI
    FLATNESS_MULTIPLIER = 2.0
    ai_score = min(avg_flatness * FLATNESS_MULTIPLIER, 1.0)
    confidence = abs(ai_score - 0.5) * 2
    
    return {
        'ai_probability': ai_score,
        'confidence': confidence,
        'method': 'spectral_flatness_heuristic'
    }
