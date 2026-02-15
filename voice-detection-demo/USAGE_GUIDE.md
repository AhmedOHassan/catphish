# Voice Detection Demo - Complete Usage Guide

## 💡 Usage Examples

### Enrollment

**Basic enrollment:**
```bash
python enroll.py sample1.wav sample2.wav sample3.wav
```

**Custom output file:**
```bash
python enroll.py *.wav -o speaker_john.json
```

**Using glob patterns:**
```bash
python enroll.py test_audio/enrollment/*.wav -o enrollment_profile.json
```

**Get help:**
```bash
python enroll.py --help
```

---

### Verification

**Basic verification (Layers 2 & 3 only):**
```bash
# Speaker matching + AI detection
python verify.py test.wav -p profile.json
```

**Full verification (All layers including Gemini):**
```bash
# Include comprehension check with expected phrase
python verify.py test.wav -p profile.json -e "Red leather yellow leather"
```

**Custom threshold:**
```bash
# Lower threshold = more lenient matching
python verify.py test.wav -p profile.json --threshold 0.70
```

**Get help:**
```bash
python verify.py --help
```

---

## 🔍 Understanding Each Layer

### Layer 2: Speaker Verification (Resemblyzer)

**What it does:**
- Creates 256-dimensional "voice fingerprint" (embedding)
- Compares test audio with enrolled profile
- Uses cosine similarity (dot product for normalized vectors)

**How it works:**
```python
# Enrollment
embedding1 = encoder.embed_utterance(wav1)
embedding2 = encoder.embed_utterance(wav2)
profile = average([embedding1, embedding2, ...])

# Verification
test_embedding = encoder.embed_utterance(test_wav)
similarity = dot_product(test_embedding, profile)

# Decision
if similarity > 0.75:
    return "MATCH"
else:
    return "NO MATCH"
```

**Interpretation:**
- **Similarity > 0.85**: Very strong match (same speaker)
- **Similarity 0.75-0.85**: Acceptable match
- **Similarity 0.60-0.75**: Borderline (re-enroll recommended)
- **Similarity < 0.60**: Different speaker

**Example output:**
```
🔍 LAYER 2: Speaker Verification
────────────────────────────────────────────────────
Similarity score: 0.923
Threshold: 0.75
Status: ✅ MATCH
```

---

### Layer 3: AI Detection

**What it does:**
- Detects if voice is AI-generated
- Tries AASIST model first (if available)
- Falls back to spectral flatness heuristic

**Primary method (AASIST):**
- State-of-the-art anti-spoofing model
- Trained on ASVspoof 2019 dataset
- Requires pre-trained weights (not included)
- 95%+ accuracy when available

**Fallback method (Heuristic):**
- Analyzes spectral flatness of audio
- AI voices tend to have more uniform spectral characteristics
- 60-70% accuracy (not production-ready)
- Automatically used if AASIST unavailable

**How it works:**
```python
# Try AASIST
try:
    model = AASIST()
    ai_score = model.predict(audio)
    method = 'AASIST'
except:
    # Fallback to heuristic
    spectral_flatness = calculate_spectral_flatness(audio)
    ai_score = normalize(spectral_flatness)
    method = 'spectral_flatness_heuristic'

# Decision
if ai_score > 0.5:
    return "AI DETECTED"
else:
    return "HUMAN"
```

**Interpretation:**
- **AI Probability < 0.3**: Likely human
- **AI Probability 0.3-0.7**: Uncertain
- **AI Probability > 0.7**: Likely AI

**Example output:**
```
🤖 LAYER 3: AI Detection
────────────────────────────────────────────────────
⚠️  AASIST not available
⚠️  Using spectral flatness heuristic
AI Probability: 0.189
Threshold: 0.5
Status: ✅ HUMAN
Method: spectral_flatness_heuristic
```

---

### Layer 4: Comprehension Check (Gemini)

**What it does:**
- Transcribes audio using Google Speech Recognition
- Analyzes content with Gemini AI
- Checks for semantic understanding and anomalies

**What it checks:**
1. **Content Match**: Did speaker say the expected phrase?
   - Allows minor variations/mispronunciations
   - Detects completely different phrases

2. **Human Behavior**: Natural speech patterns?
   - Hesitations, self-corrections (good signs)
   - Perfect pronunciation of tongue twisters (suspicious)

3. **Red Flags**:
   - Social engineering attempts
   - Authority claims
   - Commands or instructions
   - Unusual speech patterns

