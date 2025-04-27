"""
Profile Validation Module for Artist Profile Builder

This module ensures that generated artist profiles comply with the schema,
identifies and corrects minor issues, and generates helpful error messages.
"""

import logging
import json
import os
import sys
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path

# Add parent directory to path to import from sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import schema validation from schema module
from schema.artist_profile_schema import (
    ArtistProfile, 
    validate_artist_profile,
    TrendAlignmentBehavior,
    BehaviorEvolutionSettings,
    LLMAssignments,
    ReleaseStrategy,
    SocialMediaPresence,
    ArtistProfileSettings
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.profile_validator")


class ProfileValidationError(Exception):
    """Exception raised for errors in the profile validation."""
    pass


class ProfileValidator:
    """
    Validates artist profiles against the schema and provides correction capabilities.
    """

    def __init__(self):
        """Initialize the profile validator."""
        logger.info("Initialized ProfileValidator")

    def validate_profile(self, profile_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate an artist profile against the schema.
        
        Args:
            profile_data: Dictionary containing the profile data
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        logger.info("Validating artist profile against schema")
        
        # Use schema validation function
        is_valid, errors = validate_artist_profile(profile_data)
        
        if is_valid:
            logger.info("Profile validation successful")
        else:
            logger.warning(f"Profile validation failed with {len(errors)} errors")
            for error in errors:
                logger.warning(f"Validation error: {error}")
        
        return is_valid, errors

    def auto_correct_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to automatically correct minor issues in the profile.
        
        Args:
            profile_data: Dictionary containing the profile data
            
        Returns:
            Corrected profile data
        """
        logger.info("Attempting to auto-correct profile issues")
        
        corrected = profile_data.copy()
        corrections_made = []
        
        # Ensure required fields exist
        self._ensure_required_fields(corrected, corrections_made)
        
        # Ensure list fields are lists
        self._ensure_list_fields(corrected, corrections_made)
        
        # Ensure settings structure is correct
        self._ensure_settings_structure(corrected, corrections_made)
        
        # Ensure enum values are valid
        self._ensure_valid_enum_values(corrected, corrections_made)
        
        # Log corrections
        if corrections_made:
            logger.info(f"Made {len(corrections_made)} auto-corrections to profile")
            for correction in corrections_made:
                logger.info(f"Auto-correction: {correction}")
        else:
            logger.info("No auto-corrections needed")
        
        return corrected

    def _ensure_required_fields(self, profile: Dict[str, Any], corrections: List[str]) -> None:
        """
        Ensure all required fields exist in the profile.
        
        Args:
            profile: Dictionary containing the profile data
            corrections: List to append correction messages to
        """
        # Check for artist_id
        if "artist_id" not in profile or not profile["artist_id"]:
            import uuid
            profile["artist_id"] = str(uuid.uuid4())
            corrections.append("Added missing artist_id with new UUID")
        
        # Check for creation_date
        if "creation_date" not in profile or not profile["creation_date"]:
            from datetime import datetime
            profile["creation_date"] = datetime.now().isoformat()
            corrections.append("Added missing creation_date with current date")
        
        # Check for update_history
        if "update_history" not in profile:
            profile["update_history"] = []
            corrections.append("Added missing update_history as empty list")
        
        # Check for metadata
        if "metadata" not in profile:
            profile["metadata"] = {}
            corrections.append("Added missing metadata as empty dict")

    def _ensure_list_fields(self, profile: Dict[str, Any], corrections: List[str]) -> None:
        """
        Ensure fields that should be lists are actually lists.
        
        Args:
            profile: Dictionary containing the profile data
            corrections: List to append correction messages to
        """
        list_fields = ["subgenres", "personality_traits", "influences", "update_history"]
        
        for field in list_fields:
            if field in profile:
                # Convert string to list if needed
                if isinstance(profile[field], str):
                    profile[field] = [item.strip() for item in profile[field].split(",")]
                    corrections.append(f"Converted {field} from string to list")
                # Ensure it's a list
                elif not isinstance(profile[field], list):
                    profile[field] = [str(profile[field])]
                    corrections.append(f"Converted {field} to list")

    def _ensure_settings_structure(self, profile: Dict[str, Any], corrections: List[str]) -> None:
        """
        Ensure the settings structure is correct.
        
        Args:
            profile: Dictionary containing the profile data
            corrections: List to append correction messages to
        """
        # Check if settings exists
        if "settings" not in profile:
            # Create default settings
            profile["settings"] = {
                "release_strategy": {
                    "track_release_random_days": [3, 15],
                    "video_release_ratio": 0.7,
                    "content_plan_length_days": 90,
                    "social_media_post_frequency": 3
                },
                "llm_assignments": {
                    "artist_prompt_llm": "gpt-4",
                    "song_prompt_llm": "gpt-4",
                    "video_prompt_llm": "gpt-4",
                    "final_validator_llm": "gpt-4"
                },
                "training_data_version": "v1.0",
                "trend_alignment_behavior": "soft",
                "behavior_evolution_settings": {
                    "allow_minor_genre_shifts": True,
                    "allow_personality_shifts": True,
                    "safe_mode": True,
                    "evolution_speed": "medium",
                    "preserve_core_identity": True
                },
                "social_media_presence": {
                    "platforms": ["instagram", "tiktok", "twitter"],
                    "posting_style": "casual",
                    "engagement_strategy": "moderate"
                },
                "performance_metrics_tracking": True
            }
            corrections.append("Added default settings structure")
            return
        
        # Check release_strategy
        if "release_strategy" not in profile["settings"]:
            profile["settings"]["release_strategy"] = {
                "track_release_random_days": [3, 15],
                "video_release_ratio": 0.7,
                "content_plan_length_days": 90,
                "social_media_post_frequency": 3
            }
            corrections.append("Added default release_strategy to settings")
        
        # Check llm_assignments
        if "llm_assignments" not in profile["settings"]:
            profile["settings"]["llm_assignments"] = {
                "artist_prompt_llm": "gpt-4",
                "song_prompt_llm": "gpt-4",
                "video_prompt_llm": "gpt-4",
                "final_validator_llm": "gpt-4"
            }
            corrections.append("Added default llm_assignments to settings")
        
        # Check training_data_version
        if "training_data_version" not in profile["settings"]:
            profile["settings"]["training_data_version"] = "v1.0"
            corrections.append("Added default training_data_version to settings")
        
        # Check trend_alignment_behavior
        if "trend_alignment_behavior" not in profile["settings"]:
            profile["settings"]["trend_alignment_behavior"] = "soft"
            corrections.append("Added default trend_alignment_behavior to settings")
        
        # Check behavior_evolution_settings
        if "behavior_evolution_settings" not in profile["settings"]:
            profile["settings"]["behavior_evolution_settings"] = {
                "allow_minor_genre_shifts": True,
                "allow_personality_shifts": True,
                "safe_mode": True,
                "evolution_speed": "medium",
                "preserve_core_identity": True
            }
            corrections.append("Added default behavior_evolution_settings to settings")
        
        # Check social_media_presence
        if "social_media_presence" not in profile["settings"]:
            profile["settings"]["social_media_presence"] = {
                "platforms": ["instagram", "tiktok", "twitter"],
                "posting_style": "casual",
                "engagement_strategy": "moderate"
            }
            corrections.append("Added default social_media_presence to settings")
        
        # Check performance_metrics_tracking
        if "performance_metrics_tracking" not in profile["settings"]:
            profile["settings"]["performance_metrics_tracking"] = True
            corrections.append("Added default performance_metrics_tracking to settings")

    def _ensure_valid_enum_values(self, profile: Dict[str, Any], corrections: List[str]) -> None:
        """
        Ensure enum values are valid.
        
        Args:
            profile: Dictionary containing the profile data
            corrections: List to append correction messages to
        """
        # Check trend_alignment_behavior
        if "settings" in profile and "trend_alignment_behavior" in profile["settings"]:
            valid_values = ["strict", "soft", "experimental"]
            current_value = profile["settings"]["trend_alignment_behavior"]
            
            if isinstance(current_value, str) and current_value.lower() not in valid_values:
                profile["settings"]["trend_alignment_behavior"] = "soft"
                corrections.append(f"Corrected invalid trend_alignment_behavior '{current_value}' to 'soft'")
        
        # Check evolution_speed
        if ("settings" in profile and "behavior_evolution_settings" in profile["settings"] and 
            "evolution_speed" in profile["settings"]["behavior_evolution_settings"]):
            valid_values = ["slow", "medium", "fast"]
            current_value = profile["settings"]["behavior_evolution_settings"]["evolution_speed"]
            
            if isinstance(current_value, str) and current_value.lower() not in valid_values:
                profile["settings"]["behavior_evolution_settings"]["evolution_speed"] = "medium"
                corrections.append(f"Corrected invalid evolution_speed '{current_value}' to 'medium'")
        
        # Check posting_style
        if ("settings" in profile and "social_media_presence" in profile["settings"] and 
            "posting_style" in profile["settings"]["social_media_presence"]):
            valid_values = ["casual", "professional", "mysterious"]
            current_value = profile["settings"]["social_media_presence"]["posting_style"]
            
            if isinstance(current_value, str) and current_value.lower() not in valid_values:
                profile["settings"]["social_media_presence"]["posting_style"] = "casual"
                corrections.append(f"Corrected invalid posting_style '{current_value}' to 'casual'")
        
        # Check engagement_strategy
        if ("settings" in profile and "social_media_presence" in profile["settings"] and 
            "engagement_strategy" in profile["settings"]["social_media_presence"]):
            valid_values = ["passive", "moderate", "active"]
            current_value = profile["settings"]["social_media_presence"]["engagement_strategy"]
            
            if isinstance(current_value, str) and current_value.lower() not in valid_values:
                profile["settings"]["social_media_presence"]["engagement_strategy"] = "moderate"
                corrections.append(f"Corrected invalid engagement_strategy '{current_value}' to 'moderate'")

    def ensure_field_consistency(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure logical consistency between fields in the profile.
        
        Args:
            profile_data: Dictionary containing the profile data
            
        Returns:
            Profile data with consistent fields
        """
        logger.info("Ensuring field consistency in profile")
        
        profile = profile_data.copy()
        consistency_fixes = []
        
        # Ensure stage_name and real_name consistency
        if "stage_name" in profile and "real_name" in profile:
            if not profile["real_name"]:
                profile["real_name"] = f"AI Generated Artist ({profile['stage_name']})"
                consistency_fixes.append("Set default real_name based on stage_name")
        
        # Ensure song_prompt_generator and video_prompt_generator consistency with genre
        if "genre" in profile:
            genre_lower = profile["genre"].lower()
            
            if "song_prompt_generator" not in profile or not profile["song_prompt_generator"]:
                profile["song_prompt_generator"] = f"{genre_lower}_song_template"
                consistency_fixes.append(f"Set song_prompt_generator to '{profile['song_prompt_generator']}' based on genre")
            
            if "video_prompt_generator" not in profile or not profile["video_prompt_generator"]:
                profile["video_prompt_generator"] = f"{genre_lower}_video_template"
                consistency_fixes.append(f"Set video_prompt_generator to '{profile['video_prompt_generator']}' based on genre")
        
        # Log consistency fixes
        if consistency_fixes:
            logger.info(f"Made {len(consistency_fixes)} consistency fixes to profile")
            for fix in consistency_fixes:
                logger.info(f"Consistency fix: {fix}")
        else:
            logger.info("No consistency fixes needed")
        
        return profile

    def generate_validation_report(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a detailed validation report for the profile.
        
        Args:
            profile_data: Dictionary containing the profile data
            
        Returns:
            Dictionary containing the validation report
        """
        logger.info("Generating validation report")
        
        # Validate the profile
        is_valid, errors = self.validate_profile(profile_data)
        
        # Create the report
        report = {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": [],
            "suggestions": [],
            "timestamp": None
        }
        
        # Add timestamp
        from datetime import datetime
        report["timestamp"] = datetime.now().isoformat()
        
        # Check for warnings (issues that don't invalidate the profile)
        self._check_for_warnings(profile_data, report["warnings"])
        
        # Generate suggestions for improvement
        self._generate_suggestions(profile_data, report["suggestions"])
        
        logger.info(f"Validation report generated: valid={is_valid}, errors={len(errors)}, warnings={len(report['warnings'])}, suggestions={len(report['suggestions'])}")
        
        return report

    def _check_for_warnings(self, profile: Dict[str, Any], warnings: List[str]) -> None:
        """
        Check for warning conditions in the profile.
        
        Args:
            profile: Dictionary containing the profile data
            warnings: List to append warning messages to
        """
        # Check for short descriptions
        if "style_description" in profile and len(profile["style_description"]) < 50:
            warnings.append("Style description is quite short, consider expanding it")
        
        if "backstory" in profile and len(profile["backstory"]) < 100:
            warnings.append("Backstory is quite short, consider expanding it")
        
        # Check for minimal personality traits
        if "personality_traits" in profile and isinstance(profile["personality_traits"], list):
            if len(profile["personality_traits"]) < 3:
                warnings.append("Few personality traits defined, consider adding more for a richer character")
        
        # Check for missing optional fields
        optional_fields = ["influences", "backstory"]
        for field in optional_fields:
            if field not in profile or not profile[field]:
                warnings.append(f"Optional field '{field}' is missing or empty")

    def _generate_suggestions(self, profile: Dict[str, Any], suggestions: List[str]) -> None:
        """
        Generate suggestions for improving the profile.
        
        Args:
            profile: Dictionary containing the profile data
            suggestions: List to append suggestion messages to
        """
        # Suggest expanding influences
        if "influences" in profile and isinstance(profile["influences"], list):
            if len(profile["influences"]) < 3:
                suggestions.append("Consider adding more musical influences for a richer artistic background")
        
        # Suggest more detailed target audience
        if "target_audience" in profile and len(profile["target_audience"]) < 50:
            suggestions.append("Consider providing a more detailed description of the target audience")
        
        # Suggest more detailed visual identity
        if "visual_identity_prompt" in profile and len(profile["visual_identity_prompt"]) < 50:
            suggestions.append("Consider providing a more detailed visual identity prompt")

    def validate_and_correct_profile(self, profile_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Validate a profile and attempt to correct any issues.
        
        Args:
            profile_data: Dictionary containing the profile data
            
        Returns:
            Tuple of (corrected_profile, validation_report)
        """
        logger.info("Validating and correcting profile")
        
        # First, try to auto-correct any issues
        corrected_profile = self.auto_correct_profile(profile_data)
        
        # Then, ensure field consistency
        consistent_profile = self.ensure_field_consistency(corrected_profile)
        
        # Generate validation report for the corrected profile
        validation_report = self.generate_validation_report(consistent_profile)
        
        # If still not valid, log the remaining issues
        if not validation_report["is_valid"]:
            logger.warning("Profile still has validation issues after correction attempts")
            for error in validation_report["errors"]:
                logger.warning(f"Remaining error: {error}")
        else:
            logger.info("Profile successfully validated and corrected")
        
        return consistent_profile, validation_report


def main():
    """Main function for testing the profile validator."""
    # Example profile data with some issues
    profile_data = {
        "stage_name": "Neon Horizon",
        "genre": "Electronic",
        "subgenres": "Synthwave, Chillwave",  # Should be a list
        "style_description": "Retro-futuristic electronic music",  # Too short
        "voice_type": "Ethereal female vocals with vocoder effects",
        "personality_traits": ["Mysterious", "Introspective"],  # Too few traits
        "target_audience": "25-35 year old electronic music fans",
        "visual_identity_prompt": "Neon cityscape at night",  # Too short
        "song_prompt_generator": "electronic_template",
        "video_prompt_generator": "retro_video_template",
        # Missing settings
    }
    
    try:
        # Initialize validator
        validator = ProfileValidator()
        
        # Validate and correct the profile
        corrected_profile, validation_report = validator.validate_and_correct_profile(profile_data)
        
        # Print the results
        print("\nCorrected Profile:")
        print(json.dumps(corrected_profile, indent=2))
        
        print("\nValidation Report:")
        print(json.dumps(validation_report, indent=2))
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
