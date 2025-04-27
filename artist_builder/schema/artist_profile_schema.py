"""
Artist Profile Schema Definition for Database Integration

This module defines the schema for artist profiles using Pydantic models,
providing validation, serialization, and database integration capabilities.
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime
import logging
import uuid
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_profile_schema")


class UpdateHistoryItem(BaseModel):
    """Record of changes made to an artist profile."""

    update_date: date
    updated_fields: List[str]
    update_reason: Optional[str] = None
    update_source: Optional[str] = None

    class Config:
        orm_mode = True


class TrendAlignmentBehavior(str, Enum):
    """Enum for trend alignment behavior options."""
    STRICT = "strict"
    SOFT = "soft"
    EXPERIMENTAL = "experimental"


class BehaviorEvolutionSettings(BaseModel):
    """Settings that control how an artist profile can evolve over time."""

    allow_minor_genre_shifts: bool = True
    allow_personality_shifts: bool = True
    safe_mode: bool = True
    evolution_speed: str = Field(
        default="medium", 
        description="How quickly the artist evolves: 'slow', 'medium', or 'fast'"
    )
    preserve_core_identity: bool = Field(
        default=True,
        description="Whether to maintain core identity elements during evolution"
    )

    @validator("evolution_speed")
    def validate_evolution_speed(cls, v):
        """Validate that evolution speed is one of the allowed values."""
        allowed_values = ["slow", "medium", "fast"]
        if v not in allowed_values:
            raise ValueError(
                f"evolution_speed must be one of: {', '.join(allowed_values)}"
            )
        return v

    class Config:
        orm_mode = True


class LLMAssignments(BaseModel):
    """Assignment of LLM models to different generation tasks."""

    artist_prompt_llm: str
    song_prompt_llm: str
    video_prompt_llm: str
    final_validator_llm: str

    class Config:
        orm_mode = True


class ReleaseStrategy(BaseModel):
    """Strategy for releasing tracks and videos."""

    track_release_random_days: List[int] = Field(
        default=[3, 15], description="Min and max days between track releases"
    )
    video_release_ratio: float = Field(
        default=0.7, description="Probability of creating a video for a track"
    )
    content_plan_length_days: int = Field(
        default=90, description="Length of content plan in days"
    )
    social_media_post_frequency: int = Field(
        default=3, description="Number of social media posts per week"
    )

    @validator("track_release_random_days")
    def validate_release_days(cls, v):
        """Validate that release days are properly formatted."""
        if len(v) != 2:
            raise ValueError(
                "track_release_random_days must be a list of exactly 2 integers [min, max]"
            )
        if v[0] > v[1]:
            raise ValueError("Min days must be less than or equal to max days")
        return v

    @validator("video_release_ratio")
    def validate_release_ratio(cls, v):
        """Validate that release ratio is between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError("video_release_ratio must be between 0 and 1")
        return v

    class Config:
        orm_mode = True


class SocialMediaPresence(BaseModel):
    """Social media presence configuration for the artist."""
    
    platforms: List[str] = Field(
        default=["instagram", "tiktok", "twitter"],
        description="Social media platforms where the artist is present"
    )
    posting_style: str = Field(
        default="casual",
        description="Style of social media posts: 'casual', 'professional', or 'mysterious'"
    )
    engagement_strategy: str = Field(
        default="moderate",
        description="How actively the artist engages: 'passive', 'moderate', or 'active'"
    )
    
    @validator("posting_style")
    def validate_posting_style(cls, v):
        """Validate that posting style is one of the allowed values."""
        allowed_values = ["casual", "professional", "mysterious"]
        if v not in allowed_values:
            raise ValueError(
                f"posting_style must be one of: {', '.join(allowed_values)}"
            )
        return v
        
    @validator("engagement_strategy")
    def validate_engagement_strategy(cls, v):
        """Validate that engagement strategy is one of the allowed values."""
        allowed_values = ["passive", "moderate", "active"]
        if v not in allowed_values:
            raise ValueError(
                f"engagement_strategy must be one of: {', '.join(allowed_values)}"
            )
        return v
    
    class Config:
        orm_mode = True


class ArtistProfileSettings(BaseModel):
    """Settings that control artist behavior and content generation."""

    release_strategy: ReleaseStrategy
    llm_assignments: LLMAssignments
    training_data_version: str
    trend_alignment_behavior: TrendAlignmentBehavior = Field(
        default=TrendAlignmentBehavior.SOFT,
        description="How closely to follow trends: 'strict', 'soft', or 'experimental'",
    )
    behavior_evolution_settings: BehaviorEvolutionSettings = Field(
        default_factory=BehaviorEvolutionSettings
    )
    social_media_presence: SocialMediaPresence = Field(
        default_factory=SocialMediaPresence
    )
    performance_metrics_tracking: bool = Field(
        default=True,
        description="Whether to track performance metrics for this artist"
    )

    class Config:
        orm_mode = True


