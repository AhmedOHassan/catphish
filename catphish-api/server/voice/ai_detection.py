"""
AI voice detection module.
Detects if audio is AI-generated using AASIST or fallback heuristics.
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
    Detect if voice is AI-generated.
    Tries AASIST model first, falls back to spectral flatness heuristic.
    
    Args:
        audio_data: Audio as bytes, file path (str), or Path object
        threshold: AI probability threshold (default 0.5)
        
    Returns:
        dict: {
            'ai_probability': float (0-1),
            'threshold': float,
            'is_ai': bool,
            'confidence': float (0-1),
            'method': str ('AASIST', 'spectral_flatness_heuristic', or 'failed')
        }
    """
    audio_path = _prepare_audio_path(audio_data)
    
    try:
        # Try AASIST first
        result = _detect_with_aasist(audio_path)
        if result:
            result['threshold'] = threshold
            result['is_ai'] = result['ai_probability'] > threshold
            return result
    except Exception as e:
        # AASIST not available, continue to fallback
        pass
    
    # Fallback to heuristic
    try:
        result = _detect_with_heuristic(audio_path)
        result['threshold'] = threshold
        result['is_ai'] = result['ai_probability'] > threshold
        return result
    except Exception as e:
        # Complete failure
        return {
            'ai_probability': 0.0,
            'threshold': threshold,
            'is_ai': False,
            'confidence': 0.0,
            'method': 'failed',
            'error': str(e)
        }
    finally:
        # Clean up temp file if we created one
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


def _detect_with_aasist(audio_path: str) -> dict:
    """
    Detect AI voice using AASIST model.
    
    Returns:
        dict or None if AASIST not available
    """
    try:
        # Import inside try block to allow graceful fallback
        import sys
        from pathlib import Path as P
        
        # Add voice-detection-demo to path if needed
        # Navigate from catphish-api/server/voice to repository root
        demo_dir = P(__file__).parent.parent.parent.parent / "voice-detection-demo"
        if not demo_dir.exists():
            # voice-detection-demo directory not found
            return None
            
        if str(demo_dir) not in sys.path:
            sys.path.insert(0, str(demo_dir))
        
        # Check if AASIST model files exist
        models_dir = demo_dir / "models" / "aasist"
        if not models_dir.exists():
            # AASIST model not set up - need to run setup script
            return None
        
        from aasist_inference import AASISTDetector
        
        detector = AASISTDetector()
        result = detector.predict(audio_path)
        
        return {
            'ai_probability': result['ai_probability'],
            'confidence': result['confidence'],
            'method': 'AASIST'
        }
    except Exception:
        # AASIST unavailable - will use fallback
        return None


def _detect_with_heuristic(audio_path: str) -> dict:
    """
    Fallback AI detection using spectral flatness heuristic.
    AI voices tend to have more uniform spectral characteristics.
    
    Note: This is less accurate than AASIST but provides a baseline.
    """
    import librosa
    
    # Load audio
    y, sr = librosa.load(audio_path, sr=16000)
    
    # Calculate spectral flatness
    spectral_flatness = librosa.feature.spectral_flatness(y=y)
    avg_flatness = float(np.mean(spectral_flatness))
    
    # Convert to AI probability (higher flatness = more likely AI)
    # Spectral flatness ranges from 0-1, we multiply by 2 to spread the distribution
    # and cap at 1.0. This is a rough heuristic where:
    # - avg_flatness ~0.0-0.3: typical human voice (low AI probability)
    # - avg_flatness ~0.5+: more uniform spectrum, possibly AI (high AI probability)
    FLATNESS_MULTIPLIER = 2.0
    ai_score = min(avg_flatness * FLATNESS_MULTIPLIER, 1.0)
    confidence = abs(ai_score - 0.5) * 2
    
    return {
        'ai_probability': ai_score,
        'confidence': confidence,
        'method': 'spectral_flatness_heuristic',
        'warning': 'Using fallback heuristic - accuracy limited without AASIST. To enable AASIST: run voice-detection-demo/setup.sh'
    }
