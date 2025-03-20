import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
import os
import tempfile
import torch
from models.music_model import MusicGenerationModel

class AudioProcessor:
    def __init__(self):
        self.models = {}
        self.genre_to_idx = {
            "Rock": 0,
            "Electro": 1,
            "Jazz": 2,
            "Hip-Hop": 3,
            "Lo-Fi": 4
        }
        self._load_models()

    def _load_models(self):
        """Load pre-trained models for each genre"""
        models_dir = Path(__file__).parent.parent / "models" / "trained"
        
        for genre in self.genre_to_idx.keys():
            model_path = models_dir / genre.lower() / "latest.pt"
            if model_path.exists():
                model = MusicGenerationModel()
                model.load_state_dict(torch.load(str(model_path)))
                model.eval()
                self.models[genre] = model
            else:
                print(f"Warning: No trained model found for {genre}")

    @staticmethod
    def get_supported_genres():
        """Return list of supported genres"""
        return ["Rock", "Electro", "Jazz", "Hip-Hop", "Lo-Fi"]

    async def generate_remix(self, audio_path: str, target_genre: str, output_dir: str) -> str:
        """
        Generate a remix in the target genre using the trained model
        """
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Load and preprocess the input audio
        y, sr = librosa.load(audio_path, sr=44100)
        
        # Convert to torch tensor
        input_tensor = torch.FloatTensor(y).unsqueeze(0)  # Add channel dimension
        
        # Get the appropriate model
        if target_genre not in self.models:
            raise ValueError(f"No trained model available for genre {target_genre}")
        
        model = self.models[target_genre]
        genre_idx = torch.tensor([self.genre_to_idx[target_genre]])
        
        # Generate remix
        with torch.no_grad():
            output_tensor = model.generate(input_tensor, genre_idx)
            output_audio = output_tensor.squeeze().numpy()
        
        # Save the output
        output_file = output_path / f"remix_{Path(audio_path).stem}_{target_genre}.wav"
        sf.write(str(output_file), output_audio, sr)

        return str(output_file)

    async def create_track(self, audio_path: str, lyrics: str, output_dir: str) -> str:
        """
        Create a new track by combining audio and lyrics
        """
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Load and preprocess the input audio
        y, sr = librosa.load(audio_path, sr=44100)
        
        # For now, just use the Lo-Fi model as base
        input_tensor = torch.FloatTensor(y).unsqueeze(0)
        model = self.models["Lo-Fi"]
        genre_idx = torch.tensor([self.genre_to_idx["Lo-Fi"]])
        
        # Generate base track
        with torch.no_grad():
            output_tensor = model.generate(input_tensor, genre_idx)
            output_audio = output_tensor.squeeze().numpy()
        
        # Save the output
        output_file = output_path / f"creation_{Path(audio_path).stem}.wav"
        sf.write(str(output_file), output_audio, sr)

        return str(output_file)