**How it works:**
```python
# 1. Transcribe audio
transcript = speech_recognition.recognize(audio)

# 2. Build context-aware prompt
prompt = f"""
Expected: "{expected_phrase}"
Actual: "{transcript}"
Speaker similarity: {layer2_similarity}
AI probability: {layer3_probability}

Analyze for: content match, human behavior, red flags
"""

# 3. Get Gemini analysis
gemini_result = gemini.analyze(prompt)

# 4. Make recommendation
if gemini_result.recommendation == "BLOCK":
    return "BLOCKED"
```

**Recommendations:**
- **ALLOW**: All checks passed, proceed
- **BLOCK**: Critical failure detected, reject
- **CHALLENGE_AGAIN**: Unclear result, request retry

**Example output:**
```
🧠 LAYER 4: Human Comprehension Check (Gemini)
────────────────────────────────────────────────────
Transcribing audio...
Transcript: "red leather yellow leather"
Expected: "Red leather yellow leather"
Analyzing with Gemini...
Content Match: ✅
Match Confidence: 0.95
Human Behavior Score: 0.88
Recommendation: ALLOW
Reasoning: Speaker said phrase correctly with natural pronunciation
```

**Note:** Layer 4 is optional. If no Gemini API key is configured, it will gracefully skip.

---

## 📊 Decision Logic

### Final Verdict Calculation

```
START
  ↓
Layer 2: Speaker Verification
  ├─ MATCH → Continue
  └─ NO MATCH → BLOCKED (Wrong speaker)
  ↓
Layer 3: AI Detection
  ├─ HUMAN → Continue
  └─ AI → BLOCKED (AI detected)
  ↓
Layer 4: Comprehension Check (if phrase provided)
  ├─ ALLOW → Continue
  ├─ BLOCK → BLOCKED (Failed comprehension)
  └─ CHALLENGE_AGAIN → BLOCKED or retry
  ↓
All Passed → VERIFIED
```

### Example Scenarios

**Scenario 1: Success**
```
Layer 2: ✅ Similarity 0.92 (MATCH)
Layer 3: ✅ AI Prob 0.18 (HUMAN)
Layer 4: ✅ Content match (ALLOW)
━━━━━━━━━━━━━━━━━━━━
Verdict: ✅ VERIFIED
```

**Scenario 2: Wrong Speaker**
```
Layer 2: ❌ Similarity 0.48 (NO MATCH)
━━━━━━━━━━━━━━━━━━━━
Verdict: ❌ BLOCKED
Reason: Speaker mismatch
```

**Scenario 3: AI Detected**
```
Layer 2: ✅ Similarity 0.89 (MATCH)
Layer 3: ❌ AI Prob 0.87 (AI)
━━━━━━━━━━━━━━━━━━━━
Verdict: ❌ BLOCKED
Reason: AI detected
```

**Scenario 4: Wrong Phrase**
```
Layer 2: ✅ Similarity 0.91 (MATCH)
Layer 3: ✅ AI Prob 0.22 (HUMAN)
Layer 4: ❌ Said different phrase (BLOCK)
━━━━━━━━━━━━━━━━━━━━
Verdict: ❌ BLOCKED
Reason: Comprehension failed
```

---

## 🧪 Testing Strategies

### Test Case 1: Same Speaker (Should Pass)

```bash
# Use sample from enrollment
python verify.py test_audio/enrollment/sample_1.wav -p test_profile.json
```

**Expected:**
- Layer 2: Similarity > 0.8
- Layer 3: AI Prob < 0.5
- Verdict: VERIFIED

---

### Test Case 2: Different Speaker (Should Fail Layer 2)

```bash
# Use different speaker's audio
python verify.py test_audio/different_speaker/other.wav -p test_profile.json
```

**Expected:**
- Layer 2: Similarity < 0.6
- Verdict: BLOCKED (Speaker mismatch)

---

### Test Case 3: AI Voice (Should Fail Layer 3)

```bash
# Use AI-generated voice
python verify.py test_audio/ai_voice/elevenlabs.wav -p test_profile.json
```

**Expected:**
- Layer 2: May pass (if trained on target voice)
- Layer 3: AI Prob > 0.5
- Verdict: BLOCKED (AI detected)

**Note:** Requires AASIST for reliable results. Fallback may not catch sophisticated AI.

---

### Test Case 4: Wrong Phrase (Should Fail Layer 4)

```bash
# Speaker says different phrase
python verify.py recording.wav -p test_profile.json -e "Expected phrase"
# Recording contains: "Different phrase"
```

**Expected:**
- Layer 2: MATCH
- Layer 3: HUMAN
- Layer 4: Content mismatch → BLOCK
- Verdict: BLOCKED (Comprehension failed)

---

## 🔧 Configuration Options

### Enrollment Options

```bash
python enroll.py [OPTIONS] audio_files...

Options:
  -o, --output FILE    Output profile filename (default: voice_profile.json)
  --help              Show help message
```

