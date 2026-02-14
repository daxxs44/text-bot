import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import numpy as np

class AudioProcessor:
    def __init__(self, silence_thresh=-40, min_silence_len=1000, padding=200):
        """
        Initialize audio processor
        
        Args:
            silence_thresh: Silence threshold in dBFS (default: -40)
            min_silence_len: Minimum length of silence to be considered a pause in ms (default: 1000ms = 1 second)
            padding: Amount of silence to keep around speech in ms (default: 200ms)
        """
        self.silence_thresh = silence_thresh
        self.min_silence_len = min_silence_len
        self.padding = padding
    
    def remove_long_pauses(self, input_path, output_path, max_pause=1000):
        """
        Remove long pauses from audio file while keeping natural speech flow
        
        Args:
            input_path: Path to input audio file
            output_path: Path to save processed audio
            max_pause: Maximum pause length to keep in ms (default: 1000ms = 1 second)
        """
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Detect non-silent chunks
            nonsilent_ranges = detect_nonsilent(
                audio,
                min_silence_len=self.min_silence_len,
                silence_thresh=self.silence_thresh,
                seek_step=10
            )
            
            if not nonsilent_ranges:
                print("Warning: No speech detected in audio")
                # Just copy the original file
                audio.export(output_path, format="mp3")
                return
            
            # Build processed audio
            processed_audio = AudioSegment.empty()
            
            for i, (start, end) in enumerate(nonsilent_ranges):
                # Add the speech segment with padding
                start_with_padding = max(0, start - self.padding)
                end_with_padding = min(len(audio), end + self.padding)
                
                segment = audio[start_with_padding:end_with_padding]
                processed_audio += segment
                
                # Add a natural pause between segments (but not after the last one)
                if i < len(nonsilent_ranges) - 1:
                    # Calculate the gap until next speech
                    next_start = nonsilent_ranges[i + 1][0]
                    gap_length = next_start - end
                    
                    # Add a pause, but cap it at max_pause
                    pause_duration = min(gap_length, max_pause)
                    if pause_duration > 0:
                        silence = AudioSegment.silent(duration=pause_duration)
                        processed_audio += silence
            
            # Normalize audio to prevent clipping
            processed_audio = self._normalize_audio(processed_audio)
            
            # Export processed audio
            processed_audio.export(output_path, format="mp3", bitrate="192k")
            
            # Calculate compression stats
            original_duration = len(audio) / 1000  # Convert to seconds
            processed_duration = len(processed_audio) / 1000
            compression_ratio = (1 - processed_duration / original_duration) * 100
            
            print(f"Audio processed successfully!")
            print(f"Original duration: {original_duration:.2f}s")
            print(f"Processed duration: {processed_duration:.2f}s")
            print(f"Compression: {compression_ratio:.1f}%")
            
        except Exception as e:
            print(f"Error processing audio: {e}")
            # If processing fails, just copy the original
            if os.path.exists(input_path):
                audio = AudioSegment.from_file(input_path)
                audio.export(output_path, format="mp3")
    
    def _normalize_audio(self, audio, target_dBFS=-20.0):
        """
        Normalize audio to target loudness
        
        Args:
            audio: AudioSegment to normalize
            target_dBFS: Target loudness in dBFS (default: -20.0)
        """
        change_in_dBFS = target_dBFS - audio.dBFS
        return audio.apply_gain(change_in_dBFS)
    
    def trim_silence(self, input_path, output_path):
        """
        Trim silence from the beginning and end of audio
        
        Args:
            input_path: Path to input audio file
            output_path: Path to save trimmed audio
        """
        try:
            audio = AudioSegment.from_file(input_path)
            
            # Detect non-silent parts
            nonsilent_ranges = detect_nonsilent(
                audio,
                min_silence_len=500,
                silence_thresh=self.silence_thresh
            )
            
            if nonsilent_ranges:
                start = nonsilent_ranges[0][0]
                end = nonsilent_ranges[-1][1]
                
                # Add small padding
                start = max(0, start - 100)
                end = min(len(audio), end + 100)
                
                trimmed = audio[start:end]
                trimmed.export(output_path, format="mp3", bitrate="192k")
            else:
                # No speech detected, export original
                audio.export(output_path, format="mp3")
                
        except Exception as e:
            print(f"Error trimming audio: {e}")
            raise
    
    def get_audio_info(self, audio_path):
        """
        Get information about an audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with audio information
        """
        try:
            audio = AudioSegment.from_file(audio_path)
            
            return {
                "duration_seconds": len(audio) / 1000,
                "channels": audio.channels,
                "frame_rate": audio.frame_rate,
                "sample_width": audio.sample_width,
                "frame_count": audio.frame_count(),
                "loudness_dBFS": audio.dBFS,
                "max_dBFS": audio.max_dBFS
            }
        except Exception as e:
            print(f"Error getting audio info: {e}")
            return None
    
    def split_on_silence(self, input_path, output_dir, min_silence_len=2000):
        """
        Split audio file into chunks based on silence
        
        Args:
            input_path: Path to input audio file
            output_dir: Directory to save chunks
            min_silence_len: Minimum silence length in ms to split on
            
        Returns:
            List of output file paths
        """
        try:
            audio = AudioSegment.from_file(input_path)
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Detect non-silent chunks
            chunks = detect_nonsilent(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=self.silence_thresh
            )
            
            output_files = []
            
            for i, (start, end) in enumerate(chunks):
                # Extract chunk with padding
                start_with_padding = max(0, start - self.padding)
                end_with_padding = min(len(audio), end + self.padding)
                
                chunk = audio[start_with_padding:end_with_padding]
                
                # Export chunk
                output_path = os.path.join(output_dir, f"chunk_{i:03d}.mp3")
                chunk.export(output_path, format="mp3", bitrate="192k")
                output_files.append(output_path)
            
            return output_files
            
        except Exception as e:
            print(f"Error splitting audio: {e}")
            return []
