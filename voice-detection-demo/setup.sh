#!/bin/bash
# Voice Detection Demo - Complete Setup Script
# This script sets up everything needed to run the demo

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     🚀 Voice Detection Demo - Complete Setup            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "enroll.py" ]; then
    echo "❌ Error: Please run this script from the voice-detection-demo directory"
    exit 1
fi

# Step 1: Install Python dependencies
echo "Step 1/6: Installing Python dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install -r requirements.txt
echo ""

# Step 2: Verify core packages
echo "Step 2/6: Verifying installation..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Required packages:"
python3 -c "import numpy; print('✅ NumPy')"
python3 -c "import scipy; print('✅ SciPy')"
python3 -c "import torch; print('✅ PyTorch')"
python3 -c "import torchaudio; print('✅ TorchAudio')"
python3 -c "from resemblyzer import VoiceEncoder; print('✅ Resemblyzer')"
python3 -c "import librosa; print('✅ Librosa')"
python3 -c "import soundfile; print('✅ SoundFile')"
python3 -c "import speech_recognition; print('✅ SpeechRecognition')"
python3 -c "from google import genai; print('✅ Google Generative AI')"
python3 -c "import dotenv; print('✅ python-dotenv')"
echo ""

# Step 3: Setup environment file
echo "Step 3/6: Setting up environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ! -f ".env.example" ]; then
    echo "⚠️  .env.example file not found"
    echo "   Creating basic .env file..."
    echo "# Voice Detection Demo - Environment Variables" > .env
    echo "" >> .env
    echo "# Get your API key from: https://aistudio.google.com/app/apikey" >> .env
    echo "GEMINI_API_KEY=your_api_key_here" >> .env
    echo "⚠️  Created .env file - add your GEMINI_API_KEY"
elif [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Created .env file from template"
    echo "   ➜ Add your GEMINI_API_KEY to .env"
    echo "   ➜ Get key: https://aistudio.google.com/app/apikey"
else
    echo "✅ .env file exists"
    if grep -q "GEMINI_API_KEY=your" .env 2>/dev/null || grep -q "GEMINI_API_KEY=$" .env 2>/dev/null; then
        echo "⚠️  GEMINI_API_KEY appears unset - please add your key to .env"
    else
        echo "✅ GEMINI_API_KEY appears configured"
    fi
fi
echo ""

# Step 4: Download sample audio files
echo "Step 4/6: Downloading sample audio files..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "download_samples.py" ]; then
    python3 download_samples.py
    echo "✅ Sample audio downloaded"
else
    echo "⚠️  download_samples.py not found"
    echo "   Create test_audio directories manually and add .wav files"
    mkdir -p test_audio/{enrollment,legitimate,different_speaker,ai_voice}
fi
echo ""

# Step 5: Setup AASIST model (Layer 3 AI Detection) - OPTIONAL
echo "Step 5/6: Setting up AASIST model (OPTIONAL)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Note: AASIST is optional. System will use spectral flatness heuristic if unavailable."
echo ""
mkdir -p models/aasist/models/weights

if [ ! -d "models/aasist/.git" ]; then
    echo "Cloning AASIST repository..."
    if git clone https://github.com/clovaai/aasist.git models/aasist 2>&1; then
        echo "✅ AASIST repository cloned"
    else
        echo "⚠️  AASIST clone failed (continuing without it)"
    fi
else
    echo "✅ AASIST repository exists"
fi

if [ -f "models/aasist/models/weights/AASIST.pth" ]; then
    echo "✅ AASIST weights found ($(du -h models/aasist/models/weights/AASIST.pth | cut -f1))"
    echo "   AI detection will use AASIST model (high accuracy)"
else
    echo "⚠️  AASIST weights not found"
    echo "   The system will use spectral flatness fallback (lower accuracy)"
    echo "   To add AASIST:"
    echo "   1. Download weights from: https://github.com/clovaai/aasist/releases"
    echo "   2. Place at: models/aasist/models/weights/AASIST.pth"
fi
echo ""

# Step 6: Create demo profile (if enrollment audio exists)
echo "Step 6/6: Creating demo voice profile..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ENROLLMENT_COUNT=$(ls test_audio/enrollment/*.wav 2>/dev/null | wc -l)
if [ "$ENROLLMENT_COUNT" -ge 3 ]; then
    echo "Found $ENROLLMENT_COUNT enrollment audio files"
    if python3 enroll.py test_audio/enrollment/*.wav -o demo_profile.json 2>&1; then
        echo "✅ Demo profile created successfully"
    else
        echo "⚠️  Profile creation had issues - you can try again manually:"
        echo "   python enroll.py test_audio/enrollment/*.wav -o demo_profile.json"
    fi
else
    echo "⚠️  Need at least 3 audio files for enrollment (found: $ENROLLMENT_COUNT)"
    if [ "$ENROLLMENT_COUNT" -eq 0 ]; then
        echo "   Run: python download_samples.py"
    else
        echo "   Add more .wav files to test_audio/enrollment/"
    fi
fi
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         ✅ SETUP COMPLETE                               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Checklist:"

# Check each component
if [ -f ".env" ] && ! grep -q "GEMINI_API_KEY=your" .env 2>/dev/null && ! grep -q "GEMINI_API_KEY=$" .env 2>/dev/null; then
    echo "   ✅ GEMINI_API_KEY configured"
else
    echo "   ⚠️  GEMINI_API_KEY - needs to be set in .env"
fi

if [ -f "models/aasist/models/weights/AASIST.pth" ]; then
    echo "   ✅ AASIST model weights"
else
    echo "   ⚠️  AASIST weights - will use fallback heuristic"
fi

if [ "$ENROLLMENT_COUNT" -ge 3 ]; then
    echo "   ✅ Sample audio files ($ENROLLMENT_COUNT files)"
else
    echo "   ⚠️  Sample audio - run: python download_samples.py"
fi

if [ -f "demo_profile.json" ]; then
    echo "   ✅ Demo voice profile"
else
    echo "   ⚠️  Demo profile - create after adding audio files"
fi

echo ""
echo "🧪 Validate setup:    python validate_setup.py"
echo "🔬 Run full tests:    python debug_test.py"
echo "📝 Enroll voice:      python enroll.py test_audio/enrollment/*.wav -o profile.json"
echo "✅ Verify voice:      python verify.py test.wav -p profile.json -e 'expected phrase'"
echo ""
echo "📖 Documentation:     README.md, USAGE_GUIDE.md"