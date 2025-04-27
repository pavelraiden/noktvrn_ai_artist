"""
Enhanced Profile Builder Module with Production Polishing

This module integrates all components of the Artist Profile Builder
to provide a complete workflow for creating, validating, and storing
artist profiles with enhanced logging, error handling, and creation reports.
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
from builder.creation_report_manager import CreationReportManager

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
        self.creation_report_manager = CreationReportManager()
        
        self.logger.info("Initialized ArtistProfileBuilder with enhanced production features")

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
            # Log profile received event
            self.logger.info(f"Profile received from {input_source}: {json.dumps(input_data)[:100]}...")
            
            # Process and validate input
            self.logger.info("Processing input data")
            processed_input = process_input(input_data, input_source)
            
            # Generate profile using LLM
            self.logger.info("Generating profile using LLM")
            profile_draft = self.llm_pipeline.generate_complete_profile(processed_input)
            
            # Validate and correct profile
            self.logger.info("Validating and correcting profile")
            corrected_profile, validation_report = self.profile_validator.validate_and_correct_profile(profile_draft)
            
            # Log validation status
            if validation_report["is_valid"]:
                self.logger.info("Profile validation passed successfully")
            else:
                self.logger.warning(f"Profile validation has issues: {len(validation_report['errors'])} errors found")
                for error in validation_report['errors']:
                    self.logger.warning(f"Validation error: {error}")
                    
                # Log specific field failures
                if 'field_errors' in validation_report:
                    for field, error in validation_report['field_errors'].items():
                        self.logger.warning(f"Field validation error: {field} - {error}")
            
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
            
            # Generate and save creation report
            self.logger.info("Generating creation report")
            creation_report = self.creation_report_manager.generate_creation_report(
                corrected_profile, validation_report
            )
            report_path = self.creation_report_manager.save_creation_report(creation_report)
            self.logger.info(f"Saved creation report to {report_path}")
            
            # Create asset folders
            self.logger.info("Creating asset folders")
            asset_dir = self._create_asset_folders(corrected_profile)
            self.logger.info(f"Created asset folders at {asset_dir}")
            
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
            self.logger.error(f"Input validation error: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "create_artist_profile",
                "input_source": input_source,
                "error_type": "input",
                "input_data": input_data
            })
            raise
        except LLMPipelineError as e:
            self.logger.error(f"LLM pipeline error: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "create_artist_profile",
                "input_source": input_source,
                "error_type": "llm_pipeline"
            })
            raise
        except ValidationError as e:
            self.logger.error(f"Validation error: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "create_artist_profile",
                "input_source": input_source,
                "error_type": "validation",
                "validation_details": str(e)
            })
            raise
        except StorageError as e:
            self.logger.error(f"Storage error: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "create_artist_profile",
                "input_source": input_source,
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in profile creation: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "create_artist_profile",
                "input_source": input_source,
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error in profile creation: {e}")

    def _create_asset_folders(self, profile: Dict[str, Any]) -> str:
        """
        Create asset folders for an artist profile.
        
        Args:
            profile: The artist profile
            
        Returns:
            Path to the asset directory
        """
        artist_id = profile.get("artist_id", "unknown")
        stage_name = profile.get("stage_name", "Unknown Artist").replace(" ", "_")
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Create asset directory
        asset_dir = os.path.join(project_root, "assets", f"{stage_name}_{artist_id}")
        os.makedirs(asset_dir, exist_ok=True)
        
        # Create subdirectories
        subdirs = ["images", "audio", "video", "metadata", "social"]
        for subdir in subdirs:
            os.makedirs(os.path.join(asset_dir, subdir), exist_ok=True)
            
        return asset_dir

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
            self.logger.info(f"Applying updates to profile: {json.dumps(updates)[:100]}...")
            updated_profile = self.storage_manager.update_profile(profile_id, updates)
            
            # Validate updated profile
            self.logger.info("Validating updated profile")
            corrected_profile, validation_report = self.profile_validator.validate_and_correct_profile(updated_profile)
            
            # Log validation status
            if validation_report["is_valid"]:
                self.logger.info("Updated profile validation passed successfully")
            else:
                self.logger.warning(f"Updated profile validation has issues: {len(validation_report['errors'])} errors found")
                for error in validation_report['errors']:
                    self.logger.warning(f"Validation error: {error}")
                    
                # Log specific field failures
                if 'field_errors' in validation_report:
                    for field, error in validation_report['field_errors'].items():
                        self.logger.warning(f"Field validation error: {field} - {error}")
            
            # Save corrected profile if needed
            if corrected_profile != updated_profile:
                self.logger.info("Saving corrected profile")
                file_path = self.storage_manager.save_profile(corrected_profile)
                self.logger.info(f"Saved corrected profile to {file_path}")
            
            # Generate and save updated creation report
            self.logger.info("Generating updated creation report")
            creation_report = self.creation_report_manager.generate_creation_report(
                corrected_profile, validation_report
            )
            report_path = self.creation_report_manager.save_creation_report(creation_report)
            self.logger.info(f"Saved updated creation report to {report_path}")
            
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
            self.logger.error(f"Storage error: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "update_artist_profile",
                "profile_id": profile_id,
                "error_type": "storage"
            })
            raise
        except ValidationError as e:
            self.logger.error(f"Validation error: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "update_artist_profile",
                "profile_id": profile_id,
                "error_type": "validation",
                "validation_details": str(e)
            })
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in profile update: {str(e)}")
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
            self.logger.error(f"Storage error: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "get_artist_profile",
                "profile_id": profile_id,
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting profile: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "get_artist_profile",
                "profile_id": profile_id,
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error getting profile: {e}")

    def get_creation_report(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the creation report for an artist profile.
        
        Args:
            profile_id: ID of the profile
            
        Returns:
            Dictionary containing the creation report, or None if not found
        """
        try:
            self.logger.info(f"Getting creation report for profile {profile_id}")
            report = self.creation_report_manager.get_creation_report(profile_id)
            
            if report:
                self.logger.info(f"Retrieved creation report for profile {profile_id}")
            else:
                self.logger.warning(f"No creation report found for profile {profile_id}")
                
            return report
            
        except Exception as e:
            self.logger.error(f"Error getting creation report: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "get_creation_report",
                "profile_id": profile_id,
                "error_type": "unknown"
            })
            return None

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
            
            # Delete creation reports
            self.logger.info(f"Deleting creation reports for profile {profile_id}")
            self.creation_report_manager.delete_creation_report(profile_id)
            
            # Log profile operation
            self.logging_manager.log_profile_operation(
                "delete",
                profile_id,
                f"Deleted profile (backup: {create_backup})"
            )
            
            return success
            
        except StorageError as e:
            self.logger.error(f"Storage error: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "delete_artist_profile",
                "profile_id": profile_id,
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error deleting profile: {str(e)}")
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
            self.logger.error(f"Storage error: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "list_artist_profiles",
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error listing profiles: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "list_artist_profiles",
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error listing profiles: {e}")

    def list_creation_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List the most recent creation reports.
        
        Args:
            limit: Maximum number of reports to retrieve
            
        Returns:
            List of dictionaries containing creation reports
        """
        try:
            self.logger.info(f"Listing creation reports (limit: {limit})")
            reports = self.creation_report_manager.list_creation_reports(limit)
            
            self.logger.info(f"Found {len(reports)} creation reports")
            return reports
            
        except Exception as e:
            self.logger.error(f"Error listing creation reports: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "list_creation_reports",
                "error_type": "unknown"
            })
            return []

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
            self.logger.error(f"Storage error: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "search_artist_profiles",
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error searching profiles: {str(e)}")
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
            self.logger.info(f"Saved trend-updated profile to {file_path}")
            
            # Log profile operation
            self.logging_manager.log_profile_operation(
                "trend_analysis",
                profile_id,
                f"Applied trend analysis to {updated_profile.get('stage_name', '')}"
            )
            
            return updated_profile
            
        except StorageError as e:
            self.logger.error(f"Storage error: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "apply_trend_analysis",
                "profile_id": profile_id,
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error applying trend analysis: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "apply_trend_analysis",
                "profile_id": profile_id,
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error applying trend analysis: {e}")

    def adapt_behavior(self, profile_id: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt artist behavior based on performance data.
        
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
            self.logger.info(f"Saved behavior-adapted profile to {file_path}")
            
            # Log profile operation
            self.logging_manager.log_profile_operation(
                "behavior_adaptation",
                profile_id,
                f"Adapted behavior for {updated_profile.get('stage_name', '')}"
            )
            
            return updated_profile
            
        except StorageError as e:
            self.logger.error(f"Storage error: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "adapt_behavior",
                "profile_id": profile_id,
                "error_type": "storage"
            })
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error adapting behavior: {str(e)}")
            self.error_handler.handle_error(e, {
                "module": "profile_builder",
                "operation": "adapt_behavior",
                "profile_id": profile_id,
                "error_type": "unknown"
            })
            raise ArtistBuilderError(f"Unexpected error adapting behavior: {e}")


def main():
    """
    Main function for testing the Artist Profile Builder.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create builder
    builder = ArtistProfileBuilder()
    
    # Example input
    input_data = {
        "stage_name": "Test Artist",
        "genre": "Electronic",
        "subgenres": ["Synthwave", "Chillwave"],
        "style_description": "Test style description",
        "voice_type": "Test voice type",
        "personality_traits": ["Creative", "Innovative"],
        "target_audience": "Test audience",
        "visual_identity_prompt": "Test visual identity"
    }
    
    # Create profile
    try:
        profile = builder.create_artist_profile(input_data, "test")
        print(f"Created profile: {profile['stage_name']} ({profile['artist_id']})")
        
        # Get creation report
        report = builder.get_creation_report(profile['artist_id'])
        if report:
            print(f"Creation report: {json.dumps(report, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