class ArtistProfile(BaseModel):
    """
    Complete artist profile schema for the AI Artist Creation and Management System.

    This schema defines all required and optional fields for artist profiles,
    ensuring consistency and completeness across the system.
    """

    artist_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
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
    creation_date: Union[date, datetime] = Field(default_factory=datetime.now)
    update_history: List[UpdateHistoryItem] = []
    notes: Optional[str] = None
    settings: ArtistProfileSettings
    backstory: str = Field(
        default="",
        description="The artist's fictional backstory and history"
    )
    influences: List[str] = Field(
        default=[],
        description="Artists or genres that influence this artist's style"
    )
    
    # Database integration fields
    is_active: bool = Field(
        default=True,
        description="Whether the artist is currently active"
    )
    last_content_date: Optional[date] = None
    performance_rating: Optional[float] = None
    
    # Content planning fields
    current_content_plan_id: Optional[str] = None
    content_plan_end_date: Optional[date] = None
    
    # Additional fields for backward compatibility
    source_prompt: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

    @validator("creation_date", pre=True)
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

    @validator("artist_id")
    def validate_artist_id(cls, v):
        """Ensure artist_id is not empty."""
        if not v:
            raise ValueError("artist_id cannot be empty")
        return v

    @validator("stage_name")
    def validate_stage_name(cls, v):
        """Ensure stage_name is not empty."""
        if not v:
            raise ValueError("stage_name cannot be empty")
        return v

    @validator("subgenres")
    def validate_subgenres(cls, v):
        """Ensure at least one subgenre is provided."""
        if not v:
            raise ValueError("At least one subgenre must be provided")
        return v

    @validator("personality_traits")
    def validate_personality_traits(cls, v):
        """Ensure at least one personality trait is provided."""
        if not v:
            raise ValueError("At least one personality trait must be provided")
        return v
        
    @root_validator
    def check_content_plan_consistency(cls, values):
        """Ensure content plan fields are consistent."""
        has_plan_id = values.get("current_content_plan_id") is not None
        has_end_date = values.get("content_plan_end_date") is not None
        
        if has_plan_id != has_end_date:
            raise ValueError("Both current_content_plan_id and content_plan_end_date must be provided together")
            
        return values

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "artist_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "stage_name": "Neon Horizon",
                "real_name": "AI Generated Artist",
                "genre": "Electronic",
                "subgenres": ["Synthwave", "Chillwave"],
                "style_description": "Retro-futuristic electronic music with nostalgic 80s influences and modern production techniques",
                "voice_type": "Ethereal female vocals with occasional vocoder effects",
                "personality_traits": ["Mysterious", "Introspective", "Futuristic"],
                "target_audience": "25-35 year old electronic music fans with nostalgia for 80s aesthetics",
                "visual_identity_prompt": "Neon cityscape at night with purple and blue color palette, retro-futuristic aesthetic",
                "song_prompt_generator": "electronic_synthwave_template_v2",
                "video_prompt_generator": "retro_futuristic_video_template",
                "creation_date": "2025-04-15",
                "backstory": "Neon Horizon emerged from the digital underground in 2025, quickly gaining recognition for blending nostalgic synthwave elements with cutting-edge production techniques.",
                "influences": ["Kavinsky", "The Midnight", "Gunship"]
            }
        }


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
        if hasattr(e, "errors"):
            for error in e.errors():
                loc = ".".join(str(l) for l in error["loc"])
                errors.append(f"{loc}: {error['msg']}")
        else:
            errors.append(str(e))
        return False, errors


def create_database_model(profile: ArtistProfile) -> dict:
    """
    Convert a Pydantic ArtistProfile model to a format suitable for database storage.
    
    Args:
        profile: The validated artist profile
        
    Returns:
        dict: The profile in a format ready for database insertion
    """
    # Convert to dict with orm_mode enabled
    db_model = profile.dict(by_alias=True)
    
    # Ensure nested models are also converted properly
    db_model["settings"] = profile.settings.dict()
    db_model["settings"]["release_strategy"] = profile.settings.release_strategy.dict()
    db_model["settings"]["llm_assignments"] = profile.settings.llm_assignments.dict()
    db_model["settings"]["behavior_evolution_settings"] = profile.settings.behavior_evolution_settings.dict()
    db_model["settings"]["social_media_presence"] = profile.settings.social_media_presence.dict()
    
    # Convert update history items
    db_model["update_history"] = [item.dict() for item in profile.update_history]
    
    return db_model


def update_artist_profile(profile: ArtistProfile, updates: dict) -> ArtistProfile:
    """
    Update an artist profile with new values and record the update in history.
    
    Args:
        profile: The existing artist profile
        updates: Dictionary of fields to update
        
    Returns:
        ArtistProfile: The updated profile
    """
    # Track which fields are being updated
    updated_fields = list(updates.keys())
    
    # Create update history item
    update_item = UpdateHistoryItem(
        update_date=datetime.now().date(),
        updated_fields=updated_fields,
        update_reason=updates.pop("update_reason", None),
        update_source=updates.pop("update_source", None)
    )
    
    # Add to update history
    profile_dict = profile.dict()
    profile_dict["update_history"] = profile_dict.get("update_history", []) + [update_item.dict()]
    
    # Apply updates
    for key, value in updates.items():
        if "." in key:
            # Handle nested fields (e.g., "settings.release_strategy.video_release_ratio")
            parts = key.split(".")
            current = profile_dict
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            # Handle top-level fields
            profile_dict[key] = value
    
    # Create new profile with updates
    return ArtistProfile(**profile_dict)
