#!/usr/bin/env python3

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ReleaseMetadata(BaseModel):
    """Defines the structure for the release metadata JSON file."""

    release_id: str = Field(
        ..., description="Unique identifier for this specific release package."
    )
    generation_run_id: str = Field(
        ...,
        description="""The ID of the batch runner cycle that generated this             content.""",
    )
    artist_id: Optional[int] = Field(
        None, description="Unique identifier for the artist."
    )
    artist_name: str = Field(..., description="Name of the AI artist.")
    genre: Optional[str] = Field(
        None, description="Primary genre of the track."
    )
    release_date: str = Field(
        ..., description="Date the release package was created (YYYY-MM-DD)."
    )
    track_title: Optional[str] = Field(
        "Untitled Track",
        description="Title of the track (placeholder for now).",
    )
    audio_file: str = Field(
        ...,
        description="Relative path to the final audio file within the release             package (e.g., audio/track.mp3).",
    )
    video_file: str = Field(
        ...,
        description="Relative path to the final video file within the release             package (e.g., video/video.mp4).",
    )
    cover_file: str = Field(
        ...,
        description="Relative path to the cover art file within the release             package (e.g., cover/cover.jpg).",
    )
    track_structure_summary: Optional[str] = Field(
        None,
        description="Textual summary of the track structure (e.g., intro, verse,             chorus). Placeholder for now.",
    )
    visuals_source: Optional[str] = Field(
        None, description="Source of the visuals used (e.g., pexels)."
    )
    llm_summary: Optional[str] = Field(
        None,
        description="Summary of the LLM chain or process used (placeholder).",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the metadata object was created.",
    )


class PromptsUsed(BaseModel):
    """Defines the structure for the prompts used JSON file."""

    generation_run_id: str = Field(
        ..., description="The ID of the batch runner cycle."
    )
    suno_prompt: Optional[str] = Field(
        None, description="The prompt used for Suno track generation."
    )
    suno_style: Optional[str] = Field(
        None, description="The style tag used for Suno track generation."
    )
    video_keywords: Optional[List[str]] = Field(
        None, description="Keywords used for video selection/generation."
    )
    cover_prompt: Optional[str] = Field(
        None, description="Prompt used for cover art generation (placeholder)."
    )
    # Add other relevant prompt fields as needed


# Example Usage (for reference)
# if __name__ == "__main__":
#     example_metadata = ReleaseMetadata(#         release_id="artist_slug_20250430_abc1", #         generation_run_id="f3a4b1c9", #         artist_id=1, #         artist_name="Synthwave Dreamer", #         genre="synthwave", #         release_date="2025-04-30", #         track_title="Neon Dreams", #         audio_file="audio/track.mp3", #         video_file="video/video.mp4", #         cover_file="cover/cover.jpg", #         visuals_source="pexels", #     )
#     print(example_metadata.model_dump_json(indent=4))

#     example_prompts = PromptsUsed(#         generation_run_id="f3a4b1c9", #         suno_prompt="A dreamy synthwave track, upbeat tempo", #         suno_style="synthwave", #         video_keywords=["synthwave", "retro", "neon"] #     )
#     print(example_prompts.model_dump_json(indent=4))
