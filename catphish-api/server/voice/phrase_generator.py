"""
Anti-TTS Phrase Generator for Voice Authentication.

Generates instruction phrases that are easy for humans to follow
but impossible for TTS/deepfake systems to handle correctly.

Key insight: TTS systems receive text and produce audio verbatim.
They cannot *comprehend* instructions like "skip the third word"
or "say the sum of 2+3". A human reads the instruction and acts
on it; a TTS reads the instruction text aloud.
"""

import random
import secrets


# ── Registration / enrollment phrase ──
# Covers all English phonemes for a rich voice profile.
ENROLLMENT_PHRASE = (
    "Please call Stella. Ask her to bring these things with her from the store: "
    "six spoons of fresh snow peas, five thick slabs of blue cheese, "
    "and maybe a snack for her brother Bob."
)


class AntiTTSPhraseGenerator:
    """Generate phrases designed to catch AI TTS while being human-readable."""

    def __init__(self):
        self.nouns = [
            'apple', 'banana', 'cherry', 'dragon', 'elephant', 'flower', 'guitar',
            'hammer', 'island', 'jacket', 'kite', 'lemon', 'mountain', 'notebook',
            'ocean', 'piano', 'quilt', 'river', 'sunset', 'thunder', 'umbrella',
            'violin', 'window', 'castle', 'garden', 'rocket', 'palace', 'bridge',
            'crystal', 'diamond', 'falcon', 'glacier',
        ]

        self.adjectives = [
            'bright', 'calm', 'dark', 'eager', 'fast', 'gentle', 'happy', 'icy',
            'jolly', 'kind', 'loud', 'mellow', 'narrow', 'orange', 'proud', 'quiet',
            'rough', 'smooth', 'tall', 'vivid', 'warm', 'young', 'zesty',
            'ancient', 'brave', 'clever', 'distant', 'elegant', 'frozen', 'golden',
        ]

        self.colors = [
            'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'white',
            'black', 'silver', 'golden', 'crimson',
        ]

        self.simple_words = [
            'cat', 'dog', 'sun', 'moon', 'star', 'tree', 'bird', 'fish',
            'frog', 'bear', 'wolf', 'duck', 'rain', 'book', 'lamp', 'ship',
        ]

        self.templates = [
            self._math_then_words,
            self._skip_word,
            self._reverse_list,
            self._replace_color,
            self._spell_then_say,
            self._count_and_say,
        ]

    # ── Public API ──

    def generate(self) -> dict:
        """
        Generate a random anti-TTS instruction phrase.

        Returns:
            dict with:
                - instruction: str  (what the user sees on screen)
                - expected_behavior: str  (description for Gemini of correct response)
                - difficulty: str
                - type: str  (template name)
        """
        template = secrets.choice(self.templates)
        return template()

    # ── Templates ──

    def _math_then_words(self) -> dict:
        """Say the result of simple math, then some words."""
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        op = random.choice(['+', '-'])
        result = a + b if op == '+' else a - b
        words = random.sample(self.nouns, 3)

        return {
            'instruction': f'Say the answer to {a} {op} {b}, then say: {words[0]}, {words[1]}, {words[2]}',
            'expected_behavior': (
                f'The speaker should say the number "{result}" first, '
                f'then say the words "{words[0]}", "{words[1]}", "{words[2]}". '
                f'A TTS system would read the instruction literally including '
                f'"say the answer to {a} {op} {b}" instead of computing the result.'
            ),
            'difficulty': 'medium',
            'type': 'math_then_words',
        }

    def _skip_word(self) -> dict:
        """Read a list but skip one specific word."""
        words = random.sample(self.simple_words, 5)
        skip_idx = random.randint(1, 3)  # skip 2nd, 3rd, or 4th
        ordinal = ['first', 'second', 'third', 'fourth', 'fifth'][skip_idx]
        expected = [w for i, w in enumerate(words) if i != skip_idx]

        return {
            'instruction': f'Read this list but skip the {ordinal} word: {", ".join(words)}',
            'expected_behavior': (
                f'The speaker should say: "{", ".join(expected)}" — '
                f'omitting the word "{words[skip_idx]}". '
                f'A TTS would read all five words or read the instruction itself.'
            ),
            'difficulty': 'easy',
            'type': 'skip_word',
        }

    def _reverse_list(self) -> dict:
        """Say a list of words in reverse order."""
        words = random.sample(self.simple_words, 4)
        reversed_words = list(reversed(words))

        return {
            'instruction': f'Say these words in reverse order: {", ".join(words)}',
            'expected_behavior': (
                f'The speaker should say: "{", ".join(reversed_words)}". '
                f'A TTS would either read the words in the original order '
                f'or read the instruction text itself.'
            ),
            'difficulty': 'medium',
            'type': 'reverse_list',
        }

    def _replace_color(self) -> dict:
        """Say a phrase but replace one color with another."""
        color1, color2 = random.sample(self.colors, 2)
        noun = random.choice(self.nouns)
        adj = random.choice(self.adjectives)

        return {
            'instruction': (
                f'Say "the {color1} {noun} is {adj}" but replace '
                f'"{color1}" with "{color2}"'
            ),
            'expected_behavior': (
                f'The speaker should say: "the {color2} {noun} is {adj}". '
                f'A TTS would either say the original phrase with "{color1}" '
                f'or read the full instruction including "but replace".'
            ),
            'difficulty': 'easy',
            'type': 'replace_color',
        }

    def _spell_then_say(self) -> dict:
        """Spell a short word, then say a phrase."""
        word = random.choice(['cat', 'dog', 'sun', 'red', 'big', 'hot'])
        phrase_words = random.sample(self.nouns, 2)

        return {
            'instruction': f'Spell the word "{word}" letter by letter, then say: {phrase_words[0]} {phrase_words[1]}',
            'expected_behavior': (
                f'The speaker should say each letter: '
                f'"{", ".join(word.upper())}" then say '
                f'"{phrase_words[0]} {phrase_words[1]}". '
                f'A TTS would read "spell the word" literally.'
            ),
            'difficulty': 'easy',
            'type': 'spell_then_say',
        }

    def _count_and_say(self) -> dict:
        """Count to a number then say a phrase."""
        count_to = random.randint(3, 6)
        words = random.sample(self.adjectives, 2)

        return {
            'instruction': f'Count from one to {count_to}, then say: {words[0]} {words[1]}',
            'expected_behavior': (
                f'The speaker should count "one, two, three, ..., {count_to}" '
                f'then say "{words[0]} {words[1]}". '
                f'A TTS would read the instruction text verbatim.'
            ),
            'difficulty': 'easy',
            'type': 'count_and_say',
        }


