"""
Schema Converter Module

This module provides functions to convert between different versions
of the artist profile schema, ensuring backward compatibility.
"""

from datetime import datetime, date
from typing import Dict, Any, List
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("schema_converter")

def legacy_to_new_schema(legacy_profile: dict) -> dict:
    """
    Convert a legacy artist profile to the new schema format.
    
    Args:
        legacy_profile: A profile in the legacy format
        
    Returns:
        A profile conforming to the new schema
    """
    logger.info(f"Converting legacy profile '{legacy_profile.get('name', 'Unknown')}' to new schema")
    
    # Extract existing fields
    new_profile = {
        "artist_id": legacy_profile.get("id", f"artist_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
        "stage_name": legacy_profile.get("name", ""),
        "real_name": None,  # Not in legacy schema
        "genre": legacy_profile.get("genre", ""),
        "subgenres": extract_subgenres(legacy_profile),
        "style_description": combine_style_fields(legacy_profile),
        "voice_type": legacy_profile.get("voice", ""),
        "personality_traits": extract_personality_traits(legacy_profile),
        "target_audience": derive_target_audience(legacy_profile),
        "visual_identity_prompt": convert_to_prompt(legacy_profile.get("visual", "")),
        "song_prompt_generator": derive_song_prompt(legacy_profile),
        "video_prompt_generator": derive_video_prompt(legacy_profile),
        "creation_date": parse_date(legacy_profile.get("created_at")),
        "update_history": [],
        "notes": legacy_profile.get("backstory", ""),
        
        # Keep original fields for reference
        "source_prompt": legacy_profile.get("source_prompt", ""),
        "session_id": legacy_profile.get("session_id", ""),
        "metadata": legacy_profile.get("metadata", {})
    }
    
    # Add settings
    new_profile["settings"] = create_settings_from_legacy(legacy_profile)
    
    # Add initial update history entry
    new_profile["update_history"].append({
        "update_date": datetime.now().date(),
        "updated_fields": ["converted_from_legacy_schema"]
    })
    
    return new_profile

def new_to_legacy_schema(new_profile: dict) -> dict:
    """
    Convert a new schema profile to legacy format for backward compatibility.
    
    Args:
        new_profile: A profile in the new schema format
        
    Returns:
        A profile in the legacy format
    """
    logger.info(f"Converting new schema profile '{new_profile.get('stage_name', 'Unknown')}' to legacy format")
    
    legacy_profile = {
        "id": new_profile.get("artist_id", ""),
        "name": new_profile.get("stage_name", ""),
        "genre": new_profile.get("genre", ""),
        "vibe": extract_vibe_from_style(new_profile.get("style_description", "")),
        "backstory": new_profile.get("notes", ""),
        "style": extract_style_from_style(new_profile.get("style_description", "")),
        "visual": new_profile.get("visual_identity_prompt", ""),
        "voice": new_profile.get("voice_type", ""),
        "created_at": format_date(new_profile.get("creation_date")),
        "source_prompt": new_profile.get("source_prompt", ""),
        "session_id": new_profile.get("session_id", ""),
        "metadata": new_profile.get("metadata", {}),
        "version": "2.0",
        "last_updated": datetime.now().isoformat(),
        "status": "active",
        "summary": generate_summary(new_profile),
        "tags": generate_tags(new_profile)
    }
    
    return legacy_profile

def extract_subgenres(legacy_profile: Dict[str, Any]) -> List[str]:
    """
    Extract subgenres from a legacy profile.
    
    Args:
        legacy_profile: A profile in the legacy format
        
    Returns:
        A list of subgenres
    """
    # Start with the main genre as a subgenre
    subgenres = [legacy_profile.get("genre", "")]
    
    # Extract additional genres from tags if available
    if "tags" in legacy_profile and isinstance(legacy_profile["tags"], list):
        genre_keywords = {
            "trap", "electronic", "edm", "hip hop", "hip-hop", "rap", 
            "pop", "rock", "r&b", "jazz", "classical", "country", "metal",
            "techno", "house", "dubstep", "ambient", "folk", "indie"
        }
        
        for tag in legacy_profile["tags"]:
            if tag.lower() in genre_keywords and tag.lower() != subgenres[0].lower():
                subgenres.append(tag.lower())
    
    # If we still only have one subgenre, add a related one based on the main genre
    if len(subgenres) == 1:
        related_genres = {
            "trap": ["hip hop", "electronic"],
            "electronic": ["edm", "techno", "house"],
            "hip hop": ["rap", "trap"],
            "pop": ["electronic", "r&b"],
            "rock": ["indie", "alternative"],
            "r&b": ["soul", "pop"],
            "jazz": ["soul", "blues"],
            "classical": ["orchestral", "piano"],
            "country": ["folk", "acoustic"],
            "metal": ["rock", "hardcore"]
        }
        
        main_genre = subgenres[0].lower()
        if main_genre in related_genres:
            subgenres.append(related_genres[main_genre][0])
    
    # Ensure all subgenres are properly capitalized
    return [s.title() for s in subgenres]

def combine_style_fields(legacy_profile: Dict[str, Any]) -> str:
    """
    Combine style-related fields from a legacy profile.
    
    Args:
        legacy_profile: A profile in the legacy format
        
    Returns:
        A combined style description
    """
    style_parts = []
    
    # Add vibe if available
    if "vibe" in legacy_profile and legacy_profile["vibe"]:
        style_parts.append(f"The artist has a {legacy_profile['vibe']} vibe.")
    
    # Add style if available
    if "style" in legacy_profile and legacy_profile["style"]:
        style_parts.append(legacy_profile["style"])
    
    # If we have no style information, create a basic description
    if not style_parts and "genre" in legacy_profile:
        style_parts.append(f"A {legacy_profile['genre']} artist with a distinctive sound.")
    
    return " ".join(style_parts)

def extract_personality_traits(legacy_profile: Dict[str, Any]) -> List[str]:
    """
    Extract personality traits from a legacy profile.
    
    Args:
        legacy_profile: A profile in the legacy format
        
    Returns:
        A list of personality traits
    """
    traits = []
    
    # Extract from vibe if available
    if "vibe" in legacy_profile and legacy_profile["vibe"]:
        # Split by comma and clean up
        vibe_traits = [t.strip() for t in legacy_profile["vibe"].split(",")]
        traits.extend(vibe_traits)
    
    # Extract from backstory if available
    if "backstory" in legacy_profile and legacy_profile["backstory"]:
        # Look for personality-related keywords
        personality_keywords = [
            "mysterious", "energetic", "melancholic", "aggressive", "chill",
            "futuristic", "nostalgic", "spiritual", "romantic", "rebellious",
            "confident", "shy", "introspective", "extroverted", "creative"
        ]
        
        backstory = legacy_profile["backstory"].lower()
        for keyword in personality_keywords:
            if keyword in backstory and keyword.title() not in traits:
                traits.append(keyword.title())
    
    # If we still don't have traits, derive from genre
    if not traits and "genre" in legacy_profile:
        genre_traits = {
            "trap": ["Mysterious", "Intense"],
            "electronic": ["Energetic", "Innovative"],
            "hip hop": ["Confident", "Authentic"],
            "pop": ["Charismatic", "Approachable"],
            "rock": ["Passionate", "Rebellious"],
            "r&b": ["Sensual", "Emotional"],
            "jazz": ["Sophisticated", "Improvisational"],
            "classical": ["Disciplined", "Refined"],
            "country": ["Authentic", "Relatable"],
            "metal": ["Intense", "Powerful"]
        }
        
        genre = legacy_profile["genre"].lower()
        if genre in genre_traits:
            traits.extend(genre_traits[genre])
    
    # Ensure we have at least one trait
    if not traits:
        traits = ["Creative", "Unique"]
    
    return traits

def derive_target_audience(legacy_profile: Dict[str, Any]) -> str:
    """
    Derive target audience from a legacy profile.
    
    Args:
        legacy_profile: A profile in the legacy format
        
    Returns:
        A target audience description
    """
    # Default audiences by genre
    genre_audiences = {
        "trap": "Young urban listeners who appreciate dark atmospheric beats",
        "electronic": "EDM enthusiasts and festival-goers seeking energetic dance music",
        "hip hop": "Hip-hop fans who value authentic storytelling and strong beats",
        "pop": "Mainstream listeners looking for catchy, accessible music",
        "rock": "Rock fans who appreciate guitar-driven music with attitude",
        "r&b": "Listeners who enjoy smooth, soulful vocals and emotional depth",
        "jazz": "Sophisticated listeners who appreciate musical complexity and improvisation",
        "classical": "Classical music enthusiasts and those seeking emotional orchestral pieces",
        "country": "Country music fans who connect with authentic storytelling and traditional sounds",
        "metal": "Metal enthusiasts seeking intense, powerful music with technical skill"
    }
    
    # Try to get audience from genre
    if "genre" in legacy_profile:
        genre = legacy_profile["genre"].lower()
        if genre in genre_audiences:
            return genre_audiences[genre]
    
    # If no match, create a generic audience
    return "Music fans who appreciate unique and creative artistic expression"

def convert_to_prompt(visual_description: str) -> str:
    """
    Convert a visual description to a prompt format.
    
    Args:
        visual_description: A description of visual appearance
        
    Returns:
        A prompt suitable for image generation
    """
    if not visual_description:
        return "A professional portrait photograph of a music artist with a distinctive style"
    
    # If it already looks like a prompt, return as is
    if len(visual_description) > 20 and ("," in visual_description or "." in visual_description):
        return visual_description
    
    # Otherwise, format as a prompt
    return f"A professional portrait photograph of a music artist: {visual_description}"

def derive_song_prompt(legacy_profile: Dict[str, Any]) -> str:
    """
    Derive a song prompt generator from a legacy profile.
    
    Args:
        legacy_profile: A profile in the legacy format
        
    Returns:
        A song prompt generator template
    """
    genre = legacy_profile.get("genre", "")
    vibe = legacy_profile.get("vibe", "")
    style = legacy_profile.get("style", "")
    
    prompt = f"Create a {genre} track"
    
    if vibe:
        prompt += f" with a {vibe} vibe"
    
    if style:
        # Extract a short phrase from the style description
        style_phrase = re.sub(r'[.!?].*', '', style).strip()
        prompt += f". {style_phrase}"
    
    prompt += f". The track should represent the artist's unique sound and appeal to their target audience."
    
    return prompt

def derive_video_prompt(legacy_profile: Dict[str, Any]) -> str:
    """
    Derive a video prompt generator from a legacy profile.
    
    Args:
        legacy_profile: A profile in the legacy format
        
    Returns:
        A video prompt generator template
    """
    genre = legacy_profile.get("genre", "")
    visual = legacy_profile.get("visual", "")
    vibe = legacy_profile.get("vibe", "")
    
    prompt = f"Create a music video teaser for a {genre} track"
    
    if vibe:
        prompt += f" with a {vibe} atmosphere"
    
    if visual:
        # Extract a short phrase from the visual description
        visual_phrase = re.sub(r'[.!?].*', '', visual).strip()
        prompt += f". Visual style: {visual_phrase}"
    
    prompt += f". The video should capture the essence of the artist's identity and complement their music."
    
    return prompt

def parse_date(date_str: str) -> date:
    """
    Parse a date string to a date object.
    
    Args:
        date_str: A date string in ISO format
        
    Returns:
        A date object
    """
    if not date_str:
        return datetime.now().date()
    
    try:
        return datetime.fromisoformat(date_str).date()
    except (ValueError, TypeError):
        # If parsing fails, return current date
        return datetime.now().date()

def format_date(date_obj: Any) -> str:
    """
    Format a date object as an ISO string.
    
    Args:
        date_obj: A date or datetime object
        
    Returns:
        An ISO format date string
    """
    if isinstance(date_obj, datetime):
        return date_obj.isoformat()
    elif isinstance(date_obj, date):
        return datetime.combine(date_obj, datetime.min.time()).isoformat()
    else:
        return datetime.now().isoformat()

def extract_vibe_from_style(style_description: str) -> str:
    """
    Extract vibe information from a style description.
    
    Args:
        style_description: A style description from the new schema
        
    Returns:
        A vibe string for the legacy format
    """
    # Look for vibe statement
    vibe_match = re.search(r'has a ([^.]+) vibe', style_description, re.IGNORECASE)
    if vibe_match:
        return vibe_match.group(1)
    
    # Extract adjectives that might describe vibe
    vibe_keywords = [
        "mysterious", "energetic", "melancholic", "aggressive", "chill",
        "futuristic", "nostalgic", "spiritual", "romantic", "rebellious",
        "dark", "light", "intense", "calm", "chaotic", "harmonious"
    ]
    
    found_vibes = []
    for keyword in vibe_keywords:
        if keyword in style_description.lower():
            found_vibes.append(keyword.title())
    
    if found_vibes:
        return ", ".join(found_vibes[:3])  # Limit to top 3
    
    # Default vibe
    return "Unique, Distinctive"

def extract_style_from_style(style_description: str) -> str:
    """
    Extract style information from a style description.
    
    Args:
        style_description: A style description from the new schema
        
    Returns:
        A style string for the legacy format
    """
    # Remove vibe statement if present
    style = re.sub(r'The artist has a [^.]+\. ', '', style_description)
    
    # If nothing left, return the original
    if not style:
        return style_description
    
    return style

def generate_summary(new_profile: Dict[str, Any]) -> str:
    """
    Generate a summary from a new schema profile.
    
    Args:
        new_profile: A profile in the new schema format
        
    Returns:
        A summary string for the legacy format
    """
    stage_name = new_profile.get("stage_name", "")
    genre = new_profile.get("genre", "")
    
    # Extract personality traits for vibe
    traits = new_profile.get("personality_traits", [])
    vibe = ", ".join(traits[:2]) if traits else "unique"
    
    return f"{stage_name} is a {genre} artist with a {vibe} vibe."

def generate_tags(new_profile: Dict[str, Any]) -> List[str]:
    """
    Generate tags from a new schema profile.
    
    Args:
        new_profile: A profile in the new schema format
        
    Returns:
        A list of tags for the legacy format
    """
    tags = []
    
    # Add genre and subgenres
    if "genre" in new_profile:
        tags.append(new_profile["genre"].lower())
    
    if "subgenres" in new_profile:
        tags.extend([s.lower() for s in new_profile["subgenres"]])
    
    # Add personality traits
    if "personality_traits" in new_profile:
        tags.extend([t.lower() for t in new_profile["personality_traits"]])
    
    # Add artist name
    if "stage_name" in new_profile:
        tags.append(new_profile["stage_name"].lower().replace(" ", ""))
    
    # Remove duplicates
    return list(set(tags))

def create_settings_from_legacy(legacy_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create settings object from a legacy profile.
    
    Args:
        legacy_profile: A profile in the legacy format
        
    Returns:
        A settings object for the new schema
    """
    # Default settings
    settings = {
        "release_strategy": {
            "track_release_random_days": [3, 15],
            "video_release_ratio": 0.7
        },
        "llm_assignments": {
            "artist_prompt_llm": "gpt-4",
            "song_prompt_llm": "gpt-4",
            "video_prompt_llm": "gpt-4",
            "final_validator_llm": "gpt-4"
        },
        "training_data_version": "1.0",
        "trend_alignment_behavior": "soft",
        "behavior_evolution_settings": {
            "allow_minor_genre_shifts": True,
            "allow_personality_shifts": True,
            "safe_mode": True
        }
    }
    
    # Try to extract settings from metadata if available
    if "metadata" in legacy_profile and isinstance(legacy_profile["metadata"], dict):
        metadata = legacy_profile["metadata"]
        
        # Extract release strategy if available
        if "release_strategy" in metadata:
            release_strategy = metadata["release_strategy"]
            if isinstance(release_strategy, dict):
                if "track_release_days" in release_strategy:
                    days = release_strategy["track_release_days"]
                    if isinstance(days, list) and len(days) == 2:
                        settings["release_strategy"]["track_release_random_days"] = days
                
                if "video_ratio" in release_strategy:
                    ratio = release_strategy["video_ratio"]
                    if isinstance(ratio, (int, float)) and 0 <= ratio <= 1:
                        settings["release_strategy"]["video_release_ratio"] = ratio
        
        # Extract LLM assignments if available
        if "llm_models" in metadata:
            llm_models = metadata["llm_models"]
            if isinstance(llm_models, dict):
                if "artist" in llm_models:
                    settings["llm_assignments"]["artist_prompt_llm"] = llm_models["artist"]
                if "song" in llm_models:
                    settings["llm_assignments"]["song_prompt_llm"] = llm_models["song"]
                if "video" in llm_models:
                    settings["llm_assignments"]["video_prompt_llm"] = llm_models["video"]
                if "validator" in llm_models:
                    settings["llm_assignments"]["final_validator_llm"] = llm_models["validator"]
        
        # Extract trend alignment if available
        if "trend_alignment" in metadata:
            alignment = metadata["trend_alignment"]
            if alignment in ["strict", "soft", "experimental"]:
                settings["trend_alignment_behavior"] = alignment
        
        # Extract evolution settings if available
        if "evolution" in metadata:
            evolution = metadata["evolution"]
            if isinstance(evolution, dict):
                if "genre_shifts" in evolution:
                    settings["behavior_evolution_settings"]["allow_minor_genre_shifts"] = bool(evolution["genre_shifts"])
                if "personality_shifts" in evolution:
                    settings["behavior_evolution_settings"]["allow_personality_shifts"] = bool(evolution["personality_shifts"])
                if "safe_mode" in evolution:
                    settings["behavior_evolution_settings"]["safe_mode"] = bool(evolution["safe_mode"])
    
    return settings
