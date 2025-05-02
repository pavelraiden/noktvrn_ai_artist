"""
Storage Manager Module for Artist Profile Builder

This module handles the storage and retrieval of artist profiles,
including directory management, filename generation, serialization,
and version control.
"""

import logging
import json
import os
import sys
import uuid
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import shutil

# Add parent directory to path to import from sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import schema validation from schema module
from schema.artist_profile_schema import ArtistProfile

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.storage_manager")


class StorageError(Exception):
    """Exception raised for errors in the storage operations."""

    pass


class StorageManager:
    """
    Manages the storage and retrieval of artist profiles.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the storage manager.

        Args:
            storage_dir: Optional path to the storage directory. If not provided,
                        defaults to /artist_profiles in the project root.
        """
        # Set default storage directory if not provided
        if storage_dir is None:
            # Get the project root directory (two levels up from this file)
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            storage_dir = os.path.join(project_root, "artist_profiles")

        self.storage_dir = storage_dir
        self.ensure_storage_directory()
        logger.info(
            f"Initialized StorageManager with storage directory: {self.storage_dir}"
        )

    def ensure_storage_directory(self) -> None:
        """
        Ensure the storage directory exists, creating it if necessary.
        """
        try:
            os.makedirs(self.storage_dir, exist_ok=True)
            logger.info(f"Ensured storage directory exists: {self.storage_dir}")
        except Exception as e:
            logger.error(f"Error creating storage directory: {e}")
            raise StorageError(f"Failed to create storage directory: {e}")

    def generate_filename(self, profile_data: Dict[str, Any]) -> str:
        """
        Generate a filename for an artist profile based on its ID.

        Args:
            profile_data: Dictionary containing the profile data

        Returns:
            String containing the filename
        """
        # Use the artist_id if available, otherwise generate a new UUID
        artist_id = profile_data.get("artist_id", str(uuid.uuid4()))

        # Ensure artist_id is set in the profile
        if "artist_id" not in profile_data:
            profile_data["artist_id"] = artist_id

        # Create filename with UUID
        filename = f"{artist_id}.json"

        logger.info(f"Generated filename for profile: {filename}")
        return filename

    def save_profile(
        self, profile_data: Dict[str, Any], create_backup: bool = True
    ) -> str:
        """
        Save an artist profile to the storage directory.

        Args:
            profile_data: Dictionary containing the profile data
            create_backup: Whether to create a backup of existing file

        Returns:
            String containing the path to the saved file
        """
        try:
            # Generate filename
            filename = self.generate_filename(profile_data)
            file_path = os.path.join(self.storage_dir, filename)

            # Create backup if file exists and backup is requested
            if os.path.exists(file_path) and create_backup:
                self._create_backup(file_path)

            # Add timestamp if not present
            if "last_updated" not in profile_data:
                profile_data["last_updated"] = datetime.now().isoformat()

            # Save the profile
            with open(file_path, "w") as f:
                json.dump(profile_data, f, indent=2)

            logger.info(f"Saved profile to {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            raise StorageError(f"Failed to save profile: {e}")

    def _create_backup(self, file_path: str) -> str:
        """
        Create a backup of an existing profile file.

        Args:
            file_path: Path to the file to backup

        Returns:
            String containing the path to the backup file
        """
        try:
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.storage_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)

            filename = os.path.basename(file_path)
            backup_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.json"
            backup_path = os.path.join(backup_dir, backup_filename)

            # Copy the file
            shutil.copy2(file_path, backup_path)

            logger.info(f"Created backup of {file_path} at {backup_path}")
            return backup_path

        except Exception as e:
            logger.warning(f"Error creating backup: {e}")
            # Continue without backup if it fails
            return ""

    def load_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Load an artist profile from the storage directory.

        Args:
            profile_id: ID of the profile to load

        Returns:
            Dictionary containing the profile data
        """
        try:
            # Construct file path
            filename = f"{profile_id}.json"
            file_path = os.path.join(self.storage_dir, filename)

            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"Profile file not found: {file_path}")
                raise StorageError(f"Profile not found with ID: {profile_id}")

            # Load the profile
            with open(file_path, "r") as f:
                profile_data = json.load(f)

            logger.info(f"Loaded profile from {file_path}")
            return profile_data

        except Exception as e:
            logger.error(f"Error loading profile: {e}")
            raise StorageError(f"Failed to load profile: {e}")

    def list_profiles(self) -> List[Dict[str, Any]]:
        """
        List all artist profiles in the storage directory.

        Returns:
            List of dictionaries containing profile summaries
        """
        try:
            profiles = []

            # Get all JSON files in the storage directory
            for filename in os.listdir(self.storage_dir):
                if filename.endswith(".json") and os.path.isfile(
                    os.path.join(self.storage_dir, filename)
                ):
                    try:
                        # Load the profile
                        file_path = os.path.join(self.storage_dir, filename)
                        with open(file_path, "r") as f:
                            profile_data = json.load(f)

                        # Create summary
                        summary = {
                            "artist_id": profile_data.get(
                                "artist_id", os.path.splitext(filename)[0]
                            ),
                            "stage_name": profile_data.get("stage_name", "Unknown"),
                            "genre": profile_data.get("genre", "Unknown"),
                            "creation_date": profile_data.get(
                                "creation_date", "Unknown"
                            ),
                            "last_updated": profile_data.get("last_updated", "Unknown"),
                            "file_path": file_path,
                        }

                        profiles.append(summary)
                    except Exception as e:
                        logger.warning(f"Error loading profile {filename}: {e}")
                        # Continue with next file

            logger.info(f"Listed {len(profiles)} profiles")
            return profiles

        except Exception as e:
            logger.error(f"Error listing profiles: {e}")
            raise StorageError(f"Failed to list profiles: {e}")

    def delete_profile(self, profile_id: str, create_backup: bool = True) -> bool:
        """
        Delete an artist profile from the storage directory.

        Args:
            profile_id: ID of the profile to delete
            create_backup: Whether to create a backup before deletion

        Returns:
            Boolean indicating success
        """
        try:
            # Construct file path
            filename = f"{profile_id}.json"
            file_path = os.path.join(self.storage_dir, filename)

            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"Profile file not found for deletion: {file_path}")
                raise StorageError(f"Profile not found with ID: {profile_id}")

            # Create backup if requested
            if create_backup:
                self._create_backup(file_path)

            # Delete the file
            os.remove(file_path)

            logger.info(f"Deleted profile {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error deleting profile: {e}")
            raise StorageError(f"Failed to delete profile: {e}")

    def search_profiles(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for profiles matching the given criteria.

        Args:
            search_criteria: Dictionary containing search criteria

        Returns:
            List of dictionaries containing matching profile summaries
        """
        try:
            all_profiles = self.list_profiles()
            matching_profiles = []

            # Load full profiles for searching
            for profile_summary in all_profiles:
                try:
                    profile_data = self.load_profile(profile_summary["artist_id"])

                    # Check if profile matches all criteria
                    matches = True
                    for key, value in search_criteria.items():
                        # Handle nested keys with dot notation (e.g., "settings.release_strategy.video_release_ratio")
                        if "." in key:
                            parts = key.split(".")
                            current = profile_data
                            for part in parts:
                                if part not in current:
                                    matches = False
                                    break
                                current = current[part]

                            # Check if the final value matches
                            if matches and current != value:
                                matches = False

                        # Handle direct keys
                        elif key not in profile_data or profile_data[key] != value:
                            matches = False
                            break

                    if matches:
                        matching_profiles.append(profile_summary)

                except Exception as e:
                    logger.warning(
                        f"Error processing profile {profile_summary['artist_id']} during search: {e}"
                    )
                    # Continue with next profile

            logger.info(f"Found {len(matching_profiles)} profiles matching criteria")
            return matching_profiles

        except Exception as e:
            logger.error(f"Error searching profiles: {e}")
            raise StorageError(f"Failed to search profiles: {e}")

    def update_profile(
        self, profile_id: str, updates: Dict[str, Any], create_backup: bool = True
    ) -> Dict[str, Any]:
        """
        Update an existing artist profile.

        Args:
            profile_id: ID of the profile to update
            updates: Dictionary containing the updates to apply
            create_backup: Whether to create a backup before updating

        Returns:
            Dictionary containing the updated profile data
        """
        try:
            # Load the existing profile
            profile_data = self.load_profile(profile_id)

            # Create update history item
            update_item = {
                "update_date": datetime.now().isoformat(),
                "updated_fields": list(updates.keys()),
                "update_reason": updates.pop("update_reason", None),
                "update_source": updates.pop("update_source", None),
            }

            # Add to update history
            if "update_history" not in profile_data:
                profile_data["update_history"] = []
            profile_data["update_history"].append(update_item)

            # Apply updates
            for key, value in updates.items():
                if "." in key:
                    # Handle nested fields (e.g., "settings.release_strategy.video_release_ratio")
                    parts = key.split(".")
                    current = profile_data
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
                else:
                    # Handle top-level fields
                    profile_data[key] = value

            # Update last_updated timestamp
            profile_data["last_updated"] = datetime.now().isoformat()

            # Save the updated profile
            self.save_profile(profile_data, create_backup)

            logger.info(f"Updated profile {profile_id} with {len(updates)} updates")
            return profile_data

        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            raise StorageError(f"Failed to update profile: {e}")

    def export_profile(
        self,
        profile_id: str,
        export_format: str = "json",
        export_path: Optional[str] = None,
    ) -> str:
        """
        Export an artist profile to a file in the specified format.

        Args:
            profile_id: ID of the profile to export
            export_format: Format to export to (json, yaml, etc.)
            export_path: Optional path to export to

        Returns:
            String containing the path to the exported file
        """
        try:
            # Load the profile
            profile_data = self.load_profile(profile_id)

            # Generate export path if not provided
            if export_path is None:
                export_dir = os.path.join(self.storage_dir, "exports")
                os.makedirs(export_dir, exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = os.path.join(
                    export_dir, f"{profile_id}_{timestamp}.{export_format}"
                )

            # Export based on format
            if export_format.lower() == "json":
                with open(export_path, "w") as f:
                    json.dump(profile_data, f, indent=2)
            elif export_format.lower() == "yaml" or export_format.lower() == "yml":
                try:
                    import yaml

                    with open(export_path, "w") as f:
                        yaml.dump(profile_data, f, default_flow_style=False)
                except ImportError:
                    logger.warning("PyYAML not installed, falling back to JSON format")
                    export_path = export_path.replace(".yaml", ".json").replace(
                        ".yml", ".json"
                    )
                    with open(export_path, "w") as f:
                        json.dump(profile_data, f, indent=2)
            else:
                logger.warning(
                    f"Unsupported export format: {export_format}, falling back to JSON"
                )
                export_path = f"{os.path.splitext(export_path)[0]}.json"
                with open(export_path, "w") as f:
                    json.dump(profile_data, f, indent=2)

            logger.info(f"Exported profile {profile_id} to {export_path}")
            return export_path

        except Exception as e:
            logger.error(f"Error exporting profile: {e}")
            raise StorageError(f"Failed to export profile: {e}")

    def import_profile(
        self, import_path: str, overwrite_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Import an artist profile from a file.

        Args:
            import_path: Path to the file to import
            overwrite_existing: Whether to overwrite existing profile with same ID

        Returns:
            Dictionary containing the imported profile data
        """
        try:
            # Check file exists
            if not os.path.exists(import_path):
                logger.error(f"Import file not found: {import_path}")
                raise StorageError(f"Import file not found: {import_path}")

            # Determine format from extension
            file_ext = os.path.splitext(import_path)[1].lower()

            # Load the profile
            if file_ext == ".json":
                with open(import_path, "r") as f:
                    profile_data = json.load(f)
            elif file_ext in [".yaml", ".yml"]:
                try:
                    import yaml

                    with open(import_path, "r") as f:
                        profile_data = yaml.safe_load(f)
                except ImportError:
                    logger.error("PyYAML not installed, cannot import YAML file")
                    raise StorageError("PyYAML not installed, cannot import YAML file")
            else:
                logger.error(f"Unsupported import format: {file_ext}")
                raise StorageError(f"Unsupported import format: {file_ext}")

            # Check if profile has an artist_id
            if "artist_id" not in profile_data:
                profile_data["artist_id"] = str(uuid.uuid4())
                logger.info(
                    f"Added missing artist_id to imported profile: {profile_data['artist_id']}"
                )

            # Check if profile already exists
            existing_profiles = self.list_profiles()
            for profile in existing_profiles:
                if profile["artist_id"] == profile_data["artist_id"]:
                    if not overwrite_existing:
                        logger.error(
                            f"Profile with ID {profile_data['artist_id']} already exists and overwrite_existing is False"
                        )
                        raise StorageError(
                            f"Profile with ID {profile_data['artist_id']} already exists"
                        )
                    else:
                        logger.warning(
                            f"Overwriting existing profile with ID {profile_data['artist_id']}"
                        )

            # Save the imported profile
            self.save_profile(profile_data)

            logger.info(f"Imported profile from {import_path}")
            return profile_data

        except Exception as e:
            logger.error(f"Error importing profile: {e}")
            raise StorageError(f"Failed to import profile: {e}")


def main():
    """Main function for testing the storage manager."""
    # Example profile data
    profile_data = {
        "artist_id": str(uuid.uuid4()),
        "stage_name": "Neon Horizon",
        "genre": "Electronic",
        "subgenres": ["Synthwave", "Chillwave"],
        "style_description": "Retro-futuristic electronic music with nostalgic 80s influences and modern production techniques",
        "voice_type": "Ethereal female vocals with occasional vocoder effects",
        "personality_traits": ["Mysterious", "Introspective", "Futuristic"],
        "target_audience": "25-35 year old electronic music fans with nostalgia for 80s aesthetics",
        "visual_identity_prompt": "Neon cityscape at night with purple and blue color palette, retro-futuristic aesthetic",
        "song_prompt_generator": "electronic_synthwave_template_v2",
        "video_prompt_generator": "retro_futuristic_video_template",
        "creation_date": datetime.now().isoformat(),
        "backstory": "Neon Horizon emerged from the digital underground in 2025, quickly gaining recognition for blending nostalgic synthwave elements with cutting-edge production techniques.",
        "influences": ["Kavinsky", "The Midnight", "Gunship"],
        "settings": {
            "release_strategy": {
                "track_release_random_days": [3, 15],
                "video_release_ratio": 0.7,
                "content_plan_length_days": 90,
                "social_media_post_frequency": 3,
            },
            "llm_assignments": {
                "artist_prompt_llm": "gpt-4",
                "song_prompt_llm": "gpt-4",
                "video_prompt_llm": "gpt-4",
                "final_validator_llm": "gpt-4",
            },
            "training_data_version": "v1.0",
            "trend_alignment_behavior": "soft",
            "behavior_evolution_settings": {
                "allow_minor_genre_shifts": True,
                "allow_personality_shifts": True,
                "safe_mode": True,
                "evolution_speed": "medium",
                "preserve_core_identity": True,
            },
            "social_media_presence": {
                "platforms": ["instagram", "tiktok", "twitter"],
                "posting_style": "casual",
                "engagement_strategy": "moderate",
            },
            "performance_metrics_tracking": True,
        },
    }

    try:
        # Initialize storage manager
        storage_manager = StorageManager()

        # Save the profile
        file_path = storage_manager.save_profile(profile_data)
        print(f"Saved profile to: {file_path}")

        # List all profiles
        profiles = storage_manager.list_profiles()
        print(f"\nFound {len(profiles)} profiles:")
        for profile in profiles:
            print(f"  - {profile['stage_name']} ({profile['artist_id']})")

        # Load the profile
        loaded_profile = storage_manager.load_profile(profile_data["artist_id"])
        print(f"\nLoaded profile: {loaded_profile['stage_name']}")

        # Update the profile
        updates = {
            "backstory": "Neon Horizon emerged from the digital underground in 2025, quickly gaining recognition for blending nostalgic synthwave elements with cutting-edge production techniques. Their debut track 'Digital Dreams' became a viral sensation.",
            "update_reason": "Added more detail to backstory",
        }
        updated_profile = storage_manager.update_profile(
            profile_data["artist_id"], updates
        )
        print(f"\nUpdated profile backstory and added to update history")

        # Export the profile
        export_path = storage_manager.export_profile(profile_data["artist_id"])
        print(f"\nExported profile to: {export_path}")

        # Delete the profile (comment out to keep the profile for testing)
        # storage_manager.delete_profile(profile_data["artist_id"])
        # print(f"\nDeleted profile")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
