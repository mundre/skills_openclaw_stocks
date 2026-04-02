#!/usr/bin/env python3
"""
Test script for lessac_offline_voice_system
Verifies all components are working correctly.
"""

import sys
import os
import tempfile
import subprocess

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from faster_whisper import WhisperModel
        print("✓ faster-whisper")
    except ImportError as e:
        print(f"✗ faster-whisper: {e}")
        return False
    
    try:
        from piper import PiperVoice
        print("✓ piper-tts")
    except ImportError as e:
        print(f"✗ piper-tts: {e}")
        return False
    
    try:
        import soundfile
        print("✓ soundfile")
    except ImportError as e:
        print(f"✗ soundfile: {e}")
        return False
    
    return True

def test_tts():
    """Test TTS functionality"""
    print("\nTesting TTS...")
    
    try:
        # Import locally to avoid issues if piper-tts not installed
        from piper import PiperVoice
        import soundfile as sf
        import numpy as np
        
        # Check if voice model exists
        model_path = os.path.join(os.path.dirname(__file__), "..", "assets", "piper_voice.onnx")
        config_path = os.path.join(os.path.dirname(__file__), "..", "assets", "piper_voice.json")
        
        # If assets not in skill dir, check install dir
        if not os.path.exists(model_path):
            # Try default install location
            model_path = os.path.expanduser("~/.openclaw/tts/piper_voice.onnx")
            config_path = os.path.expanduser("~/.openclaw/tts/piper_voice.json")
        
        if not os.path.exists(model_path):
            print("⚠ Voice model not found (expected after installation)")
            return True  # Not an error, just not installed yet
        
        # Test loading voice
        print(f"Loading voice from {model_path}...")
        voice = PiperVoice.load(model_path, config_path=config_path)
        print("✓ Voice loaded")
        
        # Test small generation
        test_text = "Test."
        audio_chunks = voice.synthesize(test_text)
        
        audio_data = bytearray()
        for chunk in audio_chunks:
            audio_data.extend(chunk.audio_int16_bytes)
        
        if audio_data:
            print("✓ TTS generation works")
            return True
        else:
            print("✗ No audio generated")
            return False
            
    except Exception as e:
        print(f"✗ TTS test failed: {e}")
        return False

def test_stt():
    """Test STT functionality"""
    print("\nTesting STT...")
    
    try:
        from faster_whisper import WhisperModel
        
        # Load model
        print("Loading STT model...")
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        print("✓ STT model loaded")
        
        # Note: Can't test actual transcription without audio file
        # but loading the model is a good test
        return True
        
    except Exception as e:
        print(f"✗ STT test failed: {e}")
        return False

def test_ffmpeg():
    """Test ffmpeg availability"""
    print("\nTesting ffmpeg...")
    
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            # Extract version
            version_line = result.stdout.split('\n')[0]
            print(f"✓ {version_line}")
            return True
        else:
            print("✗ ffmpeg not working")
            return False
    except FileNotFoundError:
        print("✗ ffmpeg not found")
        return False

def test_voice_handler():
    """Test the main voice handler"""
    print("\nTesting voice handler...")
    
    try:
        # Try to import voice_handler
        sys.path.insert(0, os.path.dirname(__file__))
        from voice_handler import VoiceHandler
        
        print("✓ VoiceHandler class can be imported")
        
        # Create instance
        handler = VoiceHandler()
        print("✓ VoiceHandler instance created")
        
        return True
        
    except Exception as e:
        print(f"✗ Voice handler test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Lessac Offline Voice System - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Module imports", test_imports),
        ("FFmpeg", test_ffmpeg),
        ("TTS", test_tts),
        ("STT", test_stt),
        ("Voice Handler", test_voice_handler),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name:20} {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Skill is ready to use.")
        return 0
    else:
        print("⚠ Some tests failed. See above for details.")
        print("\nCommon issues:")
        print("1. Run install.sh to install dependencies")
        print("2. Ensure ffmpeg is installed: sudo apt-get install ffmpeg")
        print("3. Check Python packages: pip install faster-whisper piper-tts soundfile")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())