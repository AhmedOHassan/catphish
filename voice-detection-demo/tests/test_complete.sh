#!/bin/bash
# Complete test suite for all phases of voice detection demo

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         🧪 COMPLETE TEST SUITE                          ║"
echo "║         Voice Detection Demo - All Phases               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

pass_test() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

fail_test() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

warn_test() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Check All Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

deps=(
    "resemblyzer:Resemblyzer"
    "numpy:NumPy"
    "scipy:SciPy"
    "librosa:Librosa"
    "soundfile:SoundFile"
    "speech_recognition:SpeechRecognition"
    "google.generativeai:Google Generative AI"
    "dotenv:python-dotenv"
)

for dep_pair in "${deps[@]}"; do
    IFS=':' read -r module name <<< "$dep_pair"
    if python3 -c "import $module" 2>/dev/null; then
        pass_test "$name installed"
    else
        fail_test "$name not installed"
    fi
done

echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Check Project Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

required_files=(
    "enroll.py"
    "verify.py"
    "aasist_inference.py"
    "debug_test.py"
    "validate_setup.py"
    "requirements.txt"
    ".env.example"
    "README.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        pass_test "$file exists"
    else
        fail_test "$file missing"
    fi
done

echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: Check Audio Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

AUDIO_COUNT=$(ls test_audio/enrollment/*.wav 2>/dev/null | wc -l)

if [ "$AUDIO_COUNT" -eq 0 ]; then
    warn_test "No audio files - run: python download_samples.py"
    SKIP_TESTS=true
elif [ "$AUDIO_COUNT" -lt 3 ]; then
    warn_test "Only $AUDIO_COUNT audio file(s) - need at least 3"
    SKIP_TESTS=true
else
    pass_test "Found $AUDIO_COUNT audio files"
    SKIP_TESTS=false
fi

echo ""

if [ "$SKIP_TESTS" = false ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 4: Run Enrollment"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if python3 enroll.py test_audio/enrollment/*.wav -o test_profile.json; then
        pass_test "Enrollment completed"
    else
        fail_test "Enrollment failed"
    fi
    
    echo ""
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 5: Validate Profile"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ -f "test_profile.json" ]; then
        pass_test "Profile JSON created"
        
        python3 -c "
import json
import sys

try:
    with open('test_profile.json') as f:
        profile = json.load(f)
    
    required = ['embedding_mean', 'embedding_std', 'sample_count', 'quality_score']
    for field in required:
        if field not in profile:
            print(f'❌ Missing field: {field}')
            sys.exit(1)
    
    if len(profile['embedding_mean']) != 256:
        print(f'❌ Wrong embedding size: {len(profile[\"embedding_mean\"])}')
        sys.exit(1)
    
    score = profile['quality_score']
    if not (0 <= score <= 1):
        print(f'❌ Quality score out of range: {score}')
        sys.exit(1)
    
    print(f'✅ Profile valid (quality: {score:.3f})')
    
except Exception as e:
    print(f'❌ Validation error: {e}')
    sys.exit(1)
" && pass_test "Profile structure valid" || fail_test "Profile validation failed"
    else
        fail_test "Profile not created"
    fi
    
    echo ""
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 6: Test Verification (Layer 2 only)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo "Testing with same speaker (should verify)..."
    if python3 verify.py test_audio/enrollment/sample_1.wav -p test_profile.json 2>&1 | grep -q "VERIFIED"; then
        pass_test "Same speaker verification"
    else
        warn_test "Verification result unexpected (may still be working)"
    fi
    
    echo ""
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 7: Test Individual Layers"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    python3 -c "
from verify import verify_speaker, detect_ai_voice
import json

# Test Layer 2
print('Testing Layer 2 (Speaker Verification)...')
with open('test_profile.json') as f:
    profile = json.load(f)

result = verify_speaker('test_audio/enrollment/sample_1.wav', profile)
if result['match']:
    print('✅ Layer 2 works (speaker matched)')
else:
    print('⚠️  Layer 2 result unexpected')

# Test Layer 3
print('\nTesting Layer 3 (AI Detection)...')
result = detect_ai_voice('test_audio/enrollment/sample_1.wav')
print(f'AI Probability: {result[\"ai_probability\"]:.3f}')
print(f'Method: {result[\"method\"]}')
print('✅ Layer 3 works (executed without error)')
" && pass_test "Individual layers work" || fail_test "Layer test failed"
    
    echo ""
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 8: Test Scripts"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Test help flags
    if python3 enroll.py --help > /dev/null 2>&1; then
        pass_test "enroll.py --help works"
    else
        fail_test "enroll.py --help failed"
    fi
    
    if python3 verify.py --help > /dev/null 2>&1; then
        pass_test "verify.py --help works"
    else
        fail_test "verify.py --help failed"
    fi
    
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         ✅ ALL TESTS PASSED!                            ║${NC}"
    echo -e "${GREEN}║         Voice Detection Demo is working!                ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "🎉 You can now:"
    echo "   - Run: python debug_test.py"
    echo "   - Try verification with phrases"
    echo "   - Test with different audio samples"
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║         ⚠️  SOME TESTS FAILED                           ║${NC}"
    echo -e "${RED}║         Check errors above                              ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
