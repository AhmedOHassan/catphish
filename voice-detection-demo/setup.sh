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
echo "Step 1/5: Installing Python dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install -r requirements.txt
echo ""

# Step 2: Verify core packages
echo "Step 2/5: Verifying installation..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 -c "from resemblyzer import VoiceEncoder; print('✅ Resemblyzer')"
python3 -c "import torch; print('✅ PyTorch')"
python3 -c "from google import genai; print('✅ Google Generative AI')"
python3 -c "import soundfile; print('✅ SoundFile')"
echo ""

# Step 3: Setup environment file
echo "Step 3/5: Setting up environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ! -f ".env" ]; then
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

# Step 4: Setup AASIST model (Layer 3 AI Detection)
echo "Step 4/5: Setting up AASIST model..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
mkdir -p models/aasist/models/weights

if [ ! -d "models/aasist/.git" ]; then
    echo "Cloning AASIST repository..."
    git clone https://github.com/clovaai/aasist.git models/aasist
    echo "✅ AASIST repository cloned"
else
    echo "✅ AASIST repository exists"
fi

if [ -f "models/aasist/models/weights/AASIST.pth" ]; then
    echo "✅ AASIST weights found ($(du -h models/aasist/models/weights/AASIST.pth | cut -f1))"
else
    echo "⚠️  AASIST weights not found"
    echo "   The system will attempt to download weights on first run."
    echo "   If that fails, download manually from AASIST releases and place at:"
    echo "   models/aasist/models/weights/AASIST.pth"
fi
echo ""

# Step 5: Create demo profile (if enrollment audio exists)
echo "Step 5/5: Creating demo voice profile..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ENROLLMENT_FILES=$(find test_audio/enrollment -name "*.wav" 2>/dev/null | head -1)
if [ -n "$ENROLLMENT_FILES" ]; then
    if python3 enroll.py test_audio/enrollment/*.wav -o demo_profile.json 2>&1; then
        echo "✅ Demo profile created"
    else
        echo "⚠️  Profile creation had issues - you can try again manually:"
        echo "   python enroll.py test_audio/enrollment/*.wav -o demo_profile.json"
    fi
else
    echo "⚠️  No enrollment audio found in test_audio/enrollment/"
    echo "   Add your own .wav files and run: python enroll.py test_audio/enrollment/*.wav"
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
    echo "   ⚠️  AASIST weights - will download on first use"
fi

if [ -f "demo_profile.json" ]; then
    echo "   ✅ Demo voice profile"
else
    echo "   ⚠️  Demo profile - create with: python enroll.py <audio_files>"
fi

echo ""
echo "🧪 Validate setup:    python validate_setup.py"
echo "🔬 Run full tests:    python debug_test.py"
echo "🎮 Run demo:          python demo.py"
echo ""
echo "📖 Documentation:     README.md, USAGE_GUIDE.md"
