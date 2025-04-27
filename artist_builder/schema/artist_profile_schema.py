"""
Artist Profile Schema Definition

This module defines the schema for artist profiles using Pydantic models,
providing validation, serialization, and documentation capabilities.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("artist_profile_schema")

class UpdateHistoryItem(BaseModel):
    """Record of changes made to an artist profile."""
    update_date: date
    updated_fields: List[str]

class BehaviorEvolutionSettings(BaseModel):
    """Settings that control how an artist profile can evolve over time."""
    allow_minor_genre_shifts: bool = True
    allow_personality_shifts: bool = True
    safe_mode: bool = True

class LLMAssignments(BaseModel):
    """Assignment of LLM models to different generation tasks."""
    artist_prompt_llm: str
    song_prompt_llm: str
    video_prompt_llm: str
    final_validator_llm: str

class ReleaseStrategy(BaseModel):
    """Strategy for releasing tracks and videos."""
    track_release_random_days: List[int] = Field(
        default=[3, 15],
        description="Min and max days between track releases"
    )
    video_release_ratio: float = Field(
        default=0.7,
        description="Probability of creating a video for a track"
    )
    
    @validator('track_release_random_days')
    def validate_release_days(cls, v):
        """Validate that release days are properly formatted."""
        if len(v) != 2:
            raise ValueError("track_release_random_days must be a list of exactly 2 integers [min, max]")
        if v[0] > v[1]:
            raise ValueError("Min days must be less than or equal to max days")
        return v
    
    @validator('video_release_ratio')
    def validate_release_ratio(cls, v):
        """Validate that release ratio is between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError("video_release_ratio must be between 0 and 1")
        return v

class ArtistProfileSettings(BaseModel):
    """Settings that control artist behavior and content generation."""
    release_strategy: ReleaseStrategy
    llm_assignments: LLMAssignments
    training_data_version: str
    trend_alignment_behavior: str = Field(
        default="soft",
        description="How closely to follow trends: 'strict', 'soft', or 'experimental'"
    )
    behavior_evolution_settings: BehaviorEvolutionSettings = Field(
        default_factory=BehaviorEvolutionSettings
    )
    
    @validator('trend_alignment_behavior')
    def validate_trend_alignment(cls, v):
        """Validate that trend alignment is one of the allowed values."""
        allowed_values = ["strict", "soft", "experimental"]
        if v not in allowed_values:
            raise ValueError(f"trend_alignment_behavior must be one of: {', '.join(allowed_values)}")
        return v

class ArtistProfile(BaseModel):
    """
    Complete artist profile schema for the AI Artist Creation and Management System.
    
    This schema defines all required and optional fields for artist profiles,
    ensuring consistency and completeness across the system.
    """
    artist_id: str
    stage_name: str
    real_name: Optional[str] = None
    genre: str
    subgenres: List[str]
    style_description: str
    voice_type: str
    personality_traits: List[str]
    target_audience: str
    visual_identity_prompt: str
    song_prompt_generator: str
    video_prompt_generator: str
    creation_date: Union[date, datetime]
    update_history: List[UpdateHistoryItem] = []
    notes: Optional[str] = None
    settings: ArtistProfileSettings
    
    # Additional fields for backward compatibility
    source_prompt: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    @validator('creation_date', pre=True)
    def parse_creation_date(cls, v):
        """Convert string dates to date objects if needed."""
        if isinstance(v, str):
            try:
                # Try parsing as ISO format datetime
                return datetime.fromisoformat(v).date()
            except ValueError:
                # Try parsing as YYYY-MM-DD
                return datetime.strptime(v, "%Y-%m-%d").date()
        return v
    
    @validator('artist_id')
    def validate_artist_id(cls, v):
        """Ensure artist_id is not empty."""
        if not v:
            raise ValueError("artist_id cannot be empty")
        return v
    
    @validator('stage_name')
    def validate_stage_name(cls, v):
        """Ensure stage_name is not empty."""
        if not v:
            raise ValueError("stage_name cannot be empty")
        return v
    
    @validator('subgenres')
    def validate_subgenres(cls, v):
        """Ensure at least one subgenre is provided."""
        if not v:
            raise ValueError("At least one subgenre must be provided")
        return v
    
    @validator('personality_traits')
    def validate_personality_traits(cls, v):
        """Ensure at least one personality trait is provided."""
        if not v:
            raise ValueError("At least one personality trait must be provided")
        return v

def validate_artist_profile(profile_data: dict) -> tuple[bool, list[str]]:
    """
    Validate an artist profile against the schema.
    
    Args:
        profile_data: The artist profile data to validate
        
    Returns:
        tuple: (is_valid, error_messages)
    """
    try:
        # Use Pydantic validation
        ArtistProfile(**profile_data)
        return True, []
    except Exception as e:
        # Extract validation errors
        errors = []
        if hasattr(e, 'errors'):
            for error in e.errors():
                loc = '.'.join(str(l) for l in error['loc'])
                errors.append(f"{loc}: {error['msg']}")
        else:
            errors.append(str(e))
        return False, errors
