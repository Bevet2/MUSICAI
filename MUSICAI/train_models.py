import argparse
from pathlib import Path
import torch
from services.model_trainer import GenreModelTrainer
from models.music_model import MusicGenerationModel

def train_genre_models(base_dir: str, genres: list = None, epochs: int = 100):
    """Train models for each genre"""
    base_path = Path(base_dir)
    
    # Initialize trainer
    trainer = GenreModelTrainer(base_dir)
    
    # If no genres specified, use all available datasets
    if not genres:
        genres = [d.name for d in (base_path / "datasets").iterdir() if d.is_dir()]
    
    for genre in genres:
        print(f"\nTraining model for {genre}...")
        
        # Check if dataset exists
        dataset_path = base_path / "datasets" / genre
        if not dataset_path.exists():
            print(f"Warning: No dataset found for genre '{genre}'")
            continue
        
        try:
            # Train model
            trainer.train_genre_model(genre, epochs=epochs)
            print(f"Successfully trained model for {genre}")
            
        except Exception as e:
            print(f"Error training model for {genre}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train music generation models by genre")
    parser.add_argument("--base-dir", type=str, required=True,
                      help="Base directory containing datasets and for saving models")
    parser.add_argument("--genres", type=str, nargs="+",
                      help="Specific genres to train (default: all available)")
    parser.add_argument("--epochs", type=int, default=100,
                      help="Number of training epochs")
    
    args = parser.parse_args()
    train_genre_models(args.base_dir, args.genres, args.epochs)
