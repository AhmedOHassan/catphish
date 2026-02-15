#!/usr/bin/env python3
"""
Interactive Voice Detection Demo
Provides user-friendly interface for enrollment and verification.
"""

import sys
from pathlib import Path
import os

# Import functions from our modules
from enroll import enroll_voice
from verify import verify_voice


def print_banner():
    """Display welcome banner."""
    print("""
╔══════════════════════════════════════════════════════════╗
║         🎤 VOICE DETECTION DEMO (Catphish)              ║
║                                                          ║
║  4-Layer Voice Authentication System:                   ║
║    Layer 2: Speaker Verification (Resemblyzer)          ║
║    Layer 3: AI Detection (AASIST/Heuristic)             ║
║    Layer 4: Comprehension Check (Gemini)                ║
╚══════════════════════════════════════════════════════════╝
""")


def print_menu():
    """Display main menu."""
    print("\nChoose a demo:")
    print("  1. Enroll a voice profile")
    print("  2. Verify an audio file")
    print("  3. Full demo (enroll + verify)")
    print("  4. Exit")
    print()


def get_choice():
    """Get user menu choice."""
    while True:
        try:
            choice = input("Your choice (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return int(choice)
            print("❌ Please enter 1, 2, 3, or 4")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)
        except:
            print("❌ Invalid input")


def get_audio_files():
    """Get list of audio files from user."""
    print("\nYou need 3-5 audio samples (WAV format recommended)")
    print("Enter paths to audio files (one per line, empty line to finish):")
    
    audio_files = []
    sample_num = 1
    
    while True:
        try:
            path = input(f"  Sample {sample_num}: ").strip()
            
            if not path:
                if len(audio_files) == 0:
                    print("⚠️  Need at least 1 sample")
                    continue
                break
            
            if not Path(path).exists():
                print(f"❌ File not found: {path}")
                continue
            
            audio_files.append(path)
            sample_num += 1
            
            if len(audio_files) >= 5:
                print("✅ 5 samples collected (recommended maximum)")
                confirm = input("Add more? (y/N): ").strip().lower()
                if confirm != 'y':
                    break
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Cancelled")
            return None
    
    return audio_files


def demo_enrollment():
    """Run enrollment demo."""
    print("\n" + "=" * 60)
    print("📝 ENROLLMENT DEMO")
    print("=" * 60)
    
    # Get audio files
    audio_files = get_audio_files()
    if not audio_files:
        return None
    
    # Get output filename
    default_output = "voice_profile.json"
    output = input(f"\nOutput profile name [{default_output}]: ").strip()
    if not output:
        output = default_output
    
    # Check if file exists
    if Path(output).exists():
        overwrite = input(f"⚠️  {output} exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("⚠️  Cancelled")
            return None
    
    # Run enrollment
    print()
    try:
        profile = enroll_voice(audio_files, output)
        return output
    except Exception as e:
        print(f"\n❌ Enrollment failed: {e}")
        return None


def demo_verification():
    """Run verification demo."""
    print("\n" + "=" * 60)
    print("🔍 VERIFICATION DEMO")
    print("=" * 60)
    
    # Get profile path
    default_profile = "voice_profile.json"
    profile_path = input(f"\nVoice profile [{default_profile}]: ").strip()
    if not profile_path:
        profile_path = default_profile
    
    if not Path(profile_path).exists():
        print(f"❌ Profile not found: {profile_path}")
        return False
    
    # Get audio file
    audio_path = input("Audio file to verify: ").strip()
    if not audio_path:
        print("❌ No audio file provided")
        return False
    
    if not Path(audio_path).exists():
        print(f"❌ Audio file not found: {audio_path}")
        return False
    
    # Get expected phrase (optional)
    print("\nExpected phrase (optional, for Layer 4):")
    print("  Press Enter to skip Layer 4, or type the expected phrase")
    expected_phrase = input("Expected phrase: ").strip()
    if not expected_phrase:
        expected_phrase = None
    
    # Run verification
    try:
        result = verify_voice(audio_path, profile_path, expected_phrase)
        return result['verdict'] == 'VERIFIED'
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_full():
    """Run complete demo: enrollment + verification."""
    print("\n" + "=" * 60)
    print("🚀 FULL DEMO")
    print("=" * 60)
    print("""
This demo will:
  1. Create a voice profile from sample audio
  2. Verify a test audio file against it
  3. Show how all 4 layers work together
""")
    
    input("Press Enter to continue...")
    
    # Step 1: Enrollment
    print("\n" + "─" * 60)
    print("STEP 1: ENROLLMENT")
    print("─" * 60)
    
    profile_path = demo_enrollment()
    if not profile_path:
        print("\n❌ Demo cancelled")
        return
    
    # Step 2: Verification
    print("\n" + "─" * 60)
    print("STEP 2: VERIFICATION")
    print("─" * 60)
    print(f"\nEnrollment complete! Profile saved to: {profile_path}")
    input("\nPress Enter to test verification...")
    
    # Get test audio
    print("\nNow let's verify a test audio file.")
    audio_path = input("Audio file to verify: ").strip()
    
    if not audio_path:
        print("❌ No audio file provided")
        return
    
    if not Path(audio_path).exists():
        print(f"❌ Audio file not found: {audio_path}")
        return
    
    # Get expected phrase
    print("\nExpected phrase (optional, for Layer 4):")
    expected_phrase = input("Expected phrase: ").strip()
    if not expected_phrase:
        expected_phrase = None
    
    # Run verification
    try:
        result = verify_voice(audio_path, profile_path, expected_phrase)
        
        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETE")
        print("=" * 60)
        print(f"\nFinal Result: {result['verdict']}")
        
        if result['verdict'] == 'VERIFIED':
            print("✅ The audio passed all verification layers!")
        else:
            print("❌ The audio was blocked by one or more layers")
            print(f"Failed layers: {', '.join(f'Layer {l}' for l in result['failed_layers'])}")
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main demo loop."""
    print_banner()
    
    while True:
        try:
            print_menu()
            choice = get_choice()
            
            if choice == 1:
                demo_enrollment()
            
            elif choice == 2:
                demo_verification()
            
            elif choice == 3:
                demo_full()
            
            elif choice == 4:
                print("\n👋 Goodbye!")
                break
            
            # Ask if user wants to continue
            print()
            cont = input("Press Enter to return to menu (or 'q' to quit): ").strip().lower()
            if cont == 'q':
                print("\n👋 Goodbye!")
                break
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
            cont = input("\nPress Enter to continue (or 'q' to quit): ").strip().lower()
            if cont == 'q':
                break


if __name__ == "__main__":
    main()
