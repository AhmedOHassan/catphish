#!/usr/bin/env python3
"""
Download sample audio files for testing the voice detection system.
NOTE: This repository already includes sample audio files in test_audio/.
This script is provided as a placeholder for downloading additional samples.
"""

import os
import glob
import sys

ENROLLMENT_DIR = "test_audio/enrollment"


def check_existing_files():
    """Check for existing audio files in the enrollment directory."""
    wav_files = glob.glob(os.path.join(ENROLLMENT_DIR, "*.wav"))
    return wav_files


def main():
    """Check for sample audio files."""
    print("🔽 Checking for sample audio files...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Ensure enrollment directory exists
    os.makedirs(ENROLLMENT_DIR, exist_ok=True)
    
    # Check for existing files
    existing_files = check_existing_files()
    
    if existing_files:
        print(f"✅ Found {len(existing_files)} audio file(s) in {ENROLLMENT_DIR}/:")
        for filepath in sorted(existing_files):
            filename = os.path.basename(filepath)
            file_size = os.path.getsize(filepath)
            print(f"   • {filename} ({file_size:,} bytes)")
        print()
        
        if len(existing_files) >= 3:
            print("✅ You have enough files to create a voice profile!")
            print("   Run: python enroll.py test_audio/enrollment/*.wav -o demo_profile.json")
            return 0
        else:
            print(f"⚠️  Need at least 3 audio files for enrollment (found: {len(existing_files)})")
            print("   Add more .wav files to test_audio/enrollment/")
            return 1
    else:
        print(f"⚠️  No audio files found in {ENROLLMENT_DIR}/")
        print()
        print("To add sample audio files, you can:")
        print("1. Record your own audio samples (3-5 files, WAV format)")
        print("2. Use existing audio files from another source")
        print("3. Create test recordings with:")
        print("   • 'The quick brown fox jumps over the lazy dog'")
        print("   • 'She sells seashells by the seashore'")
        print("   • 'How much wood would a woodchuck chuck'")
        print()
        print("Save files as .wav in: test_audio/enrollment/")
        return 1


if __name__ == "__main__":
    sys.exit(main())
