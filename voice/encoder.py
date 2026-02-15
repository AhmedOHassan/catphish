"""
Voice encoder module for creating speaker embeddings.
Uses Resemblyzer for speaker verification.
"""

import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import io
import tempfile
from typing import Union, List


def create_embedding(audio_data: Union[bytes, str, Path]) -> np.ndarray:
    """
    Create a voice embedding from audio data.
    
    Args:
        audio_data: Can be:
            - bytes: raw audio data
            - str: path to audio file
            - Path: path to audio file
            
    Returns:
        np.ndarray: 256-dimensional embedding vector
        
    Raises:
        Exception: If audio processing fails
    """
    encoder = VoiceEncoder()
    
    # Handle different input types
    if isinstance(audio_data, bytes):
        # Save bytes to temp file for processing
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name
        
        try:
            wav = preprocess_wav(Path(tmp_path))
            embedding = encoder.embed_utterance(wav)
            return embedding
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
    else:
        # Handle file path (str or Path)
        wav = preprocess_wav(Path(audio_data))
        embedding = encoder.embed_utterance(wav)
        return embedding


def create_average_embedding(audio_files: List[Union[str, Path]]) -> dict:
    """
    Create an average embedding from multiple audio samples.
    Used during enrollment to create a robust voice profile.
    
    Args:
        audio_files: List of paths to audio files
        
    Returns:
        dict: Profile containing:
            - embedding_mean: Average embedding vector
            - embedding_std: Standard deviation
            - sample_count: Number of samples processed
            - quality_score: Consistency score (0-1)
    """
    embeddings = []
    
    for audio_path in audio_files:
        embedding = create_embedding(audio_path)
        embeddings.append(embedding)
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings)
    
    # Calculate statistics
    embedding_mean = np.mean(embeddings_array, axis=0)
    embedding_std = np.std(embeddings_array, axis=0)
    
    # Calculate quality score (pairwise similarity)
    quality_score = _calculate_quality_score(embeddings)
    
    return {
        "embedding_mean": embedding_mean.tolist(),
        "embedding_std": embedding_std.tolist(),
        "sample_count": len(embeddings),
        "quality_score": quality_score,
    }


def _calculate_quality_score(embeddings: List[np.ndarray]) -> float:
    """
    Calculate quality score based on pairwise similarity.
    Higher score means more consistent voice samples.
    """
    if len(embeddings) < 2:
        return 1.0
    
    similarities = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            similarity = np.dot(embeddings[i], embeddings[j])
            similarities.append(similarity)
    
    return float(np.mean(similarities))
