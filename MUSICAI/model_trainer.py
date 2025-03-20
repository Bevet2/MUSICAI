import os
import torch
import torchaudio
from pathlib import Path
from typing import List, Dict
import librosa
import numpy as np
from torch.utils.data import Dataset, DataLoader

class MusicDataset(Dataset):
    def __init__(self, audio_dir: str, segment_length: int = 65536):
        """
        Dataset for loading music segments
        
        Args:
            audio_dir: Directory containing audio files
            segment_length: Length of audio segments in samples
        """
        self.audio_dir = Path(audio_dir)
        self.segment_length = segment_length
        self.files = list(self.audio_dir.glob("*.wav"))
        
    def __len__(self):
        return len(self.files)
    
    def __getitem__(self, idx):
        audio_path = self.files[idx]
        waveform, sr = torchaudio.load(audio_path)
        
        # Convert to mono if stereo
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        # Ensure consistent sample rate
        if sr != 44100:
            resampler = torchaudio.transforms.Resample(sr, 44100)
            waveform = resampler(waveform)
        
        # Random segment if audio is longer than segment_length
        if waveform.shape[1] > self.segment_length:
            start = torch.randint(0, waveform.shape[1] - self.segment_length, (1,))
            waveform = waveform[:, start:start + self.segment_length]
        else:
            # Pad if audio is shorter
            padding = self.segment_length - waveform.shape[1]
            waveform = torch.nn.functional.pad(waveform, (0, padding))
        
        return waveform

class GenreModelTrainer:
    def __init__(self, base_dir: str):
        """
        Trainer for genre-specific music generation models
        
        Args:
            base_dir: Base directory for storing datasets and models
        """
        self.base_dir = Path(base_dir)
        self.datasets_dir = self.base_dir / "datasets"
        self.models_dir = self.base_dir / "models"
        
        # Create directories
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def prepare_dataset(self, genre: str, source_files: List[str]):
        """
        Prepare a dataset for a specific genre
        
        Args:
            genre: Genre name
            source_files: List of paths to source audio files
        """
        genre_dir = self.datasets_dir / genre
        genre_dir.mkdir(exist_ok=True)
        
        for file in source_files:
            try:
                # Load and preprocess audio
                y, sr = librosa.load(file, sr=44100)
                
                # Split into segments
                segments = librosa.util.frame(y, frame_length=65536, hop_length=32768)
                
                # Save segments
                for i, segment in enumerate(segments.T):
                    output_path = genre_dir / f"{Path(file).stem}_segment_{i}.wav"
                    librosa.output.write_wav(str(output_path), segment, sr)
                    
            except Exception as e:
                print(f"Error processing {file}: {str(e)}")
    
    def train_genre_model(self, genre: str, epochs: int = 100, batch_size: int = 32):
        """
        Train a model for a specific genre
        
        Args:
            genre: Genre name
            epochs: Number of training epochs
            batch_size: Batch size for training
        """
        dataset = MusicDataset(str(self.datasets_dir / genre))
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Initialize model (you'll need to implement your specific model architecture)
        model = self._create_model()
        optimizer = torch.optim.Adam(model.parameters())
        
        # Training loop
        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                optimizer.zero_grad()
                
                # Forward pass (implement your specific training logic)
                loss = self._training_step(model, batch)
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(dataloader)
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
            
            # Save checkpoint
            if (epoch + 1) % 10 == 0:
                self._save_checkpoint(model, genre, epoch + 1)
    
    def _create_model(self):
        """Create the model architecture (implement your specific architecture)"""
        # This is a placeholder - implement your actual model architecture
        raise NotImplementedError("Implement your model architecture")
    
    def _training_step(self, model, batch):
        """Implement your specific training logic"""
        # This is a placeholder - implement your actual training step
        raise NotImplementedError("Implement your training step")
    
    def _save_checkpoint(self, model, genre: str, epoch: int):
        """Save a model checkpoint"""
        checkpoint_path = self.models_dir / genre / f"checkpoint_epoch_{epoch}.pt"
        checkpoint_path.parent.mkdir(exist_ok=True)
        
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
        }, str(checkpoint_path))

    def load_model(self, genre: str, epoch: int = None):
        """
        Load a trained model for a specific genre
        
        Args:
            genre: Genre name
            epoch: Specific epoch to load, if None loads latest
        """
        genre_dir = self.models_dir / genre
        if not epoch:
            # Find latest checkpoint
            checkpoints = list(genre_dir.glob("checkpoint_epoch_*.pt"))
            if not checkpoints:
                raise ValueError(f"No checkpoints found for genre {genre}")
            checkpoint_path = max(checkpoints, key=lambda p: int(p.stem.split('_')[-1]))
        else:
            checkpoint_path = genre_dir / f"checkpoint_epoch_{epoch}.pt"
        
        if not checkpoint_path.exists():
            raise ValueError(f"Checkpoint {checkpoint_path} not found")
        
        model = self._create_model()
        checkpoint = torch.load(str(checkpoint_path))
        model.load_state_dict(checkpoint['model_state_dict'])
        return model
