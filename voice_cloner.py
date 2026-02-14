import os
import json
from pathlib import Path

class VoiceCloner:
    """
    Voice cloning module for generating TTS from saved voice recordings
    
    This uses a simplified approach. For production, you would want to integrate
    with proper voice cloning models like Coqui TTS, Bark, or commercial APIs.
    """
    
    def __init__(self):
        self.models = {}
    
    def train_voice(self, audio_path, output_model_path):
        """
        Train a voice model from an audio recording
        
        Args:
            audio_path: Path to the audio recording
            output_model_path: Path to save the trained model
            
        Returns:
            Path to saved model or None if training failed
        """
        try:
            # Create model directory
            model_dir = Path(output_model_path)
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # In a real implementation, you would:
            # 1. Extract voice features (pitch, tone, cadence, etc.)
            # 2. Train or fine-tune a TTS model
            # 3. Save the model weights
            
            # For this simplified version, we'll save metadata
            # and use the original recording as reference
            metadata = {
                "audio_path": audio_path,
                "created": str(Path(audio_path).stat().st_ctime),
                "type": "reference_based"
            }
            
            metadata_path = model_dir / "model_info.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Voice model prepared at {output_model_path}")
            return str(model_dir)
            
        except Exception as e:
            print(f"Error training voice model: {e}")
            return None
    
    def generate_speech(self, text, model_path, output_path):
        """
        Generate speech from text using a trained voice model
        
        Args:
            text: Text to convert to speech
            model_path: Path to the voice model
            output_path: Path to save generated audio
        """
        try:
            # Load model metadata
            model_dir = Path(model_path)
            metadata_path = model_dir / "model_info.json"
            
            if not metadata_path.exists():
                raise ValueError(f"Model not found at {model_path}")
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # For a real implementation, you would use the trained model here
            # Options include:
            # 1. Coqui TTS (open source)
            # 2. Bark (open source)
            # 3. ElevenLabs API (commercial)
            # 4. Play.ht API (commercial)
            # 5. OpenAI TTS API (commercial)
            
            # IMPLEMENTATION OPTIONS:
            
            # Option 1: Using Coqui TTS (recommended for local)
            self._generate_with_coqui(text, metadata, output_path)
            
            # Option 2: Using pyttsx3 (basic fallback)
            # self._generate_with_pyttsx3(text, output_path)
            
            # Option 3: Using gTTS (requires internet)
            # self._generate_with_gtts(text, output_path)
            
            print(f"Generated speech saved to {output_path}")
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            # Fallback to basic TTS
            self._generate_with_gtts(text, output_path)
    
    def _generate_with_coqui(self, text, metadata, output_path):
        """
        Generate speech using Coqui TTS
        This is a placeholder - install TTS package for full functionality
        """
        try:
            from TTS.api import TTS
            
            # Initialize TTS
            # You can use various models, XTTS is good for voice cloning
            tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)
            
            # Get reference audio
            reference_audio = metadata.get("audio_path")
            
            if reference_audio and os.path.exists(reference_audio):
                # Clone voice and generate
                tts.tts_to_file(
                    text=text,
                    speaker_wav=reference_audio,
                    file_path=output_path,
                    language="en"
                )
            else:
                # Use default voice
                tts.tts_to_file(text=text, file_path=output_path)
                
        except ImportError:
            print("Coqui TTS not installed, falling back to gTTS")
            self._generate_with_gtts(text, output_path)
        except Exception as e:
            print(f"Error with Coqui TTS: {e}, falling back to gTTS")
            self._generate_with_gtts(text, output_path)
    
    def _generate_with_gtts(self, text, output_path):
        """
        Generate speech using Google Text-to-Speech (fallback option)
        """
        try:
            from gtts import gTTS
            
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            
        except ImportError:
            print("gTTS not installed, trying pyttsx3")
            self._generate_with_pyttsx3(text, output_path)
        except Exception as e:
            print(f"Error with gTTS: {e}")
            self._generate_with_pyttsx3(text, output_path)
    
    def _generate_with_pyttsx3(self, text, output_path):
        """
        Generate speech using pyttsx3 (offline, basic quality)
        """
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            
            # Set properties
            engine.setProperty('rate', 150)  # Speed
            engine.setProperty('volume', 0.9)  # Volume
            
            # Get available voices
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)  # Use first available voice
            
            # Save to file
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
        except Exception as e:
            print(f"Error with pyttsx3: {e}")
            raise ValueError("All TTS engines failed")
    
    def list_available_models(self, voices_dir):
        """
        List all available voice models
        
        Args:
            voices_dir: Directory containing voice models
            
        Returns:
            List of model names
        """
        voices_path = Path(voices_dir)
        models = []
        
        for model_dir in voices_path.iterdir():
            if model_dir.is_dir():
                metadata_path = model_dir / "model_info.json"
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        models.append({
                            "name": model_dir.name,
                            "path": str(model_dir),
                            "metadata": metadata
                        })
        
        return models
    
    def delete_model(self, model_path):
        """
        Delete a voice model
        
        Args:
            model_path: Path to the model directory
        """
        try:
            import shutil
            model_dir = Path(model_path)
            
            if model_dir.exists() and model_dir.is_dir():
                shutil.rmtree(model_dir)
                print(f"Deleted model at {model_path}")
                return True
            else:
                print(f"Model not found at {model_path}")
                return False
                
        except Exception as e:
            print(f"Error deleting model: {e}")
            return False


# Advanced implementation notes:
"""
For production-quality voice cloning, consider these options:

1. COQUI TTS (Open Source, Local):
   - Install: pip install TTS
   - Model: xtts_v2 (supports voice cloning)
   - Pros: Free, runs locally, good quality
   - Cons: Requires GPU for fast inference

2. BARK (Open Source, Local):
   - Install: pip install bark
   - Pros: High quality, can clone voices
   - Cons: Slow without GPU, large model

3. ElevenLabs API (Commercial):
   - Install: pip install elevenlabs
   - Pros: Excellent quality, fast, easy to use
   - Cons: Paid API, requires internet

4. OpenAI TTS API (Commercial):
   - Use: openai.audio.speech.create()
   - Pros: Good quality, reliable
   - Cons: No true voice cloning, predefined voices only

5. Play.ht API (Commercial):
   - Pros: High quality, voice cloning support
   - Cons: Paid, requires internet

For this bot, Coqui TTS with XTTS model is recommended for best results
without requiring external APIs or payment.
"""
