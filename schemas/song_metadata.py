# schemas/song_metadata.py

from typing import Optional
from pydantic import BaseModel, HttpUrl

class SongMetadata(BaseModel):
    """Pydantic schema for metadata extracted after a song generation process,
    specifically targeting Suno BAS output.
    """
    title: str
    duration: Optional[str] = None # Duration might not always be available immediately
    model_used: str
    persona: Optional[str] = None # Persona might not always be used or extracted
    suno_link: Optional[HttpUrl] = None # Use HttpUrl for validation
    retries: int = 0 # Number of retries during the generation process

    class Config:
        # Example for adding schema documentation in OpenAPI/JSON Schema
        schema_extra = {
            "example": {
                "title": "Cosmic Lullaby",
                "duration": "02:35",
                "model_used": "v4.5",
                "persona": "Starlight Dreamer",
                "suno_link": "https://suno.com/song/1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6",
                "retries": 1
            }
        }

