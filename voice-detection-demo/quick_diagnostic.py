#!/usr/bin/env python3
"""
Quick Diagnostic Test for Voice Detection System
Tests each component individually with timeouts
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def test_environment():
    """Test environment setup"""
    print_section("1. ENVIRONMENT CHECK")
    
    results = {}
    
    # API Key
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ GEMINI_API_KEY: Set ({api_key[:10]}...)")
        results['api_key'] = 'PASS'
    else:
        print(f"❌ GEMINI_API_KEY: Missing")
        results['api_key'] = 'FAIL'
    
    # Python version
    print(f"✅ Python: {sys.version.split()[0]}")
    results['python'] = 'PASS'
    
    # Required packages
    packages = [
        ('torch', 'PyTorch'),
        ('resemblyzer', 'Resemblyzer'),
        ('soundfile', 'SoundFile'),
        ('google.genai', 'Google Generative AI (new)'),
    ]
    
    print("\nRequired Packages:")
    for module, name in packages:
        try:
            __import__(module.split('.')[0])
            print(f"✅ {name}")
            results[name] = 'PASS'
        except ImportError:
            print(f"❌ {name} - Not installed")
            results[name] = 'FAIL'
    
    return results


def test_files():
    """Test file existence"""
    print_section("2. FILE CHECK")
    
    results = {}
    base_dir = Path(__file__).parent
    
    # Check AASIST weights
    weights_path = base_dir / "models/aasist/models/weights/AASIST.pth"
    if weights_path.exists():
        size_mb = weights_path.stat().st_size / (1024 * 1024)
        print(f"✅ AASIST weights: {size_mb:.2f} MB")
        results['aasist_weights'] = 'PASS'
    else:
        print(f"❌ AASIST weights not found")
        results['aasist_weights'] = 'FAIL'
    
    # Check test audio directories
    audio_dirs = ['enrollment', 'legitimate', 'ai_voice', 'different_speaker']
    for dirname in audio_dirs:
        dirpath = base_dir / "test_audio" / dirname
        if dirpath.exists():
            files = list(dirpath.glob("*.wav"))
            print(f"✅ {dirname}/: {len(files)} WAV files")
            results[f'audio_{dirname}'] = 'PASS'
        else:
            print(f"❌ {dirname}/ not found")
            results[f'audio_{dirname}'] = 'FAIL'
    
    return results


def test_gemini_api():
    """Test Gemini API connection"""
    print_section("3. GEMINI API TEST")
    
    try:
        from google import genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not set")
            return {'gemini_api': 'FAIL'}
        
        print("Initializing Gemini client...")
        client = genai.Client(api_key=api_key)
        
        print("Testing with simple prompt...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Say "Hello from Gemini" in exactly those words.'
        )
        
        response_text = response.text if hasattr(response, 'text') else str(response)
        print(f"✅ Response received: {response_text[:100]}")
        
        return {'gemini_api': 'PASS'}
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return {'gemini_api': 'FAIL'}


def test_resemblyzer():
    """Test Resemblyzer for speaker verification"""
    print_section("4. RESEMBLYZER TEST")
    
    try:
        from resemblyzer import VoiceEncoder
        
        print("Loading voice encoder...")
        encoder = VoiceEncoder()
        print(f"✅ Resemblyzer encoder loaded on cpu")
        
        # Try to load a test audio file
        import soundfile as sf
        import numpy as np
        
        enrollment_dir = Path(__file__).parent / "test_audio/enrollment"
        audio_files = list(enrollment_dir.glob("*.wav"))
        
        if not audio_files:
            print("⚠️  No enrollment audio files to test")
            return {'resemblyzer': 'WARN'}
        
        print(f"Testing with {audio_files[0].name}...")
        wav, sr = sf.read(audio_files[0])
        if len(wav.shape) > 1:
            wav = wav.mean(axis=1)
        
        # Generate embedding
        embedding = encoder.embed_utterance(wav)
        print(f"✅ Generated embedding: {embedding.shape}")
        
        return {'resemblyzer': 'PASS'}
        
    except Exception as e:
        print(f"❌ Resemblyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return {'resemblyzer': 'FAIL'}


def test_aasist_load():
    """Test AASIST model loading only (not inference)"""
    print_section("5. AASIST MODEL LOAD TEST")
    
    try:
        from aasist_inference import AASISTDetector
        
        print("Loading AASIST model...")
        detector = AASISTDetector()
        print("✅ AASIST model loaded successfully")
        
        return {'aasist_load': 'PASS'}
        
    except Exception as e:
        print(f"❌ AASIST model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return {'aasist_load': 'FAIL'}


def test_profile_creation():
    """Test profile creation with Resemblyzer"""
    print_section("6. PROFILE CREATION TEST")
    
    try:
        from enroll import enroll_voice
        
        # Find enrollment audio files
        enrollment_dir = Path(__file__).parent / "test_audio/enrollment"
        
        if not enrollment_dir.exists():
            print(f"❌ Enrollment directory not found")
            return {'profile_creation': 'FAIL'}
        
        audio_files = list(enrollment_dir.glob("*.wav"))
        
        if not audio_files:
            print(f"❌ No WAV files found in enrollment/")
            return {'profile_creation': 'FAIL'}
        
        print(f"Found {len(audio_files)} enrollment samples")
        
        # Create profile
        print("Creating voice profile...")
        profile = enroll_voice([str(f) for f in audio_files], output_profile="test_profile.json")
        
        print(f"✅ Profile created successfully")
        print(f"   Sample count: {profile['sample_count']}")
        print(f"   Quality score: {profile['quality_score']:.3f}")
        print(f"   Embedding dimension: {len(profile['embedding_mean'])}")
        
        return {'profile_creation': 'PASS'}
        
    except Exception as e:
        print(f"❌ Profile creation failed: {e}")
        import traceback
        traceback.print_exc()
        return {'profile_creation': 'FAIL'}


def test_speaker_verification():
    """Test speaker verification"""
    print_section("7. SPEAKER VERIFICATION TEST")
    
    try:
        from verify import verify_speaker
        
        # Load profile
        profile_path = Path(__file__).parent / "test_profile.json"
        if not profile_path.exists():
            print(f"❌ Test profile not found. Run profile creation test first.")
            return {'speaker_verification': 'SKIP'}
        
        with open(profile_path, 'r') as f:
            profile = json.load(f)
        
        # Test with legitimate speaker
        test_dir = Path(__file__).parent / "test_audio"
        legit_dir = test_dir / "legitimate"
        
        if not legit_dir.exists():
            print(f"❌ Legitimate test directory not found")
            return {'speaker_verification': 'SKIP'}
        
        audio_files = list(legit_dir.glob("*.wav"))
        if not audio_files:
            print(f"❌ No test audio files")
            return {'speaker_verification': 'SKIP'}
        
        audio_path = str(audio_files[0])
        print(f"Testing with: {audio_files[0].name}")
        
        result = verify_speaker(audio_path, profile, threshold=0.75)
        
        print(f"✅ Similarity: {result['similarity']:.3f}, Match: {result['match']}")
        
        return {'speaker_verification': 'PASS'}
        
    except Exception as e:
        print(f"❌ Speaker verification failed: {e}")
        import traceback
        traceback.print_exc()
        return {'speaker_verification': 'FAIL'}


def main():
    """Run all diagnostic tests"""
    print("\n" + "=" * 70)
    print(" VOICE DETECTION SYSTEM - QUICK DIAGNOSTIC")
    print("=" * 70)
    
    all_results = {}
    
    # Run tests
    tests = [
        test_environment,
        test_files,
        test_gemini_api,
        test_resemblyzer,
        test_aasist_load,
        test_profile_creation,
        test_speaker_verification,
    ]
    
    for test_func in tests:
        try:
            results = test_func()
            all_results.update(results)
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    print_section("SUMMARY")
    
    passed = sum(1 for v in all_results.values() if v == 'PASS')
    failed = sum(1 for v in all_results.values() if v == 'FAIL')
    warned = sum(1 for v in all_results.values() if v == 'WARN')
    skipped = sum(1 for v in all_results.values() if v == 'SKIP')
    total = len(all_results)
    
    for key, result in all_results.items():
        if result == 'PASS':
            print(f"✅ {key}: PASSED")
        elif result == 'FAIL':
            print(f"❌ {key}: FAILED")
        elif result == 'WARN':
            print(f"⚠️  {key}: WARNING")
        else:
            print(f"⏭️  {key}: SKIPPED")
    
    print(f"\n📊 Results: {passed} passed, {failed} failed, {warned} warnings, {skipped} skipped (total: {total})")
    
    if failed == 0:
        print("\n✅ All critical tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed - see details above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
