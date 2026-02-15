#!/usr/bin/env python3
"""
Anti-TTS Phrase Generator for Voice Authentication
Generates phrases that are easy for humans but break AI TTS/deepfakes
"""

import random


class AntiTTSPhraseGenerator:
    """Generate phrases designed to catch AI TTS while being human-readable"""
    
    def __init__(self):
        # Diverse word banks (removed account-specific bias)
        self.nouns = [
            'apple', 'banana', 'cherry', 'dragon', 'elephant', 'flower', 'guitar',
            'hammer', 'island', 'jacket', 'kite', 'lemon', 'mountain', 'notebook',
            'ocean', 'piano', 'quilt', 'river', 'sunset', 'thunder', 'umbrella',
            'violin', 'window', 'yellow', 'zebra', 'castle', 'garden', 'rocket',
            'palace', 'bridge', 'crystal', 'diamond', 'emerald', 'falcon', 'glacier'
        ]
        
        self.adjectives = [
            'bright', 'calm', 'dark', 'eager', 'fast', 'gentle', 'happy', 'icy',
            'jolly', 'kind', 'loud', 'mellow', 'narrow', 'orange', 'proud', 'quiet',
            'rough', 'smooth', 'tall', 'ultra', 'vivid', 'warm', 'young', 'zesty',
            'ancient', 'brave', 'clever', 'distant', 'elegant', 'frozen', 'golden'
        ]
        
        self.verbs = [
            'jump', 'run', 'swim', 'fly', 'walk', 'dance', 'sing', 'write',
            'read', 'think', 'speak', 'listen', 'watch', 'build', 'create', 'play',
            'climb', 'drift', 'explore', 'float', 'guard', 'hide', 'inspire', 'join'
        ]
        
        self.simple_words = ['cat', 'dog', 'sun', 'moon', 'star', 'tree', 'bird', 'fish', 'frog', 'bear', 'wolf', 'duck']
        self.vowels = ['a', 'e', 'i', 'o', 'u']
        
        # Homophone pairs - different spellings, same sound
        self.homophones = [
            ('blue', 'blew'), ('knight', 'night'), ('write', 'right'),
            ('flour', 'flower'), ('our', 'hour'), ('hear', 'here'),
            ('see', 'sea'), ('pair', 'pear'), ('piece', 'peace'),
            ('road', 'rode'), ('tail', 'tale'), ('weak', 'week')
        ]
        
        # Heteronyms - same spelling, different pronunciation
        self.heteronyms = [
            ('lead', 'metal', 'to guide'),
            ('bow', 'ribbon', 'to bend'),
            ('tear', 'rip', 'cry'),
            ('wind', 'air', 'to turn'),
            ('close', 'near', 'to shut'),
            ('live', 'alive', 'broadcast')
        ]
        
        # Common rhyme pairs
        self.rhyme_map = {
            'cat': 'bat', 'tree': 'free', 'night': 'light', 'day': 'way',
            'blue': 'true', 'run': 'sun', 'star': 'far', 'moon': 'soon',
            'bear': 'care', 'dog': 'fog', 'fish': 'wish', 'bird': 'word'
        }
        
        # Syllable count words (simplified - very obvious counts)
        self.syllable_words = [
            ('pizza', 2), ('happy', 2), ('tiger', 2),
            ('window', 2), ('robot', 2), ('puppy', 2),
            ('table', 2), ('pencil', 2), ('rainbow', 2)
        ]
    
    def _random_words(self, count=3):
        """Get random words from all banks"""
        all_words = self.nouns + self.adjectives + self.verbs
        return random.sample(all_words, min(count, len(all_words)))
    
    # Template 1: Vowel Duration - Most Effective (breaks ElevenLabs)
    def vowel_duration(self):
        """AI TTS cannot sustain sounds for timed duration"""
        vowel = random.choice(self.vowels)
        duration = random.randint(3, 5)
        words = self._random_words(3)
        
        return {
            'phrase': f"[Hold vowel for {duration} seconds] {vowel.upper()} [then say]: {' '.join(words)}",
            'expected': f"{vowel.upper()}aaaaaaa ({duration}sec) {' '.join(words)}",
            'difficulty': 'hard',
            'breaks_tts': 'TTS cannot sustain phonemes for timed duration'
        }
    
    # Template 2: Math Operations (simplified for accessibility)
    def math_operation(self):
        """TTS reads instruction verbatim, cannot compute"""
        # Only use simple addition with small numbers (easier for all users)
        num1 = random.randint(1, 5)
        num2 = random.randint(1, 5)
        result = num1 + num2
        
        words = self._random_words(3)
        phrase = f"[Say the sum of {num1} + {num2}, then say]: {' '.join(words)}"
        expected = f"{result} {' '.join(words)}"
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'easy',
            'breaks_tts': 'TTS reads instructions literally, cannot compute math'
        }
    
    # Template 3: Spell and Say
    def spell_word(self):
        """TTS pronounces words, cannot spell them"""
        spell_word = random.choice(self.simple_words)
        words = self._random_words(3)
        
        spelled = '-'.join(spell_word.upper())
        phrase = f"[Spell {spell_word}, then say]: {' '.join(words)}"
        expected = f"{spelled} {' '.join(words)}"
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'easy',
            'breaks_tts': 'TTS reads words normally, cannot spell letter-by-letter'
        }
    
    # Template 4: Reverse Word
    def reverse_word(self):
        """TTS cannot reverse strings on the fly"""
        word = random.choice(self.simple_words)
        words = self._random_words(3)
        reversed_word = word[::-1]
        
        phrase = f"[Say {word} backwards, then say]: {' '.join(words)}"
        expected = f"{reversed_word} {' '.join(words)}"
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'medium',
            'breaks_tts': 'TTS cannot dynamically reverse words'
        }
    
    # Template 5: Count Letters
    def count_letters(self):
        """TTS cannot analyze letter count"""
        count_word = random.choice(self.nouns)
        letter_count = len(count_word)
        words = self._random_words(3)
        
        phrase = f"[Say letter count in {count_word}, then say]: {' '.join(words)}"
        expected = f"{letter_count} {' '.join(words)}"
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'medium',
            'breaks_tts': 'TTS cannot perform meta-linguistic analysis'
        }
    
    # Template 6: Homophone Disambiguation
    def homophone_context(self):
        """TTS cannot disambiguate based on semantic context"""
        h1, h2 = random.choice(self.homophones)
        correct_word = random.choice([h1, h2])
        words = self._random_words(2)
        
        contexts = {
            'blue': 'the color', 'blew': 'past tense of blow',
            'knight': 'warrior in armor', 'night': 'dark time',
            'write': 'with a pen', 'right': 'correct or direction',
            'flour': 'for baking', 'flower': 'blooming plant',
            'our': 'belonging to us', 'hour': 'sixty minutes',
            'hear': 'with ears', 'here': 'this location',
            'see': 'with eyes', 'sea': 'ocean water',
            'pair': 'two items', 'pear': 'a fruit',
            'piece': 'a portion', 'peace': 'no conflict',
            'road': 'a street', 'rode': 'past tense of ride',
            'tail': 'animal appendage', 'tale': 'a story',
            'weak': 'not strong', 'week': 'seven days'
        }
        
        context = contexts.get(correct_word, 'appropriate meaning')
        phrase = f"[Use {correct_word} as in {context}, then say]: {' '.join(words)}"
        expected = f"{correct_word} {' '.join(words)}"
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'hard',
            'breaks_tts': 'TTS cannot disambiguate homophones semantically'
        }
    
    # Template 7: Heteronym Pronunciation
    def heteronym_pronunciation(self):
        """TTS uses default pronunciation, ignores context"""
        word, context1, context2 = random.choice(self.heteronyms)
        chosen_context = random.choice([context1, context2])
        words = self._random_words(2)
        
        phrase = f"[Say {word} as in {chosen_context}, then say]: {' '.join(words)}"
        expected = f"{word}[{chosen_context}] {' '.join(words)}"
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'hard',
            'breaks_tts': 'TTS uses default pronunciation regardless of context'
        }
    
    # Template 8: Rhyme Generation
    def rhyme_generation(self):
        """TTS cannot generate rhymes dynamically"""
        base_word = random.choice(list(self.rhyme_map.keys()))
        expected_rhyme = self.rhyme_map[base_word]
        words = self._random_words(2)
        
        phrase = f"[Say a word that rhymes with {base_word}, then say]: {' '.join(words)}"
        expected = f"{expected_rhyme} {' '.join(words)}"
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'hard',
            'breaks_tts': 'TTS cannot generate rhymes, reads instruction literally'
        }
    
    # Template 9: Syllable Count (simplified for accessibility)
    def syllable_count(self):
        """TTS cannot analyze phonological structure"""
        word, count = random.choice(self.syllable_words)
        words = self._random_words(2)
        
        phrase = f"[Say syllable count in {word}, then say]: {' '.join(words)}"
        expected = f"{count} {' '.join(words)}"
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'medium',  # Changed from hard to medium
            'breaks_tts': 'TTS cannot count syllables phonologically'
        }
    
    # Template 10: Emphasis Pattern
    def emphasis_pattern(self):
        """TTS cannot shift emphasis dynamically"""
        words_list = self._random_words(4)
        emphasis_pos = random.randint(0, len(words_list) - 1)
        
        phrase = f"[Emphasize word {emphasis_pos + 1}]: {' '.join(words_list)}"
        expected_words = [w.upper() if i == emphasis_pos else w for i, w in enumerate(words_list)]
        expected = ' '.join(expected_words)
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'medium',
            'breaks_tts': 'TTS uses flat prosody, cannot emphasize specific words'
        }
    
    # Template 11: Speed Variation
    def speed_control(self):
        """TTS cannot vary speaking speed on command"""
        fast_words = self._random_words(2)
        slow_words = self._random_words(2)
        
        phrase = f"[Say quickly]: {' '.join(fast_words)} [say slowly]: {' '.join(slow_words)}"
        expected = f"{'-'.join(fast_words)}[fast] {' '.join(slow_words)}[slow]"
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'medium',
            'breaks_tts': 'TTS maintains constant speaking rate'
        }
    
    # Template 12: First Letters Only (Acronym)
    def first_letters_only(self):
        """TTS reads full words, not individual letters"""
        words_list = self._random_words(4)
        first_letters = '-'.join([w[0].upper() for w in words_list])
        
        phrase = f"[Say first letter of each word]: {' '.join(words_list)}"
        expected = first_letters
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'medium',
            'breaks_tts': 'TTS reads complete words, not letter extraction'
        }
    
    # Template 13: Every Other Word
    def every_other_word(self):
        """TTS reads all words sequentially"""
        all_words = self._random_words(7)
        
        phrase = f"[Read every other word]: {' '.join(all_words)}"
        expected = " ".join(all_words[::2])
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'medium',
            'breaks_tts': 'TTS cannot skip words based on position'
        }
    
    # Template 14: Replace Placeholder
    def replace_placeholder(self):
        """TTS reads placeholder literally"""
        words_list = self._random_words(4)
        
        phrase = f"[Replace BLANK with your name]: {words_list[0]} BLANK {' '.join(words_list[1:])}"
        expected = f"{words_list[0]} [your name] {' '.join(words_list[1:])}"
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'easy',
            'breaks_tts': 'TTS says BLANK instead of substituting'
        }
    
    # Template 15: Pause Duration
    def pause_duration(self):
        """TTS cannot execute timed pauses"""
        duration = random.randint(2, 4)
        words = self._random_words(3)
        
        phrase = f"[Say] pause, [wait {duration} seconds], [then say]: {' '.join(words)}"
        expected = f"pause [{duration}sec silence] {' '.join(words)}"
        
        return {
            'phrase': phrase,
            'expected': expected,
            'difficulty': 'medium',
            'breaks_tts': 'TTS cannot execute timed pauses from instructions'
        }
    
    def generate(self, difficulty=None):
        """Generate a random phrase, optionally filtered by difficulty"""
        templates = [
            self.vowel_duration,
            self.math_operation,
            self.spell_word,
            self.reverse_word,
            self.count_letters,
            self.homophone_context,
            self.rhyme_generation,
            self.syllable_count,
            self.emphasis_pattern,
            self.speed_control,
            self.first_letters_only,
            self.every_other_word,
            self.replace_placeholder,
            self.pause_duration
        ]
        
        if difficulty:
            # Generate multiple and filter by difficulty
            candidates = [t() for t in templates]
            filtered = [c for c in candidates if c['difficulty'] == difficulty]
            if filtered:
                return random.choice(filtered)
        
        # Random template
        template = random.choice(templates)
        return template()
    
    def generate_batch(self, count=10, difficulty=None):
        """Generate multiple phrases"""
        return [self.generate(difficulty) for _ in range(count)]


