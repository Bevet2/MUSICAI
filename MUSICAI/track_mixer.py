import torch
import librosa
import numpy as np
from pathlib import Path
from typing import List, Dict
import soundfile as sf
from .voice_synthesizer import VoiceSynthesizer

class TrackMixer:
    def __init__(self):
        """Initialize track mixer with voice synthesizer"""
        self.voice_synth = VoiceSynthesizer()
        
    async def mix_tracks(self, track_paths: List[str], mix_ratios: List[float], 
                        output_dir: str) -> str:
        """
        Mix multiple tracks together with specified ratios
        
        Args:
            track_paths: List of paths to audio files
            mix_ratios: List of mixing ratios (should sum to 1.0)
            output_dir: Directory to save mixed track
        """
        if len(track_paths) != len(mix_ratios):
            raise ValueError("Number of tracks must match number of mix ratios")
            
        if not np.isclose(sum(mix_ratios), 1.0):
            raise ValueError("Mix ratios must sum to 1.0")
        
        # Load and process each track
        mixed = None
        sr = None
        
        for track_path, ratio in zip(track_paths, mix_ratios):
            # Load audio
            y, current_sr = librosa.load(track_path, sr=None)
            
            # Set sample rate from first track
            if sr is None:
                sr = current_sr
            elif current_sr != sr:
                y = librosa.resample(y, orig_sr=current_sr, target_sr=sr)
            
            # Initialize or add to mix
            if mixed is None:
                mixed = y * ratio
            else:
                # Pad shorter track with zeros
                if len(y) > len(mixed):
                    mixed = np.pad(mixed, (0, len(y) - len(mixed)))
                else:
                    y = np.pad(y, (0, len(mixed) - len(y)))
                mixed += y * ratio
        
        # Normalize
        mixed = librosa.util.normalize(mixed)
        
        # Save mixed track
        output_path = Path(output_dir) / "mixed_track.wav"
        sf.write(str(output_path), mixed, sr)
        
        return str(output_path)
    
    async def create_track(self, source_tracks: List[str], lyrics: str,
                         voice_style: str, output_dir: str) -> str:
        """
        Create a new track by mixing source tracks and adding vocals
        
        Args:
            source_tracks: List of paths to source audio files
            lyrics: Lyrics to add to the track
            voice_style: Voice style to use
            output_dir: Directory to save the output
        """
        try:
            # First mix the source tracks
            mixed_track = await self.mix_tracks(
                source_tracks,
                [1.0/len(source_tracks)] * len(source_tracks),
                output_dir
            )
            
            # Analyze tempo and key of mixed track
            y, sr = librosa.load(mixed_track)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            key = self._estimate_key(y, sr)
            
            # Generate vocals
            vocals_path = await self.voice_synth.generate_vocals(
                lyrics=lyrics,
                voice_style=voice_style,
                output_path=output_dir,
                tempo=tempo,
                key=key
            )
            
            # Mix instrumental with vocals
            final_track = await self.mix_tracks(
                [mixed_track, vocals_path],
                [0.7, 0.3],  # 70% instrumental, 30% vocals
                output_dir
            )
            
            return final_track
            
        except Exception as e:
            raise Exception(f"Error creating track: {str(e)}")
    
    def _estimate_key(self, y: np.ndarray, sr: int) -> str:
        """Estimate the musical key of an audio track"""
        # Extract chromagram
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        
        # Average over time
        chroma_avg = np.mean(chroma, axis=1)
        
        # Find the strongest pitch class
        key_idx = np.argmax(chroma_avg)
        
        # Map to musical key (C, C#, D, etc.)
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return keys[key_idx]
