"""
AASIST Inference Helper
Loads and runs AASIST model for AI voice detection
"""

import sys
import torch
import numpy as np
import soundfile as sf
from pathlib import Path

# Add AASIST models directory to path
AASIST_DIR = Path(__file__).parent / "models" / "aasist"
sys.path.insert(0, str(AASIST_DIR))

try:
    from models.AASIST import Model as AASIST
except ImportError:
    AASIST = None


class AASISTDetector:
    """Wrapper for AASIST anti-spoofing model"""
    
    def __init__(self, model_path=None):
        """
        Initialize AASIST model
        
        Args:
            model_path: Path to model weights (default: models/aasist/models/weights/AASIST.pth)
        """
        if AASIST is None:
            raise ImportError("AASIST model not available")
        
        if model_path is None:
            model_path = AASIST_DIR / "models" / "weights" / "AASIST.pth"
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Model configuration (from AASIST.conf)
        self.model_config = {
            "architecture": "AASIST",
            "nb_samp": 64600,
            "first_conv": 128,
            "filts": [70, [1, 32], [32, 32], [32, 64], [64, 64]],
            "gat_dims": [64, 32],
            "pool_ratios": [0.5, 0.7, 0.5, 0.5],
            "temperatures": [2.0, 2.0, 100.0, 100.0]
        }
        
        # Load model
        self.model = AASIST(self.model_config).to(self.device)
        
        # Load weights
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(checkpoint)
        self.model.eval()
        
        print(f"✅ AASIST model loaded on {self.device}")
    
    def predict(self, audio_path):
        """
        Predict if audio is AI-generated
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            dict: {
                'ai_probability': float (0-1),
                'is_ai': bool,
                'confidence': float (0-1)
            }
        """
        # Load audio
        audio, sr = sf.read(audio_path)
        
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        
        # Pad or truncate to expected length (64600 samples)
        target_length = self.model_config['nb_samp']
        if len(audio) < target_length:
            # Pad with zeros
            audio = np.pad(audio, (0, target_length - len(audio)))
        else:
            # Truncate
            audio = audio[:target_length]
        
        # Convert to tensor
        audio_tensor = torch.FloatTensor(audio).unsqueeze(0).to(self.device)
        
        # Run inference
        with torch.no_grad():
            output = self.model(audio_tensor)
            
            # Output is [batch, 2] logits for [bonafide, spoof]
            # Apply softmax to get probabilities
            probs = torch.softmax(output, dim=1)
            
            # Probability that audio is spoofed (AI-generated)
            ai_probability = probs[0, 1].item()
        
        # Determine if AI (threshold at 0.5)
        is_ai = ai_probability > 0.5
        
        # Confidence is distance from uncertain (0.5)
        confidence = abs(ai_probability - 0.5) * 2
        
        return {
            'ai_probability': float(ai_probability),
            'is_ai': is_ai,
            'confidence': float(confidence),
            'method': 'AASIST'
        }


def test_aasist():
    """Test function"""
    detector = AASISTDetector()
    print("AASIST detector initialized successfully!")
    return detector


if __name__ == "__main__":
    test_aasist()
