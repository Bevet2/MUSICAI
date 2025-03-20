import asyncio
import argparse
from pathlib import Path
from services.youtube import YouTubeService

async def collect_all_genres(base_dir: str, songs_per_genre: int = 1000):
    """Collect datasets for all supported genres"""
    youtube_service = YouTubeService()
    base_path = Path(base_dir)
    
    # Create base directory
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Collect each genre
    genres = ["rock", "electro", "jazz", "hiphop", "lofi"]
    for genre in genres:
        print(f"\nCollecting dataset for {genre}...")
        genre_dir = base_path / genre
        
        try:
            downloaded_files = await youtube_service.collect_genre_dataset(
                genre=genre,
                output_dir=str(genre_dir),
                target_count=songs_per_genre
            )
            print(f"Successfully downloaded {len(downloaded_files)} {genre} songs")
            
        except Exception as e:
            print(f"Error collecting {genre} dataset: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect music datasets from YouTube")
    parser.add_argument("--base-dir", type=str, required=True,
                      help="Base directory for downloading datasets")
    parser.add_argument("--songs-per-genre", type=int, default=1000,
                      help="Number of songs to collect per genre")
    
    args = parser.parse_args()
    
    # Run the async collection
    asyncio.run(collect_all_genres(args.base_dir, args.songs_per_genre))
