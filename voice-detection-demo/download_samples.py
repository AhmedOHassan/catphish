#!/usr/bin/env python3
"""
Helper script to download sample audio files from Resemblyzer repository.
"""

import os
import urllib.request
from pathlib import Path


def download_sample_audio():
    """Download sample audio files for testing."""
    
    print("📥 Downloading sample audio files from Resemblyzer repository...\n")
    
    # Create enrollment directory if it doesn't exist
    enrollment_dir = Path("test_audio/enrollment")
    enrollment_dir.mkdir(parents=True, exist_ok=True)
    
    # URLs to sample audio files
    base_url = "https://github.com/resemble-ai/Resemblyzer/raw/master/audio_data"
    samples = [
        ("1.wav", "sample_1.wav"),
        ("2.wav", "sample_2.wav"),
        ("3.wav", "sample_3.wav"),
    ]
    
    success_count = 0
    
    for source, target in samples:
        url = f"{base_url}/{source}"
        output_path = enrollment_dir / target
        
        try:
            print(f"Downloading {target}...")
            urllib.request.urlretrieve(url, output_path)
            
            # Check file size
            size = os.path.getsize(output_path)
            print(f"  ✅ Downloaded {target} ({size:,} bytes)")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed to download {target}: {e}")
    
    print(f"\n✅ Successfully downloaded {success_count}/{len(samples)} files")
    print(f"📁 Files saved to: {enrollment_dir}")
    
    if success_count > 0:
        print("\n💡 Next steps:")
        print("   1. Run: python enroll.py test_audio/enrollment/*.wav")
        print("   2. This will create a voice_profile.json file")


if __name__ == "__main__":
    download_sample_audio()
