"""
Layer 2 — Human Comprehension Check via Gemini.

Sends the audio + the instruction prompt to Gemini and asks:
"Did the speaker *follow the instruction* (human) or just read it
verbatim / produce something unrelated (TTS / deepfake)?"

This is the core anti-TTS layer. A human reads "say the sum of 2+3
then say apple banana cherry" and says "5 apple banana cherry".
A TTS system receives the same text and says "say the sum of 2 plus 3
then say apple banana cherry" — it cannot comprehend instructions.
"""

import os
import json
import base64
import tempfile
from pathlib import Path
from typing import Union, Optional


def comprehension_check(
    audio_data: Union[bytes, str, Path],
    instruction: str,
    expected_behavior: str,
    similarity_score: float = 0.0,
) -> dict:
    """
    Use Gemini to judge whether the speaker followed the instruction.

    Args:
        audio_data: Audio as bytes, file path, or Path
        instruction: The instruction shown to the user
        expected_behavior: Description of what correct behavior looks like
        similarity_score: Speaker similarity from Layer 1 (for context)

    Returns:
        dict with:
            - followed_instruction: bool
            - confidence: float (0-1)
            - reasoning: str
            - transcript: str (what Gemini heard)
            - red_flags: list[str]
            - recommendation: 'ALLOW' | 'BLOCK' | 'CHALLENGE_AGAIN'
    """
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        return {
            'skipped': True,
            'reason': 'no_api_key',
            'recommendation': 'ALLOW',
            'warning': 'GEMINI_API_KEY not set — comprehension check skipped',
        }

    audio_path = _prepare_audio_path(audio_data)

    try:
        result = _analyze_with_gemini(
            audio_path=audio_path,
            instruction=instruction,
            expected_behavior=expected_behavior,
            similarity_score=similarity_score,
            api_key=api_key,
        )
        return result
    except Exception as e:
        return {
            'error': str(e),
            'recommendation': 'CHALLENGE_AGAIN',
            'reasoning': f'Gemini comprehension check failed: {e}',
        }
    finally:
        if isinstance(audio_data, bytes):
            Path(audio_path).unlink(missing_ok=True)


def _prepare_audio_path(audio_data: Union[bytes, str, Path]) -> str:
    if isinstance(audio_data, bytes):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_data)
            return f.name
    return str(audio_data)


def _analyze_with_gemini(
    audio_path: str,
    instruction: str,
    expected_behavior: str,
    similarity_score: float,
    api_key: str,
) -> dict:
    """
    Send audio + instruction to Gemini and get a structured judgment.
    Uses the Gemini multimodal API to analyze the actual audio.
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    # Read audio file and encode for Gemini
    with open(audio_path, 'rb') as f:
        audio_bytes = f.read()

    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

    prompt = f"""You are a voice authentication security system. Your job is to determine
whether a speaker FOLLOWED an instruction correctly, or whether they just
read the instruction text verbatim (which is what an AI TTS system would do).

## The Instruction Shown to the User
"{instruction}"

## What a Correct Human Response Sounds Like
{expected_behavior}

## Context
- Speaker voice similarity to enrolled profile: {similarity_score:.2f}

## Your Task
Listen to the audio carefully. Determine:

1. **transcript**: What did the speaker actually say? Transcribe it.
2. **followed_instruction**: Did the speaker follow the instruction (true) or did they
   just read the instruction text literally / say something unrelated (false)?
   - A HUMAN will compute math, skip words, reverse lists, etc.
   - A TTS/AI will read "say the answer to 2 plus 3" literally instead of saying "5".
   - Be lenient with pronunciation and minor mistakes. Focus on whether they
     UNDERSTOOD and ACTED ON the instruction.
3. **confidence**: How confident are you (0.0 to 1.0)?
4. **reasoning**: Brief explanation of your decision.
5. **red_flags**: List any suspicious patterns (empty list if none):
   - "verbatim_reading" — speaker read the instruction text itself
   - "no_comprehension" — speaker said something completely unrelated
   - "too_perfect" — unnaturally perfect robotic delivery
   - "social_engineering" — speaker tried to manipulate the system
6. **recommendation**: "ALLOW" if human comprehension detected, "BLOCK" if TTS/AI
   behavior detected, "CHALLENGE_AGAIN" if unclear.

Return ONLY valid JSON:
{{
    "transcript": "...",
    "followed_instruction": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "...",
    "red_flags": [],
    "recommendation": "ALLOW" or "BLOCK" or "CHALLENGE_AGAIN"
}}"""

    response = client.models.generate_content(
        model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'),
        contents=[
            types.Content(
                parts=[
                    types.Part.from_bytes(data=audio_bytes, mime_type='audio/wav'),
                    types.Part.from_text(text=prompt),
                ]
            )
        ],
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
        ),
    )

    response_text = response.text if hasattr(response, 'text') else str(response)
    result = json.loads(response_text)

    # Ensure required fields exist
    result.setdefault('followed_instruction', False)
    result.setdefault('confidence', 0.0)
    result.setdefault('reasoning', '')
    result.setdefault('transcript', '')
    result.setdefault('red_flags', [])
    result.setdefault('recommendation', 'CHALLENGE_AGAIN')

    return result

