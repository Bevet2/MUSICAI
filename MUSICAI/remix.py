from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from services.youtube import YouTubeService
from services.audio_processor import AudioProcessor
from services.voice_synthesizer import VoiceSynthesizer
from pathlib import Path

router = APIRouter()
youtube_service = YouTubeService()
audio_processor = AudioProcessor()
voice_synthesizer = VoiceSynthesizer()

class SearchQuery(BaseModel):
    query: str
    max_results: int = 10

class RemixRequest(BaseModel):
    video_id: str
    genre: str
    lyrics: Optional[str] = None
    voice_style: Optional[str] = None

@router.post("/search")
async def search_videos(query: SearchQuery):
    try:
        results = await youtube_service.search_videos(query.query, query.max_results)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/remix")
async def create_remix(request: RemixRequest):
    try:
        # Create output directory
        output_dir = Path("static/output")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Download the video audio
        video_path = await youtube_service.download_audio(
            request.video_id,
            str(output_dir / f"{request.video_id}.mp3")
        )

        # Generate remix
        remix_path = await audio_processor.create_remix(
            video_path,
            request.genre,
            str(output_dir / f"{request.video_id}_{request.genre}_remix.mp3")
        )

        # Add vocals if provided
        if request.lyrics and request.voice_style:
            vocals_path = await voice_synthesizer.generate_vocals(
                request.lyrics,
                request.voice_style,
                str(output_dir),
                tempo=audio_processor.get_tempo(remix_path),
                key=audio_processor.get_key(remix_path)
            )
            
            # Mix vocals with remix
            final_path = str(output_dir / f"{request.video_id}_{request.genre}_final.mp3")
            await audio_processor.mix_tracks(
                [remix_path, vocals_path],
                [0.7, 0.3],  # Mix ratios
                final_path
            )
            remix_path = final_path

        # Return the URL to the remixed audio
        relative_path = str(Path(remix_path).relative_to(Path("static")))
        return {"url": f"/static/{relative_path}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/genres")
async def get_genres():
    return {"genres": audio_processor.get_supported_genres()}
