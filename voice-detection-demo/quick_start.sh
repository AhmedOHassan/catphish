#!/bin/bash
# Quick Start Script for Phase 1-2

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     🚀 Voice Detection Demo - Quick Start               ║"
echo "║     Phase 1-2: Environment Setup + Enrollment           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "enroll.py" ]; then
    echo "❌ Error: Please run this script from the voice-detection-demo directory"
    exit 1
fi

echo "Step 1/4: Installing dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install -r requirements.txt
echo ""

echo "Step 2/4: Verifying installation..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 -c "from resemblyzer import VoiceEncoder; print('✅ Resemblyzer installed')"
python3 -c "import numpy; print('✅ NumPy installed')"
echo ""

echo "Step 3/4: Downloading sample audio files..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 download_samples.py
echo ""

echo "Step 4/4: Creating voice profile..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 enroll.py test_audio/enrollment/*.wav -o demo_profile.json
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         ✅ SETUP COMPLETE!                              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Files created:"
echo "   - demo_profile.json (voice profile)"
echo "   - test_audio/enrollment/*.wav (3 sample files)"
echo ""
echo "🧪 Run tests:"
echo "   ./tests/test_phase1-2.sh"
echo ""
echo "📖 See README.md for next steps"
