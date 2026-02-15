"""
Speaker verification module using cosine similarity.
Compares voice embeddings to verify speaker identity.
"""

import numpy as np
from typing import Union, List


def compare_embeddings(
    enrolled_embedding: Union[np.ndarray, List[float]],
    test_embedding: Union[np.ndarray, List[float]],
    threshold: float = 0.89
) -> dict:
    """
    Compare two voice embeddings using cosine similarity.
    
    Args:
        enrolled_embedding: The enrolled speaker's embedding
        test_embedding: The test audio embedding
        threshold: Similarity threshold for match (default 0.89)
            Resemblyzer cosine similarities:
              - Same speaker:      ~0.88 – 0.98
              - Different speaker:  ~0.75 – 0.87
            0.89 is a good balance between FAR and FRR.
        
    Returns:
        dict: {
            'similarity': float (0-1),
            'threshold': float,
            'match': bool,
            'confidence': float (0-1)
        }
    """
    # Convert to numpy arrays if needed
    if not isinstance(enrolled_embedding, np.ndarray):
        enrolled_embedding = np.array(enrolled_embedding)
    if not isinstance(test_embedding, np.ndarray):
        test_embedding = np.array(test_embedding)
    
    # Calculate cosine similarity (embeddings are already normalized by Resemblyzer)
    similarity = float(np.dot(test_embedding, enrolled_embedding))
    
    # Determine if it's a match
    match = similarity >= threshold
    
    # Calculate confidence (distance from threshold)
    if match:
        # Confidence increases as we move away from threshold toward 1.0
        confidence = abs(similarity - threshold) / (1 - threshold)
    else:
        # Confidence increases as we move away from threshold toward 0.0
        confidence = abs(similarity - threshold) / threshold
    
    confidence = min(confidence, 1.0)
    
    return {
        'similarity': similarity,
        'threshold': threshold,
        'match': match,
        'confidence': confidence
    }
