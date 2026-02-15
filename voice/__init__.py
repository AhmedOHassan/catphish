"""
Voice authentication module for Catphish.
Provides speaker verification, AI detection, and comprehension checking.
"""

from .encoder import create_embedding
from .verification import compare_embeddings
from .ai_detection import detect_ai
from .comprehension import comprehension_check

__all__ = [
    "create_embedding",
    "compare_embeddings", 
    "detect_ai",
    "comprehension_check",
]
