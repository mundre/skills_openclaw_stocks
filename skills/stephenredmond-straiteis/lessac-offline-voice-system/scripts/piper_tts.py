#!/usr/bin/env python3
"""
Piper TTS Handler for OpenClaw
Uses Lessac High Quality voice as default
"""
from piper import PiperVoice
import soundfile as sf
import numpy as np
import sys
import os
import time

class PiperTTS:
    def __init__(self, model_path=None, config_path=None):
        """Initialize Piper TTS with Lessac High voice"""
        self.model_path = model_path or "/root/.openclaw/tts/piper_voice.onnx"
        self.config_path = config_path or "/root/.openclaw/tts/piper_voice.json"
        self.voice = None
        self.load_time = None
        
    def load(self):
        """Load the voice model (one-time cost)"""
        if self.voice is None:
            print(f"Loading Piper voice: {os.path.basename(self.model_path)}", file=sys.stderr)
            start = time.time()
            self.voice = PiperVoice.load(self.model_path, config_path=self.config_path)
            self.load_time = time.time() - start
            print(f"Voice loaded in {self.load_time:.2f}s", file=sys.stderr)
        return self.voice
    
    def text_to_speech(self, text, output_file=None):
        """
        Convert text to speech using Piper TTS
        
        Args:
            text: Text to convert to speech
            output_file: Output WAV file path (default: auto-generated in /tmp)
        
        Returns:
            Path to generated WAV file, or None on error
        """
        if output_file is None:
            # Create temp file
            import tempfile
            output_file = tempfile.mktemp(suffix=".wav", prefix="tts_")
        
        try:
            voice = self.load()
            
            # Generate audio
            start_gen = time.time()
            audio_chunks = voice.synthesize(text)
            
            # Collect audio data
            audio_data = bytearray()
            for chunk in audio_chunks:
                audio_data.extend(chunk.audio_int16_bytes)
            
            if not audio_data:
                print("Error: No audio generated", file=sys.stderr)
                return None
            
            # Save as WAV
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            sf.write(output_file, audio_np, voice.config.sample_rate)
            
            gen_time = time.time() - start_gen
            print(f"Audio generated in {gen_time:.2f}s -> {output_file}", file=sys.stderr)
            
            return output_file
            
        except Exception as e:
            print(f"Error in TTS: {e}", file=sys.stderr)
            return None
    
    def synthesize_to_file(self, text, output_file):
        """Alias for text_to_speech for backward compatibility"""
        return self.text_to_speech(text, output_file)

# Global instance for easy access
_tts_instance = None

def get_tts():
    """Get or create global TTS instance"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = PiperTTS()
    return _tts_instance

def text_to_speech(text, output_file=None):
    """Convenience function for one-off TTS"""
    tts = get_tts()
    return tts.text_to_speech(text, output_file)

if __name__ == "__main__":
    # Command-line interface
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <text> [output_file]", file=sys.stderr)
        print(f"Example: {sys.argv[0]} 'Hello world' output.wav", file=sys.stderr)
        sys.exit(1)
    
    text = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = text_to_speech(text, output_file)
    if result:
        print(result)
        sys.exit(0)
    else:
        sys.exit(1)