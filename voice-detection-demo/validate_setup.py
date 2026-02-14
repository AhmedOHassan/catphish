#!/usr/bin/env python3
"""
Validation script to check if Phase 1-2 setup is complete.
Can be run before having audio files.
"""

import sys


def check_import(module_name, package_name=None):
    """Check if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {package_name or module_name} installed")
        return True
    except ImportError:
        print(f"❌ {package_name or module_name} not installed")
        return False


def check_file(filepath, description):
    """Check if a file exists."""
    from pathlib import Path
    if Path(filepath).exists():
        print(f"✅ {description} exists")
        return True
    else:
        print(f"❌ {description} missing")
        return False


def check_directory(dirpath, description):
    """Check if a directory exists."""
    from pathlib import Path
    if Path(dirpath).is_dir():
        print(f"✅ {description} exists")
        return True
    else:
        print(f"❌ {description} missing")
        return False


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     🔍 Phase 1-2 Validation Check                       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    checks_passed = 0
    checks_failed = 0
    
    # Check Python version
    print("🐍 Python Environment")
    print("─" * 60)
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 7:
        print("✅ Python version is compatible (3.7+)")
        checks_passed += 1
    else:
        print("❌ Python 3.7+ required")
        checks_failed += 1
    print()
    
    # Check dependencies
    print("📦 Dependencies")
    print("─" * 60)
    
    deps = [
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("torch", "PyTorch"),
        ("resemblyzer", "Resemblyzer"),
        ("librosa", "Librosa"),
        ("soundfile", "SoundFile"),
        ("speech_recognition", "SpeechRecognition"),
        ("google.generativeai", "Google Generative AI"),
        ("dotenv", "python-dotenv"),
    ]
    
    for module, name in deps:
        if check_import(module, name):
            checks_passed += 1
        else:
            checks_failed += 1
    print()
    
    # Check project structure
    print("📁 Project Structure")
    print("─" * 60)
    
    files = [
        ("requirements.txt", "requirements.txt"),
        ("enroll.py", "enroll.py"),
        (".env.example", ".env.example"),
        (".gitignore", ".gitignore"),
        ("README.md", "README.md"),
    ]
    
    for filepath, desc in files:
        if check_file(filepath, desc):
            checks_passed += 1
        else:
            checks_failed += 1
    
    dirs = [
        ("test_audio/enrollment", "test_audio/enrollment"),
        ("test_audio/legitimate", "test_audio/legitimate"),
        ("test_audio/different_speaker", "test_audio/different_speaker"),
        ("test_audio/ai_voice", "test_audio/ai_voice"),
        ("tests", "tests directory"),
    ]
    
    for dirpath, desc in dirs:
        if check_directory(dirpath, desc):
            checks_passed += 1
        else:
            checks_failed += 1
    print()
    
    # Check for audio files
    print("🎵 Test Audio Files")
    print("─" * 60)
    from pathlib import Path
    audio_files = list(Path("test_audio/enrollment").glob("*.wav"))
    
    if len(audio_files) == 0:
        print("⚠️  No audio files found in test_audio/enrollment/")
        print("   Run: python download_samples.py")
    elif len(audio_files) < 3:
        print(f"⚠️  Only {len(audio_files)} audio file(s) found")
        print("   Recommend at least 3 samples for enrollment")
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
        print(f"✅ NumPy operations working (test similarity: {similarity:.3f})")
        checks_passed += 1
    except Exception as e:
        print(f"❌ NumPy test failed: {e}")
        checks_failed += 1
    
    try:
        import json
        test_data = {"embedding": [0.1, 0.2, 0.3], "score": 0.85}
        json_str = json.dumps(test_data)
        loaded = json.loads(json_str)
        print("✅ JSON serialization working")
        checks_passed += 1
    except Exception as e:
        print(f"❌ JSON test failed: {e}")
        checks_failed += 1
    print()
    
    # Summary
    print("═" * 60)
    print("📊 VALIDATION SUMMARY")
    print("═" * 60)
    print(f"✅ Checks Passed: {checks_passed}")
    print(f"❌ Checks Failed: {checks_failed}")
    print()
    
    if checks_failed == 0:
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         ✅ ALL CHECKS PASSED!                           ║")
        print("║         Phase 1-2 setup is complete                     ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        print("🚀 Next steps:")
        print("   1. Ensure you have audio files: python download_samples.py")
        print("   2. Run enrollment: python enroll.py test_audio/enrollment/*.wav")
        print("   3. Run full test suite: ./tests/test_phase1-2.sh")
        return 0
    else:
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         ⚠️  SOME CHECKS FAILED                          ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        if checks_failed <= 3:
            print("🔧 Quick fixes:")
            print("   - Install missing dependencies: pip install -r requirements.txt")
            print("   - Download test audio: python download_samples.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
