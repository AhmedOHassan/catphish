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
    AI detection using multiple audio features.
    
    Modern AI/TTS voices are too clean compared to real microphone recordings:
    - Very low noise floor (no background hiss)
    - Unnaturally consistent pitch and energy
    - Less micro-variation in spectral features frame-to-frame
    - Missing natural breath sounds and mouth noise
    
    We combine several signals into a weighted score.
    """
    import librosa

    y, sr = librosa.load(audio_path, sr=16000)

    scores = {}

    # ── 1. Spectral flatness (original) ──
    # AI voices can be either too flat or too peaked; not very reliable alone
    spec_flat = librosa.feature.spectral_flatness(y=y)
    avg_flatness = float(np.mean(spec_flat))
    scores['spectral_flatness'] = min(avg_flatness * 2.0, 1.0)

    # ── 2. Noise floor / silence analysis ──
    # Real mic recordings have background noise; AI TTS has near-silent gaps
    # Look at the quietest 20% of frames — if they're extremely quiet, suspicious
    rms = librosa.feature.rms(y=y)[0]
    sorted_rms = np.sort(rms)
    quiet_portion = sorted_rms[:max(1, len(sorted_rms) // 5)]
    avg_quiet = float(np.mean(quiet_portion))
    # Real mic: quiet portions ~0.001-0.01; AI TTS: ~0.0001 or less
    # Lower noise floor → higher AI score
    noise_floor_score = max(0.0, 1.0 - (avg_quiet * 200))  # 0.005 → 0.0, 0.0 → 1.0
    scores['noise_floor'] = float(np.clip(noise_floor_score, 0, 1))

    # ── 3. RMS energy variance ──
    # Real speech has more dynamic range; AI is more consistent
    rms_std = float(np.std(rms))
    rms_mean = float(np.mean(rms)) + 1e-10
    rms_cv = rms_std / rms_mean  # coefficient of variation
    # Real voice: CV ~0.6-1.5; AI: CV ~0.3-0.6
    energy_score = max(0.0, 1.0 - (rms_cv * 1.2))
    scores['energy_consistency'] = float(np.clip(energy_score, 0, 1))

    # ── 4. MFCC frame-to-frame variance (delta stability) ──
    # AI voices have smoother transitions; real speech has micro-jitter
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_delta = librosa.feature.delta(mfccs)
    delta_var = float(np.mean(np.var(mfcc_delta, axis=1)))
    # Real voice: higher delta variance; AI: lower
    # Typical real: ~5-20; AI: ~1-5
    mfcc_score = max(0.0, 1.0 - (delta_var / 15.0))
    scores['mfcc_stability'] = float(np.clip(mfcc_score, 0, 1))

    # ── 5. Zero-crossing rate variance ──
    # Real speech has more varied ZCR; AI is smoother
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zcr_std = float(np.std(zcr))
    # Real voice: std ~0.03-0.08; AI: ~0.01-0.03
    zcr_score = max(0.0, 1.0 - (zcr_std * 20.0))
    scores['zcr_consistency'] = float(np.clip(zcr_score, 0, 1))

    # ── Weighted combination ──
    weights = {
        'noise_floor': 0.30,         # strongest signal: AI has no mic noise
        'energy_consistency': 0.25,   # AI energy is too even
        'mfcc_stability': 0.20,       # AI transitions are too smooth
        'zcr_consistency': 0.15,      # AI zero-crossings are too uniform
        'spectral_flatness': 0.10,    # weak signal on its own
    }

    ai_score = sum(scores[k] * weights[k] for k in weights)
    ai_score = float(np.clip(ai_score, 0, 1))
    confidence = abs(ai_score - 0.5) * 2

    return {
        'ai_probability': ai_score,
        'confidence': confidence,
        'method': 'multi_feature_heuristic',
        'feature_scores': scores
    }
