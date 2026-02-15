# Test Audio Samples

This directory should contain audio samples for testing the voice detection system.

## Directory Structure

- **enrollment/**: 3-5 audio samples from the same speaker for creating a voice profile
- **legitimate/**: Audio samples from the enrolled speaker (should pass verification)
- **different_speaker/**: Audio from different speakers (should fail Layer 2)
- **ai_voice/**: AI-generated voice samples (should fail Layer 3) - optional

## Preparing Test Audio

### Option A: Record Your Own (Recommended)

Record 3-5 samples of yourself saying different phrases:
- Use WAV format
- 16kHz sample rate preferred
- 5-10 seconds each
- Clear audio, minimal background noise

Example phrases:
- "The quick brown fox jumps over the lazy dog"
- "She sells seashells by the seashore"
- "How much wood would a woodchuck chuck"

### Option B: Download Sample Audio

You can download sample audio from the Resemblyzer repository:

```bash
wget https://github.com/resemble-ai/Resemblyzer/raw/master/audio_data/1.wav -O enrollment/sample_1.wav
wget https://github.com/resemble-ai/Resemblyzer/raw/master/audio_data/2.wav -O enrollment/sample_2.wav
wget https://github.com/resemble-ai/Resemblyzer/raw/master/audio_data/3.wav -O enrollment/sample_3.wav
```

### Option C: Generate with TTS (requires gTTS)

```bash
pip install gtts pydub
python ../scripts/generate_test_audio.py
```

## Audio Format Requirements

- **Format**: WAV (16-bit PCM)
- **Sample Rate**: 8kHz - 48kHz (16kHz recommended)
- **Channels**: Mono or Stereo
- **Duration**: 3-30 seconds per sample

## Converting Audio Files

If you have audio in other formats, convert using ffmpeg:

```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
```
