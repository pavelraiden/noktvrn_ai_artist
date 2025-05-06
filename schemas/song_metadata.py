from pydantic import BaseModel, HttpUrl
from typing import Optional, List

class SongMetadata(BaseModel):
    """Schema for storing metadata about a generated song."""
    title: str
    artist: str = "AI Artist"
    genre: Optional[str] = None
    style_prompt: Optional[str] = None
    lyrics: Optional[str] = None
    generation_source: str # e.g., 'suno_bas', 'udion_api'
    suno_song_id: Optional[str] = None # Specific ID from Suno UI
    suno_song_url: Optional[HttpUrl] = None # Direct URL to the generated song on Suno
    local_file_path: Optional[str] = None # Path if downloaded locally
    tags: Optional[List[str]] = None
    duration_seconds: Optional[float] = None
    # Add other relevant fields as needed, e.g., bpm, key, instrumentation

