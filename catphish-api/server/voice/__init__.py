"""
Voice authentication module for Catphish.
Provides speaker verification, phrase generation, and comprehension checking.
"""

from .encoder import create_embedding
from .verification import compare_embeddings
from .comprehension import comprehension_check
from .phrase_generator import generate_verification_phrase, get_enrollment_phrase

__all__ = [
    "create_embedding",
    "compare_embeddings",
    "comprehension_check",
    "generate_verification_phrase",
    "get_enrollment_phrase",
]
