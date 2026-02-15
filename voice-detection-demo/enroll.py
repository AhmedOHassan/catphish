#!/usr/bin/env python3
"""
Voice Enrollment Script
Creates a voice profile from multiple audio samples for speaker verification.
"""

import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import json
import sys
import argparse


def calculate_quality_score(embeddings):
    """
    Calculate quality score based on pairwise similarity of embeddings.
    Higher score means more consistent voice samples.
    
    Args:
        embeddings: List of embedding arrays
        
    Returns:
        float: Quality score between 0 and 1
    """
    if len(embeddings) < 2:
        return 1.0
    
    # Calculate pairwise cosine similarities
    similarities = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            # Cosine similarity is just the dot product for normalized vectors
            similarity = np.dot(embeddings[i], embeddings[j])
            similarities.append(similarity)
    
    # Return average similarity as quality score
    return float(np.mean(similarities))


def enroll_voice(audio_files, output_profile="voice_profile.json"):
    """
    Create a voice profile from multiple audio samples.
    
    Args:
        audio_files: List of paths to audio files
        output_profile: Path to save the voice profile JSON
        
    Returns:
        dict: Voice profile data
    """
    print("\n🎤 Starting voice enrollment...")
    print(f"📁 Processing {len(audio_files)} audio samples...\n")
    
    # Initialize the voice encoder
    encoder = VoiceEncoder()
    
    embeddings = []
    valid_files = []
    
    # Process each audio file
    for idx, audio_path in enumerate(audio_files, 1):
        try:
            print(f"[{idx}/{len(audio_files)}] Processing: {audio_path}")
            
            # Load and preprocess the audio
            wav = preprocess_wav(Path(audio_path))
            
            # Extract embedding
            embedding = encoder.embed_utterance(wav)
            
            print(f"  ✅ Embedding shape: {embedding.shape}")
            
            embeddings.append(embedding)
            valid_files.append(str(audio_path))
            
        except Exception as e:
            print(f"  ❌ Error processing {audio_path}: {e}")
            continue
    
    if len(embeddings) == 0:
        print("\n❌ No valid audio files were processed!")
        sys.exit(1)
    
    # Convert to numpy array for easier manipulation
    embeddings_array = np.array(embeddings)
    
    # Calculate mean and standard deviation
    embedding_mean = np.mean(embeddings_array, axis=0)
    embedding_std = np.std(embeddings_array, axis=0)
    
    # Calculate quality score
    quality_score = calculate_quality_score(embeddings)
    
    # Create profile dictionary
    profile = {
        "embedding_mean": embedding_mean.tolist(),
        "embedding_std": embedding_std.tolist(),
        "sample_count": len(embeddings),
        "quality_score": quality_score,
        "embedding_shape": list(embeddings_array.shape),
        "source_files": valid_files
    }
    
    # Save to JSON
    with open(output_profile, 'w') as f:
        json.dump(profile, f, indent=2)
    
    # Print summary
    print("\n✅ Voice profile created successfully!")
    print("📊 Profile Statistics:")
    print(f"   Samples used: {len(embeddings)}")
    print(f"   Quality score: {quality_score:.3f}")
    print(f"   Embedding dimensions: {embeddings_array.shape}")
    print(f"💾 Saved to: {output_profile}")
    
    # Quality interpretation
    if quality_score > 0.85:
        print("   ✨ Excellent quality - samples are very consistent")
    elif quality_score > 0.75:
        print("   ✅ Good quality - suitable for verification")
    elif quality_score > 0.65:
        print("   ⚠️  Fair quality - consider adding more samples")
    else:
        print("   ⚠️  Low quality - samples may be from different speakers or poor quality")
    
    return profile


def main():
    parser = argparse.ArgumentParser(
        description="Enroll a voice by creating a profile from audio samples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sample1.wav sample2.wav sample3.wav
  %(prog)s *.wav -o my_profile.json
  %(prog)s enrollment/*.wav --output speaker1.json
        """
    )
    
    parser.add_argument(
        'audio_files',
        nargs='+',
        help='Audio files to process (WAV format recommended)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='voice_profile.json',
        help='Output profile filename (default: voice_profile.json)'
    )
    
    args = parser.parse_args()
    
    # Validate that files exist
    valid_files = []
    for file_path in args.audio_files:
        if Path(file_path).exists():
            valid_files.append(file_path)
        else:
            print(f"⚠️  Warning: File not found: {file_path}")
    
    if not valid_files:
        print("❌ No valid audio files provided!")
        sys.exit(1)
    
    # Run enrollment
    try:
        enroll_voice(valid_files, args.output)
    except KeyboardInterrupt:
        print("\n\n⚠️  Enrollment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Enrollment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