### Verification Options

```bash
python verify.py [OPTIONS] audio_file

Options:
  -p, --profile FILE   Voice profile JSON (required)
  -e, --expected TEXT  Expected phrase for Layer 4 (optional)
  --threshold FLOAT    Speaker similarity threshold (default: 0.75)
  --help              Show help message
```

### Environment Variables (.env)

```bash
# Required for Layer 4 only
GEMINI_API_KEY=your_api_key_here

# Get your key from:
# https://aistudio.google.com/app/apikey
```

---

## 📈 Performance Tuning

### Adjusting Similarity Threshold

**Default: 0.75** (balanced)

```bash
# More lenient (fewer false rejections, more false accepts)
python verify.py test.wav -p profile.json --threshold 0.70

# More strict (more false rejections, fewer false accepts)
python verify.py test.wav -p profile.json --threshold 0.85
```

**Guidelines:**
- **High security**: Use 0.80-0.85
- **Balanced**: Use 0.75 (default)
- **Convenience**: Use 0.70-0.75

### Improving Quality Score

Low enrollment quality score? Try:

1. **More samples**: Use 5+ instead of 3
2. **Longer samples**: 10-15 seconds each
3. **Same conditions**: Same mic, environment, volume
4. **Clear speech**: Avoid background noise
5. **Consistent speaker**: Ensure all samples from same person

### Optimizing Layer 3 (AI Detection)

**Without AASIST (fallback):**
- Accuracy: ~60-70%
- May miss sophisticated AI voices
- Good for basic detection

**With AASIST:**
- Accuracy: ~95%+
- Requires setup and weights
- Production-ready

**To add AASIST:**
1. Clone AASIST repository
2. Download pre-trained weights
3. Install AASIST dependencies
4. Update verify.py import path

---

## 🚨 Common Issues

### Issue 1: Low Quality Score

**Symptoms:**
```
Quality score: 0.52
⚠️  Low quality - check audio quality or speaker consistency
```

**Solutions:**
- Re-record with better quality
- Use same microphone for all samples
- Ensure quiet environment
- Verify same speaker for all files

---

### Issue 2: Layer 4 Skipped

**Symptoms:**
```
⚠️  GEMINI_API_KEY not found
⚠️  Skipping Layer 4
```

**Solutions:**
1. Get API key: https://aistudio.google.com/app/apikey
2. Add to `.env` file:
   ```
   GEMINI_API_KEY=your_actual_key
   ```
3. Verify:
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"
   ```

---

### Issue 3: AASIST Warning

**Symptoms:**
```
⚠️  AASIST not available
⚠️  Using spectral flatness heuristic
```

**Solutions:**
- This is expected behavior
- Fallback heuristic will be used
- To use AASIST, install separately (advanced)

---

### Issue 4: Transcription Failed

**Symptoms:**
```
⚠️  Transcription failed: UnknownValueError
```

**Solutions:**
- Ensure clear audio (no heavy background noise)
- Check audio format (WAV preferred)
- Speak clearly and audibly
- Try recording again

---

## 💡 Best Practices

### For Enrollment

✅ **DO:**
- Use 3-5 samples (5 recommended)
- Record 5-10 seconds per sample
- Use same microphone and environment
- Speak naturally
- Include variety (different phrases)

❌ **DON'T:**
- Mix different speakers
- Use poor quality audio
- Include heavy background noise
- Use overly short clips (< 3 seconds)

### For Verification

✅ **DO:**
- Use same recording conditions as enrollment
- Choose appropriate threshold for use case
- Provide expected phrase for Layer 4 when needed
- Test with known samples first

❌ **DON'T:**
- Skip testing with same-speaker samples
- Assume fallback AI detection is production-ready
- Ignore low quality scores
- Use without understanding each layer

### For Production Use

✅ **DO:**
- Add AASIST for real AI detection
- Set up monitoring and logging
- Implement rate limiting
- Test with diverse scenarios
- Have fallback authentication method

❌ **DON'T:**
- Rely solely on fallback heuristic for Layer 3
- Skip Layer 4 comprehension checks
- Use default thresholds without testing
- Deploy without security review

---

## 📚 Additional Resources

- **Resemblyzer**: https://github.com/resemble-ai/Resemblyzer
- **AASIST**: https://github.com/clovaai/aasist
- **ASVspoof 2019**: https://www.asvspoof.org/
- **Gemini API**: https://ai.google.dev/

---

**For complete implementation details, see:**
- [README.md](README.md) - Main documentation
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details
- [GETTING_STARTED.txt](GETTING_STARTED.txt) - Quick reference
