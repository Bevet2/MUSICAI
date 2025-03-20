import os
import argparse
from pathlib import Path
import requests
import zipfile
import tqdm

# URLs for genre-specific datasets (you'll need to replace these with actual dataset URLs)
DATASET_URLS = {
    "rock": "https://example.com/rock_dataset.zip",
    "electro": "https://example.com/electro_dataset.zip",
    "jazz": "https://example.com/jazz_dataset.zip",
    "hiphop": "https://example.com/hiphop_dataset.zip",
    "lofi": "https://example.com/lofi_dataset.zip"
}

def download_file(url: str, target_path: Path, chunk_size: int = 8192):
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(target_path, 'wb') as f, tqdm.tqdm(
        desc=target_path.name,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=chunk_size):
            size = f.write(data)
            pbar.update(size)

def extract_dataset(zip_path: Path, extract_path: Path):
    """Extract a dataset zip file"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

def download_datasets(base_dir: str, genres: list = None):
    """Download and prepare datasets for specified genres"""
    base_path = Path(base_dir)
    downloads_path = base_path / "downloads"
    datasets_path = base_path / "datasets"
    
    # Create directories
    downloads_path.mkdir(parents=True, exist_ok=True)
    datasets_path.mkdir(parents=True, exist_ok=True)
    
    # If no genres specified, download all
    if not genres:
        genres = list(DATASET_URLS.keys())
    
    for genre in genres:
        if genre not in DATASET_URLS:
            print(f"Warning: No dataset URL found for genre '{genre}'")
            continue
        
        print(f"\nProcessing {genre} dataset...")
        
        # Download
        zip_path = downloads_path / f"{genre}_dataset.zip"
        if not zip_path.exists():
            print(f"Downloading {genre} dataset...")
            download_file(DATASET_URLS[genre], zip_path)
        
        # Extract
        genre_path = datasets_path / genre
        if not genre_path.exists():
            print(f"Extracting {genre} dataset...")
            extract_dataset(zip_path, genre_path)
        
        print(f"Completed processing {genre} dataset")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download music datasets by genre")
    parser.add_argument("--base-dir", type=str, required=True,
                      help="Base directory for downloading and extracting datasets")
    parser.add_argument("--genres", type=str, nargs="+",
                      help="Specific genres to download (default: all)")
    
    args = parser.parse_args()
    download_datasets(args.base_dir, args.genres)
