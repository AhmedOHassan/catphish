#!/usr/bin/env python3
"""
AASIST Setup Status Checker
Verifies if AASIST model is properly configured for AI voice detection.
"""

import sys
from pathlib import Path


def check_aasist_status():
    """Check AASIST setup status and print diagnostic information."""
    
    print("=" * 70)
    print("AASIST AI Voice Detection - Setup Status Checker")
    print("=" * 70)
    print()
    
    # Find repository root
    script_dir = Path(__file__).parent.absolute()
    repo_root = script_dir
    
    # Check voice-detection-demo directory
    demo_dir = repo_root / "voice-detection-demo"
    print(f"1. Checking voice-detection-demo directory...")
    print(f"   Location: {demo_dir}")
    if demo_dir.exists():
        print(f"   Status: ✅ EXISTS")
    else:
        print(f"   Status: ❌ NOT FOUND")
        print(f"   Action: This directory should exist. Check your repository.")
        return False
    print()
    
    # Check models directory
    models_dir = demo_dir / "models"
    print(f"2. Checking models directory...")
    print(f"   Location: {models_dir}")
    if models_dir.exists():
        print(f"   Status: ✅ EXISTS")
    else:
        print(f"   Status: ❌ NOT FOUND")
        print(f"   Action: Run 'cd voice-detection-demo && ./setup.sh'")
        return False
    print()
    
    # Check AASIST repository
    aasist_dir = models_dir / "aasist"
    print(f"3. Checking AASIST model repository...")
    print(f"   Location: {aasist_dir}")
    if aasist_dir.exists():
        print(f"   Status: ✅ EXISTS")
        
        # Check if it's a git repo
        if (aasist_dir / ".git").exists():
            print(f"   Type: Git repository")
        else:
            print(f"   Type: Directory (not a git repo)")
    else:
        print(f"   Status: ❌ NOT FOUND")
        print(f"   Action: Run 'cd voice-detection-demo && ./setup.sh'")
        print(f"           OR manually: git clone https://github.com/clovaai/aasist.git {aasist_dir}")
        return False
    print()
    
    # Check AASIST model file
    model_file = aasist_dir / "models" / "AASIST.py"
    print(f"4. Checking AASIST model code...")
    print(f"   Location: {model_file}")
    if model_file.exists():
        print(f"   Status: ✅ EXISTS")
    else:
        print(f"   Status: ❌ NOT FOUND")
        print(f"   Action: Re-clone AASIST repository or check file structure")
        return False
    print()
    
    # Check weights directory
    weights_dir = aasist_dir / "models" / "weights"
    print(f"5. Checking weights directory...")
    print(f"   Location: {weights_dir}")
    if weights_dir.exists():
        print(f"   Status: ✅ EXISTS")
    else:
        print(f"   Status: ⚠️  NOT FOUND")
        print(f"   Action: Create directory: mkdir -p {weights_dir}")
    print()
    
    # Check model weights
    weights_file = weights_dir / "AASIST.pth"
    print(f"6. Checking AASIST model weights...")
    print(f"   Location: {weights_file}")
    if weights_file.exists():
        import os
        size_mb = os.path.getsize(weights_file) / (1024 * 1024)
        print(f"   Status: ✅ EXISTS")
        print(f"   Size: {size_mb:.1f} MB")
    else:
        print(f"   Status: ❌ NOT FOUND")
        print(f"   Action: Download pre-trained weights from AASIST repository")
        print(f"           See AASIST_SETUP.md for detailed instructions")
        return False
    print()
    
    # Check Python dependencies
    print(f"7. Checking Python dependencies...")
    
    deps_status = {}
    required_deps = {
        'torch': 'PyTorch (AI model framework)',
        'torchaudio': 'PyTorch audio processing',
        'numpy': 'Numerical computing',
        'soundfile': 'Audio file I/O'
    }
    
    all_deps_ok = True
    for dep_name, dep_desc in required_deps.items():
        try:
            __import__(dep_name)
            print(f"   ✅ {dep_name}: {dep_desc}")
        except ImportError:
            print(f"   ❌ {dep_name}: {dep_desc} - NOT INSTALLED")
            all_deps_ok = False
    
    if not all_deps_ok:
        print()
        print(f"   Action: Install dependencies:")
        print(f"           pip install -r catphish-api/server/requirements.txt")
        return False
    print()
    
    # Try to import and initialize AASIST
    print(f"8. Testing AASIST import and initialization...")
    try:
        sys.path.insert(0, str(demo_dir))
        from aasist_inference import AASISTDetector
        print(f"   ✅ aasist_inference module imported successfully")
        
        # Try to initialize (this will test if weights can be loaded)
        print(f"   Initializing AASIST detector...")
        detector = AASISTDetector()
        print(f"   ✅ AASIST detector initialized successfully")
        print(f"   Device: {detector.device}")
        
    except Exception as e:
        print(f"   ❌ Failed to initialize AASIST")
        print(f"   Error: {e}")
        return False
    print()
    
    # Summary
    print("=" * 70)
    print("✅ AASIST SETUP COMPLETE")
    print("=" * 70)
    print()
    print("Your system is ready to use AASIST for AI voice detection!")
    print()
    print("Next steps:")
    print("  - Test voice detection: cd voice-detection-demo && python verify.py")
    print("  - Run API server: cd catphish-api/server && uvicorn main:app")
    print()
    return True


if __name__ == "__main__":
    try:
        success = check_aasist_status()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCheck interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
