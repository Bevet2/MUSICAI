import yt_dlp
from pathlib import Path
from typing import List, Dict

class YouTubeService:
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True
        }

    async def search_videos(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for videos on YouTube"""
        search_opts = {
            **self.ydl_opts,
            'extract_flat': True,
            'force_generic_extractor': True,
            'default_search': 'ytsearch'
        }

        with yt_dlp.YoutubeDL(search_opts) as ydl:
            try:
                # Perform the search
                results = ydl.extract_info(f'ytsearch{max_results}:{query}', download=False)
                
                # Process results
                videos = []
                if 'entries' in results:
                    for entry in results['entries']:
                        if entry:
                            videos.append({
                                'id': entry['id'],
                                'title': entry['title'],
                                'thumbnail': entry.get('thumbnail', ''),
                                'channel': entry.get('uploader', 'Unknown')
                            })
                return videos
            except Exception as e:
                print(f"Search error: {str(e)}")
                return []

    async def download_audio(self, video_id: str, output_path: str) -> str:
        """Download audio from a YouTube video"""
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Set output template
        download_opts = {
            **self.ydl_opts,
            'outtmpl': output_path
        }

        try:
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                # Download the video
                url = f'https://www.youtube.com/watch?v={video_id}'
                ydl.download([url])
                return output_path
        except Exception as e:
            raise Exception(f"Download error: {str(e)}")

    def get_video_info(self, video_id: str) -> Dict:
        """Get information about a specific video"""
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                url = f'https://www.youtube.com/watch?v={video_id}'
                info = ydl.extract_info(url, download=False)
                return {
                    'id': info['id'],
                    'title': info['title'],
                    'thumbnail': info.get('thumbnail', ''),
                    'channel': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0)
                }
            except Exception as e:
                raise Exception(f"Error getting video info: {str(e)}")
