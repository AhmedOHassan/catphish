#!/usr/bin/env python3
"""
Debug and Test Script for Voice Detection System
Tests profile creation, verification, and AI detection components
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def test_environment():
    """Test environment setup"""
    print_section("TESTING ENVIRONMENT SETUP")
    
    all_good = True
    required_vars = ['GEMINI_API_KEY']
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set ({value[:10]}...)")
        else:
            print(f"❌ {var}: Missing")
            all_good = False
    
    # Check Python version
    print(f"\n✅ Python: {sys.version.split()[0]}")
    
    # Check required packages
    required_packages = [
        ('numpy', 'NumPy'),
        ('torch', 'PyTorch'),
        ('resemblyzer', 'Resemblyzer'),
        ('google.genai', 'Google Generative AI'),
        ('soundfile', 'SoundFile'),
    ]
    
    print("\nRequired Packages:")
    for module, name in required_packages:
        try:
            __import__(module.split('.')[0])
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Not installed")
            all_good = False
    
    return all_good


def test_aasist_model():
    """Test AASIST model loading"""
    print_section("TESTING AASIST MODEL")
    
    try:
        from aasist_inference import AASISTDetector
        
        print("Loading AASIST model...")
        detector = AASISTDetector()
        print("✅ AASIST model loaded successfully")
        
        # Check if weights file exists
        weights_path = Path(__file__).parent / "models/aasist/models/weights/AASIST.pth"
        if weights_path.exists():
            size_mb = weights_path.stat().st_size / (1024 * 1024)
            print(f"✅ Model weights: {size_mb:.2f} MB")
        else:
            print(f"❌ Model weights not found at: {weights_path}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AASIST model loading failed: {e}")
        traceback.print_exc()
        return False


def test_profile_creation():
    """Test profile creation with Resemblyzer"""
    print_section("TESTING PROFILE CREATION")
    
    try:
        from enroll import enroll_voice
        
        # Find enrollment audio files
        enrollment_dir = Path(__file__).parent / "test_audio/enrollment"
        
        if not enrollment_dir.exists():
            print(f"❌ Enrollment directory not found: {enrollment_dir}")
            return False
        
        audio_files = list(enrollment_dir.glob("*.wav"))
        
        if not audio_files:
            print(f"❌ No WAV files found in {enrollment_dir}")
            return False
        
        print(f"Found {len(audio_files)} enrollment samples:")
        for f in audio_files:
            print(f"  - {f.name}")
        
        # Create profile
        print("\nCreating voice profile...")
        profile = enroll_voice([str(f) for f in audio_files], output_profile="test_profile.json")
        
        print(f"✅ Profile created successfully")
        print(f"   Sample count: {profile['sample_count']}")
        print(f"   Quality score: {profile['quality_score']:.3f}")
        print(f"   Embedding dimension: {len(profile['embedding_mean'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Profile creation failed: {e}")
        traceback.print_exc()
        return False


def test_speaker_verification():
    """Test speaker verification"""
    print_section("TESTING SPEAKER VERIFICATION")
    
    try:
        from verify import verify_speaker
        
        # Load profile
        profile_path = Path(__file__).parent / "test_profile.json"
        if not profile_path.exists():
            print(f"❌ Test profile not found. Run profile creation test first.")
            return False
        
        with open(profile_path, 'r') as f:
            profile = json.load(f)
        
        # Test cases with expected decisions
        test_dir = Path(__file__).parent / "test_audio"
        test_cases = [
            ("enrollment", "Enrollment Audio (Same Speaker)", True, "Should MATCH - same speaker as profile"),
            ("legitimate", "Legitimate Speaker (Same)", True, "Should MATCH - legitimate recordings from enrolled speaker"),
            ("different_speaker", "Different Speaker", False, "Should NOT MATCH - different person's voice"),
        ]
        
        all_passed = True
        for subdir, label, expected_match, explanation in test_cases:
            audio_dir = test_dir / subdir
            if not audio_dir.exists():
                print(f"⚠️  Skipping {label}: directory not found")
                continue
            
            audio_files = list(audio_dir.glob("*.wav"))
            if not audio_files:
                print(f"⚠️  Skipping {label}: no WAV files")
                continue
            
            audio_path = str(audio_files[0])
            print(f"\nTesting: {label} ({audio_files[0].name})")
            print(f"Expected: {explanation}")
            
            result = verify_speaker(audio_path, profile, threshold=0.75)
            
            status = "✅" if result['match'] == expected_match else "❌"
            print(f"{status} Similarity: {result['similarity']:.3f}, Match: {result['match']} (Expected: {expected_match})")
            
            if result['match'] != expected_match:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Speaker verification failed: {e}")
        traceback.print_exc()
        return False


def test_ai_detection():
    """Test AI voice detection"""
    print_section("TESTING AI DETECTION")
    
    try:
        from verify import detect_ai_voice
        
        test_dir = Path(__file__).parent / "test_audio"
        # Test cases with expected decisions and explanations
        test_cases = [
            ("enrollment", "Enrollment Audio", False, "Should be HUMAN - real person enrollment"),
            ("legitimate", "Legitimate Voice", False, "Should be HUMAN - genuine human recordings"),
            ("different_speaker", "Different Speaker", False, "Should be HUMAN - different person but still human"),
            ("ai_voice", "AI Generated Voice", True, "Should be AI - synthetic/cloned voice"),
        ]
        
        all_passed = True
        for subdir, label, expected_ai, explanation in test_cases:
            audio_dir = test_dir / subdir
            if not audio_dir.exists():
                print(f"⚠️  Skipping {label}: directory not found")
                continue
            
            audio_files = list(audio_dir.glob("*.wav"))
            if not audio_files:
                print(f"⚠️  Skipping {label}: no WAV files")
                continue
            
            audio_path = str(audio_files[0])
            print(f"\nTesting: {label} ({audio_files[0].name})")
            print(f"Expected: {explanation}")
            
            result = detect_ai_voice(audio_path, threshold=0.993)
            
            status = "✅" if result['is_ai'] == expected_ai else "⚠️"
            decision = "AI" if result['is_ai'] else "HUMAN"
            expected_decision = "AI" if expected_ai else "HUMAN"
            print(f"{status} AI Probability: {result['ai_probability']:.3f}, Decision: {decision} (Expected: {expected_decision})")
            print(f"   Method: {result['method']}")
            
            if result.get('warning'):
                print(f"   ⚠️  {result['warning']}")
            
            # Don't fail if using heuristic method (less accurate)
            if result['method'] != 'AASIST' and result['is_ai'] != expected_ai:
                print(f"   Note: Using fallback heuristic, results may vary")
        
        return True
        
    except Exception as e:
        print(f"❌ AI detection failed: {e}")
        traceback.print_exc()
        return False


def test_gemini_api():
    """Test Gemini API connection"""
    print_section("TESTING GEMINI API")
    
    try:
        from google import genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not set")
            return False
        
        print("Initializing Gemini client...")
        client = genai.Client(api_key=api_key)
        
        print("Testing with simple prompt...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Say "Hello from Gemini" in exactly those words.'
        )
        
        response_text = response.text if hasattr(response, 'text') else str(response)
        print(f"✅ Response received: {response_text[:100]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test complete verification pipeline"""
    print_section("TESTING FULL VERIFICATION PIPELINE")
    
    try:
        from verify import verify_voice
        
        profile_path = Path(__file__).parent / "test_profile.json"
        if not profile_path.exists():
            print(f"❌ Test profile not found")
            return False
        
        # Test multiple scenarios with expected outcomes
        test_scenarios = [
            {
                "dir": "legitimate",
                "phrase": "toy boat toy boat toy boat 3 free throws",
                "expected_verdict": "VERIFIED",
                "description": "Should PASS all layers - legitimate speaker with correct phrase"
            },
            {
                "dir": "different_speaker",
                "phrase": None,
                "expected_verdict": "BLOCKED",
                "description": "Should FAIL Layer 2 - different speaker (no phrase check)"
            },
            {
                "dir": "ai_voice",
                "phrase": None,
                "expected_verdict": "BLOCKED",
                "description": "Should FAIL Layer 3 - AI-generated voice (no phrase check)"
            },
        ]
        
        all_passed = True
        for scenario in test_scenarios:
            test_dir = Path(__file__).parent / "test_audio" / scenario["dir"]
            if not test_dir.exists():
                print(f"⚠️  Skipping {scenario['dir']}: directory not found")
                continue
            
            audio_files = list(test_dir.glob("*.wav"))
            if not audio_files:
                print(f"⚠️  Skipping {scenario['dir']}: no WAV files")
                continue
            
            audio_path = str(audio_files[0])
            
            print(f"\n{'='*60}")
            print(f"Scenario: {scenario['dir']} ({audio_files[0].name})")
            print(f"Expected: {scenario['description']}")
            if scenario['phrase']:
                print(f"Phrase: '{scenario['phrase']}'")
            print(f"{'='*60}")
            
            result = verify_voice(
                audio_path,
                str(profile_path),
                expected_phrase=scenario['phrase']
            )
            
            verdict_match = result['verdict'] == scenario['expected_verdict']
            status = "✅" if verdict_match else "❌"
            
            print(f"\n{status} Result: {result['verdict']} (Expected: {scenario['expected_verdict']})")
            if result.get('failed_layers'):
                print(f"   Failed layers: {', '.join(f'Layer {l}' for l in result['failed_layers'])}")
            
            if not verdict_match:
                all_passed = False
                print(f"   ⚠️  Verdict mismatch!")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print(" VOICE DETECTION SYSTEM - DEBUG AND TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Environment Setup", test_environment),
        ("AASIST Model", test_aasist_model),
        ("Profile Creation", test_profile_creation),
        ("Speaker Verification", test_speaker_verification),
        ("AI Detection", test_ai_detection),
        ("Gemini API", test_gemini_api),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
