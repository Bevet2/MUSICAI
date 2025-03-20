import argparse
from pathlib import Path
import shutil
from services.model_trainer import GenreModelTrainer
import torch

def train_all_genres(data_dir: str, output_dir: str, epochs: int = 100):
    """Train models for all genres"""
    data_path = Path(data_dir)
    output_path = Path(output_dir)
    
    # Initialize trainer
    trainer = GenreModelTrainer(str(data_path))
    
    # Train each genre
    genres = ["rock", "electro", "jazz", "hiphop", "lofi"]
    for genre in genres:
        print(f"\nTraining model for {genre}...")
        genre_data = data_path / genre
        
        if not genre_data.exists():
            print(f"No dataset found for {genre}, skipping...")
            continue
            
        try:
            # Train the model
            trainer.train_genre_model(genre, epochs=epochs)
            
            # Copy the trained model to the output directory
            genre_output = output_path / genre.lower()
            genre_output.mkdir(parents=True, exist_ok=True)
            
            source = data_path / "models" / genre / f"checkpoint_epoch_{epochs}.pt"
            target = genre_output / "latest.pt"
            
            shutil.copy2(str(source), str(target))
            print(f"Successfully trained and saved model for {genre}")
            
        except Exception as e:
            print(f"Error training model for {genre}: {str(e)}")
            continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train models for all genres")
    parser.add_argument("--data-dir", type=str, required=True,
                      help="Directory containing genre datasets")
    parser.add_argument("--output-dir", type=str, required=True,
                      help="Directory to save trained models")
    parser.add_argument("--epochs", type=int, default=100,
                      help="Number of training epochs")
    
    args = parser.parse_args()
    
    # Make sure CUDA is available
    if not torch.cuda.is_available():
        print("Warning: CUDA not available, training will be slow!")
    
    train_all_genres(args.data_dir, args.output_dir, args.epochs)
