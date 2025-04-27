"""
Artist Profile Builder Module

This module integrates all components of the Artist Profile Builder
to provide a complete workflow for creating, validating, and storing
artist profiles.
"""

import logging
import json
import os
import sys
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import from sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from builder.input_handler import process_input, InputValidationError
from builder.llm_pipeline import ArtistProfileLLMPipeline, LLMPipelineError
from builder.profile_validator import ProfileValidator, ValidationError
from builder.storage_manager import StorageManager, StorageError
from builder.future_hooks import FutureHooks
from builder.error_handler import setup_logging_and_error_handling, ArtistBuilderError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.profile_builder")


class ArtistProfileBuilder:
    """
    Main class for the Artist Profile Builder, integrating all components.
    """

    def __init__(self):
        """Initialize the Artist Profile Builder."""
        # Set up logging and error handling
        self.logging_manager, self.error_handler = setup_logging_and_error_handling()
        self.logger = self.logging_manager.get_logger("profile_builder")
        
        # Initialize components
        self.llm_pipeline = ArtistProfileLLMPipeline()
        self.profile_validator = ProfileValidator()
        self.storage_manager = StorageManager()
        self.future_hooks = FutureHooks()
        
        self.logger.info("Initialized ArtistProfileBuilder")

    def create_artist_profile(self, input_data: Dict[str, Any], input_source: str = "api") -> Dict[str, Any]:
        """
        Create a complete artist profile from initial inputs.
        
        Args:
            input_data: Dictionary containing the initial user inputs
            input_source: Source of the input (cli, api, gui, file)
            
        Returns:
            Dictionary containing the created artist profile
        """
        start_time = time.time()
        self.logger.info(f"Starting artist profile creation from {input_source} input")
        
        try:
            # Process and validate input
            self.logger.info("Processing input data")
            processed_input = process_input(input_data, input_source)
            
            # Generate profile using LLM
            self.logger.info("Generating profile using LLM")
            profile_draft = self.llm_pipeline.generate_complete_profile(processed_input)
            
            # Validate and correct profile
            self.logger.info("Validating and correcting profile")
            corrected_profile, validation_report = self.profile_validator.validate_and_correct_profile(profile_draft)
            
            # If validation failed, log warnings but continue
            if not validation_report["is_valid"]:
                self.logger.warning(f"Profile validation has issues: {validation_report['errors']}")
                for error in validation_report["errors"]:
                    self.logger.warning(f"Validation error: {error}")
            
            # Apply custom validators from future hooks
            self.logger.info("Applying custom validators")
            custom_valid, custom_errors = self.future_hooks.validate_with_custom_validators(corrected_profile)
            if not custom_valid:
                self.logger.warning(f"Custom validation has issues: {custom_errors}")
                for error in custom_errors:
                    self.logger.warning(f"Custom validation error: {error}")
            
            # Save profile
            self.logger.info("Saving profile")
            file_path = self.storage_manager.save_profile(corrected_profile)
            self.logger.info(f"Saved profile to {file_path}")
            
            # Run post-generation hooks
            self.logger.info("Running post-generation hooks")
            self.future_hooks.run_post_generation_hooks(corrected_profile)
            
            # Log performance
            duration_ms = (time.time() - start_time) * 1000
            self.logging_manager.log_performance("profile_builder", "create_artist_profile", duration_ms)
            self.logger.info(f"Completed artist profile creation in {duration_ms:.2f}ms")
            
            # Log profile operation
            self.logging_manager.log_profile_operation(
                "create",
                corrected_profile.get("artist_id", "unknown"),
                f"Created {corrected_profile.get('genre', '')} artist profile: {corrected_profile.get('stage_name', '')}"
            )
            
            return corrected_profile
            
        except InputValidationError as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "create_artist_profile",
                "input_source": input_source,
                "error_type": "input"
            })
            raise
        except LLMPipelineError as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "create_artist_profile",
                "input_source": input_source,
                "error_type": "llm_pipeline"
            })
            raise
        except ValidationError as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "create_artist_profile",
                "input_source": input_source,
                "error_type": "validation"
            })
            raise
        except StorageError as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "create_artist_profile",
                "input_source": input_source,
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "create_artist_profile",
                "input_source": input_source,
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error in profile creation: {e}")

    def update_artist_profile(self, profile_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing artist profile.
        
        Args:
            profile_id: ID of the profile to update
            updates: Dictionary containing the updates to apply
            
        Returns:
            Dictionary containing the updated profile
        """
        start_time = time.time()
        self.logger.info(f"Starting artist profile update for profile {profile_id}")
        
        try:
            # Load existing profile
            self.logger.info(f"Loading profile {profile_id}")
            existing_profile = self.storage_manager.load_profile(profile_id)
            
            # Apply updates
            self.logger.info(f"Applying updates to profile")
            updated_profile = self.storage_manager.update_profile(profile_id, updates)
            
            # Validate updated profile
            self.logger.info("Validating updated profile")
            corrected_profile, validation_report = self.profile_validator.validate_and_correct_profile(updated_profile)
            
            # If validation failed, log warnings but continue
            if not validation_report["is_valid"]:
                self.logger.warning(f"Updated profile validation has issues: {validation_report['errors']}")
                for error in validation_report["errors"]:
                    self.logger.warning(f"Validation error: {error}")
            
            # Save corrected profile if needed
            if corrected_profile != updated_profile:
                self.logger.info("Saving corrected profile")
                file_path = self.storage_manager.save_profile(corrected_profile)
                self.logger.info(f"Saved corrected profile to {file_path}")
            
            # Track profile evolution
            self.logger.info("Tracking profile evolution")
            self.future_hooks.track_profile_evolution(existing_profile, corrected_profile)
            
            # Log performance
            duration_ms = (time.time() - start_time) * 1000
            self.logging_manager.log_performance("profile_builder", "update_artist_profile", duration_ms)
            self.logger.info(f"Completed artist profile update in {duration_ms:.2f}ms")
            
            # Log profile operation
            self.logging_manager.log_profile_operation(
                "update",
                corrected_profile.get("artist_id", "unknown"),
                f"Updated {corrected_profile.get('stage_name', '')} profile with {len(updates)} changes"
            )
            
            return corrected_profile
            
        except StorageError as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "update_artist_profile",
                "profile_id": profile_id,
                "error_type": "storage"
            })
            raise
        except ValidationError as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "update_artist_profile",
                "profile_id": profile_id,
                "error_type": "validation"
            })
            raise
        except Exception as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "update_artist_profile",
                "profile_id": profile_id,
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error in profile update: {e}")

    def get_artist_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Get an artist profile by ID.
        
        Args:
            profile_id: ID of the profile to get
            
        Returns:
            Dictionary containing the profile data
        """
        try:
            self.logger.info(f"Getting artist profile {profile_id}")
            profile = self.storage_manager.load_profile(profile_id)
            
            # Log profile operation
            self.logging_manager.log_profile_operation(
                "get",
                profile_id,
                f"Retrieved profile: {profile.get('stage_name', '')}"
            )
            
            return profile
            
        except StorageError as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "get_artist_profile",
                "profile_id": profile_id,
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "get_artist_profile",
                "profile_id": profile_id,
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error getting profile: {e}")

    def delete_artist_profile(self, profile_id: str, create_backup: bool = True) -> bool:
        """
        Delete an artist profile.
        
        Args:
            profile_id: ID of the profile to delete
            create_backup: Whether to create a backup before deletion
            
        Returns:
            Boolean indicating success
        """
        try:
            self.logger.info(f"Deleting artist profile {profile_id}")
            success = self.storage_manager.delete_profile(profile_id, create_backup)
            
            # Log profile operation
            self.logging_manager.log_profile_operation(
                "delete",
                profile_id,
                f"Deleted profile (backup: {create_backup})"
            )
            
            return success
            
        except StorageError as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "delete_artist_profile",
                "profile_id": profile_id,
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "delete_artist_profile",
                "profile_id": profile_id,
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error deleting profile: {e}")

    def list_artist_profiles(self) -> List[Dict[str, Any]]:
        """
        List all artist profiles.
        
        Returns:
            List of dictionaries containing profile summaries
        """
        try:
            self.logger.info("Listing all artist profiles")
            profiles = self.storage_manager.list_profiles()
            
            self.logger.info(f"Found {len(profiles)} profiles")
            return profiles
            
        except StorageError as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "list_artist_profiles",
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "list_artist_profiles",
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error listing profiles: {e}")

    def search_artist_profiles(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for artist profiles matching criteria.
        
        Args:
            search_criteria: Dictionary containing search criteria
            
        Returns:
            List of dictionaries containing matching profile summaries
        """
        try:
            self.logger.info(f"Searching artist profiles with criteria: {json.dumps(search_criteria)}")
            profiles = self.storage_manager.search_profiles(search_criteria)
            
            self.logger.info(f"Found {len(profiles)} matching profiles")
            return profiles
            
        except StorageError as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "search_artist_profiles",
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "search_artist_profiles",
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error searching profiles: {e}")

    def apply_trend_analysis(self, profile_id: str, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply trend analysis to an artist profile.
        
        Args:
            profile_id: ID of the profile to update
            trend_data: Dictionary containing trend data
            
        Returns:
            Dictionary containing the updated profile
        """
        try:
            self.logger.info(f"Applying trend analysis to profile {profile_id}")
            
            # Load existing profile
            existing_profile = self.storage_manager.load_profile(profile_id)
            
            # Apply trend analysis
            updated_profile = self.future_hooks.apply_trend_analysis(existing_profile, trend_data)
            
            # Save updated profile
            file_path = self.storage_manager.save_profile(updated_profile)
            
            # Track profile evolution
            self.future_hooks.track_profile_evolution(existing_profile, updated_profile)
            
            # Log profile operation
            self.logging_manager.log_profile_operation(
                "trend_analysis",
                profile_id,
                f"Applied trend analysis to {updated_profile.get('stage_name', '')}"
            )
            
            return updated_profile
            
        except StorageError as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "apply_trend_analysis",
                "profile_id": profile_id,
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "apply_trend_analysis",
                "profile_id": profile_id,
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error applying trend analysis: {e}")

    def adapt_behavior(self, profile_id: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt an artist profile's behavior based on performance data.
        
        Args:
            profile_id: ID of the profile to update
            performance_data: Dictionary containing performance data
            
        Returns:
            Dictionary containing the updated profile
        """
        try:
            self.logger.info(f"Adapting behavior for profile {profile_id}")
            
            # Load existing profile
            existing_profile = self.storage_manager.load_profile(profile_id)
            
            # Apply behavior adaptation
            updated_profile = self.future_hooks.adapt_behavior(existing_profile, performance_data)
            
            # Save updated profile
            file_path = self.storage_manager.save_profile(updated_profile)
            
            # Track profile evolution
            self.future_hooks.track_profile_evolution(existing_profile, updated_profile)
            
            # Log profile operation
            self.logging_manager.log_profile_operation(
                "behavior_adaptation",
                profile_id,
                f"Adapted behavior for {updated_profile.get('stage_name', '')}"
            )
            
            return updated_profile
            
        except StorageError as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "adapt_behavior",
                "profile_id": profile_id,
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "adapt_behavior",
                "profile_id": profile_id,
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error adapting behavior: {e}")


def main():
    """Main function for testing the Artist Profile Builder."""
    # Example input data
    input_data = {
        "stage_name": "Neon Horizon",
        "genre": "Electronic",
        "subgenres": ["Synthwave", "Chillwave"],
        "style_description": "Retro-futuristic electronic music with nostalgic 80s influences",
        "voice_type": "Ethereal female vocals with vocoder effects",
        "personality_traits": ["Mysterious", "Introspective"],
        "target_audience": "25-35 year old electronic music fans",
        "visual_identity_prompt": "Neon cityscape at night with purple and blue color palette"
    }
    
    try:
        # Initialize profile builder
        builder = ArtistProfileBuilder()
        
        # Create artist profile
        print("Creating artist profile...")
        profile = builder.create_artist_profile(input_data, "test")
        
        # Print the profile
        print(f"\nCreated profile: {profile['stage_name']} ({profile['artist_id']})")
        print(f"Genre: {profile['genre']}")
        print(f"Subgenres: {', '.join(profile['subgenres'])}")
        
        # List all profiles
        print("\nListing all profiles:")
        profiles = builder.list_artist_profiles()
        for p in profiles:
            print(f"  - {p['stage_name']} ({p['artist_id']})")
        
        # Update the profile
        print("\nUpdating profile...")
        updates = {
            "backstory": "Neon Horizon emerged from the digital underground in 2025, quickly gaining recognition for blending nostalgic synthwave elements with cutting-edge production techniques. Their debut track 'Digital Dreams' became a viral sensation.",
            "update_reason": "Added more detail to backstory"
        }
        updated_profile = builder.update_artist_profile(profile["artist_id"], updates)
        print(f"Updated profile backstory: {updated_profile['backstory'][:100]}...")
        
        # Apply trend analysis
        print("\nApplying trend analysis...")
        trend_data = {
            "trending_subgenres": ["Darksynth", "Vaporwave"],
            "genre_compatibility": {
                "Electronic": {
                    "Darksynth": 0.9,
                    "Vaporwave": 0.8
                }
            }
        }
        trend_profile = builder.apply_trend_analysis(profile["artist_id"], trend_data)
        print(f"Profile after trend analysis - Subgenres: {', '.join(trend_profile['subgenres'])}")
        
        # Get the profile
        print("\nGetting profile...")
        retrieved_profile = builder.get_artist_profile(profile["artist_id"])
        print(f"Retrieved profile: {retrieved_profile['stage_name']}")
        
        # Delete the profile (comment out to keep the profile for testing)
        # print("\nDeleting profile...")
        # builder.delete_artist_profile(profile["artist_id"])
        # print("Profile deleted")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