# Module-level instance for convenience
_generator = AntiTTSPhraseGenerator()


def generate_verification_phrase() -> dict:
    """Generate a random anti-TTS instruction phrase for verification."""
    return _generator.generate()


def generate_enrollment_phrases(count: int = 5) -> dict:
    """
    Generate multiple anti-TTS instruction phrases for enrollment.

    Using several phrases gives Resemblyzer a richer baseline of the
    speaker's natural voice (tone, cadence, pitch) and ensures the
    embedding is built from the same *kind* of speech used during
    verification.

    Returns:
        dict with:
            - instruction: str  (numbered list of all instructions)
            - expected_behavior: str  (combined expected behaviors)
            - phrases: list[dict]  (individual phrase dicts)
            - difficulty: str
            - type: str
    """
    seen_types: set[str] = set()
    phrases: list[dict] = []

    # Pick distinct template types so the user gets variety
    while len(phrases) < count:
        p = _generator.generate()
        if p['type'] not in seen_types or len(seen_types) >= len(_generator.templates):
            phrases.append(p)
            seen_types.add(p['type'])

    numbered = [f"{i+1}. {p['instruction']}" for i, p in enumerate(phrases)]
    combined_instruction = "\n".join(numbered)
    combined_expected = " | ".join(
        f"Phrase {i+1}: {p['expected_behavior']}" for i, p in enumerate(phrases)
    )

    return {
        'instruction': combined_instruction,
        'expected_behavior': combined_expected,
        'phrases': phrases,
        'difficulty': 'medium',
        'type': 'enrollment_multi',
    }


def get_enrollment_phrase() -> str:
    """Return the standard enrollment phrase (covers all phonemes)."""
    return ENROLLMENT_PHRASE