def main():
    """Test the generator"""
    generator = AntiTTSPhraseGenerator()
    
    print("=" * 80)
    print(" ANTI-TTS PHRASE GENERATOR - Test Output")
    print("=" * 80)
    print()
    
    # Show all template types
    print("📋 ALL PHRASE TYPES:\n")
    
    templates = [
        ("Vowel Duration ⭐", generator.vowel_duration),
        ("Math Operation", generator.math_operation),
        ("Spell Word", generator.spell_word),
        ("Reverse Word", generator.reverse_word),
        ("Count Letters", generator.count_letters),
        ("Homophone Context", generator.homophone_context),
        ("Rhyme Generation", generator.rhyme_generation),
        ("Syllable Count", generator.syllable_count),
        ("Emphasis Pattern", generator.emphasis_pattern),
        ("Speed Control", generator.speed_control),
        ("First Letters Only", generator.first_letters_only),
        ("Every Other Word", generator.every_other_word),
        ("Replace Placeholder", generator.replace_placeholder),
        ("Pause Duration", generator.pause_duration),
    ]
    
    for name, template_func in templates:
        result = template_func()
        print(f"─── {name} ({'─' * (55 - len(name))})")
        print(f"  Phrase:   {result['phrase']}")
        print(f"  Expected: {result['expected']}")
        print(f"  Difficulty: {result['difficulty'].upper()}")
        print(f"  Why: {result['breaks_tts']}")
        print()
    
    print("\n" + "=" * 80)
    print(" RANDOM BATCH (10 phrases)")
    print("=" * 80)
    print()
    
    batch = generator.generate_batch(10)
    for i, phrase_data in enumerate(batch, 1):
        print(f"{i}. [{phrase_data['difficulty'].upper()}] {phrase_data['phrase']}")
        print(f"   → {phrase_data['expected']}")
        print()
    
    print("\n" + "=" * 80)
    print(" DIFFICULTY FILTERING")
    print("=" * 80)
    print()
    
    for diff in ['easy', 'medium', 'hard']:
        print(f"\n{diff.upper()} Difficulty:")
        phrases = generator.generate_batch(3, difficulty=diff)
        for i, p in enumerate(phrases, 1):
            print(f"  {i}. {p['phrase']}")


if __name__ == '__main__':
    main()
