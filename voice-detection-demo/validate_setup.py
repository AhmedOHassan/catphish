#!/usr/bin/env python3
"""
Validation script to check if setup is complete.
Updated for new Gemini API and AASIST requirements.
"""

import sys
from pathlib import Path


def check_import(module_name, package_name=None):
    """Check if a module can be imported."""
    if package_name is None:
        package_name = module_name
    try:
        __import__(module_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} (run: pip install {package_name.lower().replace(' ', '-')})")
        return False


def check_file(filepath, description):
    """Check if a file exists."""
    path = Path(filepath)
    if path.exists():
        size = path.stat().st_size
        if size > 0:
            print(f"✅ {description} ({size:,} bytes)")
            return True
        else:
            print(f"⚠️  {description} (empty file)")
            return False
    else:
        print(f"❌ {description} (not found)")
        return False


def check_directory(dirpath, description):
    """Check if a directory exists."""
    path = Path(dirpath)
    if path.exists() and path.is_dir():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} (not found)")
        return False


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     🔍 Voice Detection Demo - Setup Validation          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    checks_passed = 0
    checks_failed = 0
    checks_warned = 0
    
    # Check Python version
    print("🐍 Python Environment")
    print("─" * 60)
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 9:
        print("✅ Python version is compatible (3.9+)")
        checks_passed += 1
    elif version.major >= 3 and version.minor >= 7:
        print("⚠️  Python 3.9+ recommended (you have {}.{})".format(version.major, version.minor))
        checks_warned += 1
    else:
        print("❌ Python 3.9+ required")
        checks_failed += 1
    print()
    
    # Check dependencies
    print("📦 Core Dependencies")
    print("─" * 60)
    
    deps = [
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("torch", "PyTorch"),
        ("torchaudio", "TorchAudio"),
        ("resemblyzer", "Resemblyzer"),
        ("librosa", "Librosa"),
        ("soundfile", "SoundFile"),
        ("speech_recognition", "SpeechRecognition"),
        ("google.genai", "Google Generative AI (NEW)"),
        ("dotenv", "python-dotenv"),
    ]
    
    for module, name in deps:
        if check_import(module, name):
            checks_passed += 1
        else:
            checks_failed += 1
    print()
    
    # Check for old Gemini API
    print("🔍 API Version Check")
    print("─" * 60)
    try:
        import google.generativeai
        print("⚠️  Old google-generativeai package detected")
        print("   Consider uninstalling: pip uninstall google-generativeai")
        checks_warned += 1
    except ImportError:
        print("✅ Old API not installed (good)")
        checks_passed += 1
    
    try:
        from google import genai
        print("✅ New google-genai package available")
        checks_passed += 1
    except ImportError:
        print("❌ New google-genai package missing")
        print("   Install: pip install google-genai")
        checks_failed += 1
    print()
    
    # Check project structure
    print("📁 Project Structure")
    print("─" * 60)
    
    files = [
        ("requirements.txt", "requirements.txt"),
        ("enroll.py", "enroll.py"),
        ("verify.py", "verify.py"),
        ("demo.py", "demo.py"),
        (".env.example", ".env.example"),
        (".gitignore", ".gitignore"),
        ("README.md", "README.md"),
    ]
    
    for filepath, description in files:
        if check_file(filepath, description):
            checks_passed += 1
        else:
            checks_failed += 1
    print()
    
    # Check AASIST model
    print("🤖 AASIST Model (Optional)")
    print("─" * 60)
    aasist_weights = Path("models/aasist/models/weights/AASIST.pth")
    if aasist_weights.exists():
        size_mb = aasist_weights.stat().st_size / (1024 * 1024)
        print(f"✅ AASIST weights found ({size_mb:.2f} MB)")
        checks_passed += 1
    else:
        print("⚠️  AASIST weights not found")
        print("   System will use spectral flatness fallback")
        print("   To add AASIST: clone repo and download weights")
        checks_warned += 1
    print()
    
    # Check directories
    print("📂 Audio Directories")
    print("─" * 60)
    
    dirs = [
        ("test_audio", "test_audio/"),
        ("test_audio/enrollment", "test_audio/enrollment/"),
        ("test_audio/legitimate", "test_audio/legitimate/"),
        ("test_audio/different_speaker", "test_audio/different_speaker/"),
        ("test_audio/ai_voice", "test_audio/ai_voice/"),
    ]
    
    for dirpath, description in dirs:
        if check_directory(dirpath, description):
            checks_passed += 1
        else:
            checks_failed += 1
    print()
    
    # Check for audio files
    print("🎵 Audio Files")
    print("─" * 60)
    enrollment_dir = Path("test_audio/enrollment")
    if enrollment_dir.exists():
        audio_files = list(enrollment_dir.glob("*.wav"))
        if not audio_files:
            print("⚠️  No audio files found in test_audio/enrollment/")
            print("   Run: python download_samples.py")
            checks_warned += 1
        elif len(audio_files) < 3:
            print(f"⚠️  Only {len(audio_files)} audio file(s) found")
            print("   Recommend at least 3 samples for enrollment")
            checks_warned += 1
        else:
            print(f"✅ Found {len(audio_files)} audio files")
            checks_passed += 1
    print()
    
    # Test Resemblyzer functionality
    print("🧪 Functional Tests")
    print("─" * 60)
    
    try:
        from resemblyzer import VoiceEncoder
        encoder = VoiceEncoder()
        print("✅ VoiceEncoder can be instantiated")
        checks_passed += 1
    except Exception as e:
        print(f"❌ VoiceEncoder test failed: {e}")
        checks_failed += 1
    
    try:
        import numpy as np
        test_array = np.random.rand(256)
        similarity = np.dot(test_array, test_array)
        if 0.99 <= similarity <= 1.01:
            print("✅ NumPy operations working")
            checks_passed += 1
        else:
            print(f"⚠️  NumPy test unexpected result: {similarity}")
            checks_warned += 1
    except Exception as e:
        print(f"❌ NumPy test failed: {e}")
        checks_failed += 1
    
    # Test new Gemini API
    try:
        from google import genai
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        
        if api_key:
            print(f"✅ Gemini API key found ({api_key[:10]}...)")
            checks_passed += 1
        else:
            print("⚠️  GEMINI_API_KEY not set in .env")
            print("   Layer 4 (comprehension) will be skipped")
            checks_warned += 1
    except Exception as e:
        print(f"⚠️  Gemini check skipped: {e}")
        checks_warned += 1
    
    print()
    
    # Summary
    print("=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    total = checks_passed + checks_failed + checks_warned
    print(f"✅ Passed:  {checks_passed}/{total}")
    print(f"❌ Failed:  {checks_failed}/{total}")
    print(f"⚠️  Warnings: {checks_warned}/{total}")
    print()
    
    if checks_failed == 0 and checks_warned == 0:
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         ✅ ALL CHECKS PASSED!                           ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        print("🎉 Ready to use!")
        print("   Try: python demo.py")
        return 0
    elif checks_failed == 0:
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         ⚠️  SETUP COMPLETE WITH WARNINGS               ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        print("✅ Core functionality ready")
        print("⚠️  Some optional features may be limited")
        return 0
    else:
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         ⚠️  SOME CHECKS FAILED                          ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        print("🔧 Quick fixes:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Download test audio: python download_samples.py")
        print("   - Add Gemini API key to .env file")
        return 1


if __name__ == "__main__":
    sys.exit(main())
