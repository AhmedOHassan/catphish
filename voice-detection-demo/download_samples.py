#!/usr/bin/env python3
"""
Download sample audio files for testing the voice detection system.
Downloads sample WAV files from the Resemblyzer repository.
"""

import os
import urllib.request
import sys

# Sample audio files from Resemblyzer repository
SAMPLE_URLS = [
    "https://github.com/resemble-ai/Resemblyzer/raw/master/audio_data/1.wav",
    "https://github.com/resemble-ai/Resemblyzer/raw/master/audio_data/2.wav",
    "https://github.com/resemble-ai/Resemblyzer/raw/master/audio_data/3.wav",
]

ENROLLMENT_DIR = "test_audio/enrollment"


def download_file(url, destination):
    """Download a file from URL to destination."""
    try:
        print(f"Downloading {os.path.basename(destination)}...", end=" ", flush=True)
        urllib.request.urlretrieve(url, destination)
        file_size = os.path.getsize(destination)
        print(f"✅ ({file_size:,} bytes)")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Download sample audio files for enrollment."""
    print("🔽 Downloading sample audio files...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Ensure enrollment directory exists
    os.makedirs(ENROLLMENT_DIR, exist_ok=True)
    
    success_count = 0
    total_count = len(SAMPLE_URLS)
    
    for i, url in enumerate(SAMPLE_URLS, 1):
        filename = f"sample_{i}.wav"
        destination = os.path.join(ENROLLMENT_DIR, filename)
        
        # Skip if file already exists
        if os.path.exists(destination):
            file_size = os.path.getsize(destination)
            print(f"Skipping {filename} (already exists, {file_size:,} bytes)")
            success_count += 1
            continue
        
        if download_file(url, destination):
            success_count += 1
    
    print()
    if success_count == total_count:
        print(f"✅ Successfully downloaded {success_count}/{total_count} files")
        print(f"📁 Files saved to: {ENROLLMENT_DIR}/")
        return 0
    else:
        print(f"⚠️  Downloaded {success_count}/{total_count} files")
        print(f"   Some downloads failed, but you can continue if you have at least 3 files")
        return 1


if __name__ == "__main__":
    sys.exit(main())
