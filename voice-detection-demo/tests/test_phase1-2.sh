#!/bin/bash
# Test script for Phase 1-2: Environment Setup and Enrollment

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         🧪 PHASE 1-2 TEST SUITE                         ║"
echo "║         Environment Setup + Enrollment                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function for test results
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
echo "TEST 1: Check Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test Resemblyzer
if python3 -c "from resemblyzer import VoiceEncoder; print('Resemblyzer OK')" 2>/dev/null; then
    pass_test "Resemblyzer installed"
else
    fail_test "Resemblyzer not installed (run: pip install -r requirements.txt)"
fi

# Test NumPy
if python3 -c "import numpy; print('NumPy OK')" 2>/dev/null; then
    pass_test "NumPy installed"
else
    fail_test "NumPy not installed"
fi

# Test JSON
if python3 -c "import json; print('JSON OK')" 2>/dev/null; then
    pass_test "JSON module available"
else
    fail_test "JSON module not available"
fi

echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: Check Project Structure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check files exist
if [ -f "requirements.txt" ]; then
    pass_test "requirements.txt exists"
else
    fail_test "requirements.txt missing"
fi

if [ -f "enroll.py" ]; then
    pass_test "enroll.py exists"
else
    fail_test "enroll.py missing"
fi

if [ -f ".env.example" ]; then
    pass_test ".env.example exists"
else
    fail_test ".env.example missing"
fi

if [ -d "test_audio/enrollment" ]; then
    pass_test "test_audio/enrollment directory exists"
else
    fail_test "test_audio/enrollment directory missing"
fi

echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: Check Test Audio Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

AUDIO_COUNT=$(ls test_audio/enrollment/*.wav 2>/dev/null | wc -l)

if [ "$AUDIO_COUNT" -eq 0 ]; then
    warn_test "No audio files found - run: python download_samples.py"
    echo "      Skipping enrollment tests..."
    SKIP_ENROLLMENT=true
elif [ "$AUDIO_COUNT" -lt 3 ]; then
    warn_test "Only $AUDIO_COUNT audio file(s) found - need at least 3"
    SKIP_ENROLLMENT=true
else
    pass_test "Found $AUDIO_COUNT audio files"
    SKIP_ENROLLMENT=false
fi

echo ""

if [ "$SKIP_ENROLLMENT" = false ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 4: Run Enrollment"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Run enrollment
    if python3 enroll.py test_audio/enrollment/*.wav -o test_profile.json; then
        pass_test "Enrollment completed successfully"
    else
        fail_test "Enrollment failed"
    fi
    
    echo ""
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST 5: Validate Profile JSON"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ -f "test_profile.json" ]; then
        pass_test "test_profile.json created"
        
        # Validate JSON structure
        python3 -c "
import json
import sys

try:
    with open('test_profile.json') as f:
        profile = json.load(f)
    
    # Check required fields
    required = ['embedding_mean', 'embedding_std', 'sample_count', 'quality_score']
    for field in required:
        if field not in profile:
            print(f'❌ Missing field: {field}')
            sys.exit(1)
    
    # Check embedding size
    if len(profile['embedding_mean']) != 256:
        print(f'❌ Wrong embedding size: {len(profile[\"embedding_mean\"])}')
        sys.exit(1)
    
    # Check quality score range
    score = profile['quality_score']
    if not (0 <= score <= 1):
        print(f'❌ Quality score out of range: {score}')
        sys.exit(1)
    
    print(f'✅ Profile structure valid')
    print(f'   - Sample count: {profile[\"sample_count\"]}')
    print(f'   - Quality score: {score:.3f}')
    print(f'   - Embedding dimensions: {len(profile[\"embedding_mean\"])}')
    
except Exception as e:
    print(f'❌ Validation error: {e}')
    sys.exit(1)
" && pass_test "Profile JSON structure valid" || fail_test "Profile JSON validation failed"
        
    else
        fail_test "test_profile.json not created"
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
    echo -e "${GREEN}║         Phase 1-2 Complete                              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║         ❌ SOME TESTS FAILED                            ║${NC}"
    echo -e "${RED}║         Please fix the issues above                     ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
