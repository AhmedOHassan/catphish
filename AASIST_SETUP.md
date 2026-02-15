# AASIST Setup Guide

## What is AASIST?

AASIST (Audio Anti-Spoofing using Integrated Spectro-Temporal graph attention networks) is a state-of-the-art AI voice detection model that can detect AI-generated/synthesized voices with >95% accuracy. Without AASIST, the system falls back to a simple spectral flatness heuristic with ~60-70% accuracy.

## Why is AASIST not working?

The system currently falls back to the spectral flatness heuristic because:

1. **AASIST model code is not cloned** - The AASIST repository needs to be cloned to `voice-detection-demo/models/aasist`
2. **Model weights are not downloaded** - Pre-trained weights need to be downloaded separately
3. **Dependencies may not be installed** - PyTorch and other dependencies are required

## Setup Instructions

### Option 1: Automated Setup (Recommended)

Run the provided setup script:

```bash
cd voice-detection-demo
./setup.sh
```

This script will:
- Install Python dependencies
- Clone the AASIST repository
- Create necessary directories for model weights
- Verify the setup

### Option 2: Manual Setup

#### Step 1: Install Dependencies

```bash
cd catphish-api/server
pip install -r requirements.txt
```

Key dependencies:
- `torch>=2.0.0` - PyTorch for model inference
- `torchaudio>=2.0.0` - Audio processing
- `soundfile>=0.12.0` - Audio file I/O

#### Step 2: Clone AASIST Repository

```bash
cd voice-detection-demo
mkdir -p models
git clone https://github.com/clovaai/aasist.git models/aasist
```

#### Step 3: Download Model Weights

The AASIST model weights are not included in the repository. You need to download them from one of these sources:

**Option A: Official AASIST Repository**
- Visit: https://github.com/clovaai/aasist
- Download the pre-trained weights (AASIST.pth)
- Place at: `voice-detection-demo/models/aasist/models/weights/AASIST.pth`

**Option B: Alternative Sources**
If the official weights are not available, you may need to:
- Train your own model using the ASVspoof 2019 dataset
- Use alternative pre-trained weights (ensure compatibility)

#### Step 4: Verify Setup

```bash
cd voice-detection-demo
python3 -c "from aasist_inference import AASISTDetector; detector = AASISTDetector(); print('✅ AASIST setup complete')"
```

Expected output:
```
✅ AASIST model loaded on cpu
✅ AASIST setup complete
```

## Directory Structure

After successful setup, you should have:

```
voice-detection-demo/
└── models/
    └── aasist/
        ├── models/
        │   ├── AASIST.py          # Model architecture
        │   └── weights/
        │       └── AASIST.pth     # Pre-trained weights (~XX MB)
        └── ... (other AASIST files)
```

## Troubleshooting

### Issue: "No module named 'torch'"

**Solution:** Install PyTorch
```bash
pip install torch>=2.0.0 torchaudio>=2.0.0
```

### Issue: "AASIST model not available"

**Cause:** The AASIST model code couldn't be imported

**Solutions:**
1. Verify the AASIST repository was cloned correctly:
   ```bash
   ls -la voice-detection-demo/models/aasist/models/AASIST.py
   ```
2. Check if the path resolution is correct in the logs

### Issue: "AASIST weights not found"

**Cause:** Model weights file (AASIST.pth) is missing

**Solutions:**
1. Check if weights exist:
   ```bash
   ls -la voice-detection-demo/models/aasist/models/weights/AASIST.pth
   ```
2. Download weights from the official AASIST repository
3. Place weights in the correct location

### Issue: Still using fallback heuristic after setup

**Debugging steps:**
1. Check the logs for specific error messages
2. Verify all dependencies are installed:
   ```bash
   python3 -c "import torch; import soundfile; print('✅ Dependencies OK')"
   ```
3. Test AASIST directly:
   ```bash
   cd voice-detection-demo
   python3 aasist_inference.py
   ```
4. Check file permissions on the models directory

## Performance Notes

### With AASIST
- **Accuracy:** >95% for AI voice detection
- **Speed:** ~0.5-2 seconds per audio sample (CPU)
- **GPU Acceleration:** Supported (significantly faster with CUDA)
- **Production Ready:** Yes

### Without AASIST (Fallback Heuristic)
- **Accuracy:** ~60-70% for AI voice detection
- **Speed:** ~0.1-0.5 seconds per audio sample
- **Limitations:** 
  - May miss sophisticated AI voices
  - Higher false positive/negative rates
  - Not recommended for production

## Additional Resources

- **AASIST Paper:** "AASIST: Audio Anti-Spoofing using Integrated Spectro-Temporal graph attention networks"
- **AASIST Repository:** https://github.com/clovaai/aasist
- **ASVspoof Challenge:** https://www.asvspoof.org/
- **Voice Detection Demo Guide:** See `voice-detection-demo/USAGE_GUIDE.md`

## Quick Reference

### Check AASIST Status

```bash
# From repository root
python3 -c "
import sys
from pathlib import Path
demo_dir = Path('voice-detection-demo')
models_dir = demo_dir / 'models' / 'aasist'
weights = models_dir / 'models' / 'weights' / 'AASIST.pth'

print(f'voice-detection-demo exists: {demo_dir.exists()}')
print(f'AASIST model exists: {models_dir.exists()}')
print(f'AASIST weights exist: {weights.exists()}')

if weights.exists():
    import os
    size_mb = os.path.getsize(weights) / (1024 * 1024)
    print(f'Weights size: {size_mb:.1f} MB')
"
```

### Enable AASIST

```bash
cd voice-detection-demo
./setup.sh
# Then follow prompts to download weights if needed
```

### Test Voice Detection

```bash
# Test with sample audio
cd voice-detection-demo
python3 verify.py test_audio/legitimate/sample.wav -p demo_profile.json
```

## Support

If you continue to experience issues:
1. Check the application logs for detailed error messages
2. Review the `voice-detection-demo/README.md` for additional setup instructions
3. Ensure all dependencies are correctly installed
4. Verify file permissions on the models directory
