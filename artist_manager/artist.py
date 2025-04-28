"""
Artist class for managing AI artist profiles.

This module provides the core Artist class for creating, validating,
serializing, and managing artist profiles according to the schema.
"""

import os
import yaml
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_manager.artist")


class Artist:
    """
    Core class for managing AI artist profiles.
    
    This class provides methods for creating, validating, serializing,
    and managing artist profiles according to the schema.
    """
    
    def __init__(self, profile_data: Optional[Dict[str, Any]] = None, schema_path: Optional[str] = None):
        """
        Initialize an Artist instance.
        
        Args:
            profile_data: Optional dictionary containing artist profile data
            schema_path: Optional path to the schema file (uses default if None)
        """
        # Set default schema path if not provided
        if schema_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            schema_path = os.path.join(current_dir, "artist_profile_schema.yaml")
        
        self.schema_path = schema_path
        self._schema = self._load_schema()
        
        # Initialize profile data
        if profile_data:
            self.profile = profile_data
            # Validate the provided profile
            is_valid, errors = self.validate()
            if not is_valid:
                logger.warning(f"Provided profile has validation errors: {errors}")
        else:
            # Create empty profile with required fields
            self.profile = {
                "artist_id": str(uuid.uuid4()),
                "creation_date": datetime.now().isoformat(),
                "update_history": [],
                "metadata": {}
            }
    
    def _load_schema(self) -> Dict[str, Any]:
        """
        Load the artist profile schema from YAML file.
        
        Returns:
            Dictionary containing the schema
        """
        try:
            with open(self.schema_path, 'r') as f:
                schema = yaml.safe_load(f)
            logger.debug("Successfully loaded schema")
            return schema
        except Exception as e:
            logger.error(f"Error loading schema: {str(e)}")
            raise ValueError(f"Failed to load schema from {self.schema_path}: {str(e)}")
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the artist profile against the schema.
        
        Returns:
            Tuple containing (is_valid, error_messages)
        """
        errors = []
        
        # Check required fields
        required_fields = self._schema["artist_profile"]["required"]
        for field in required_fields:
            if field not in self.profile:
                errors.append(f"Missing required field: {field}")
        
        # Validate field types and constraints
        if "artist_id" in self.profile and not isinstance(self.profile["artist_id"], str):
            errors.append("artist_id must be a string")
        
        if "stage_name" in self.profile:
            if not isinstance(self.profile["stage_name"], str):
                errors.append("stage_name must be a string")
            elif len(self.profile["stage_name"]) < 1:
                errors.append("stage_name cannot be empty")
        
        if "genre" in self.profile:
            if not isinstance(self.profile["genre"], str):
                errors.append("genre must be a string")
            elif len(self.profile["genre"]) < 1:
                errors.append("genre cannot be empty")
        
        if "subgenres" in self.profile:
            if not isinstance(self.profile["subgenres"], list):
                errors.append("subgenres must be a list")
            elif len(self.profile["subgenres"]) < 1:
                errors.append("subgenres must contain at least one item")
        
        if "personality_traits" in self.profile:
            if not isinstance(self.profile["personality_traits"], list):
                errors.append("personality_traits must be a list")
            elif len(self.profile["personality_traits"]) < 1:
                errors.append("personality_traits must contain at least one item")
        
        # Check settings if present
        if "settings" in self.profile:
            settings = self.profile["settings"]
            
            # Check release strategy
            if "release_strategy" in settings:
                rs = settings["release_strategy"]
                if "track_release_random_days" in rs:
                    days = rs["track_release_random_days"]
                    if not isinstance(days, list) or len(days) != 2:
                        errors.append("track_release_random_days must be a list with exactly 2 items")
                    elif days[0] > days[1]:
                        errors.append("track_release_random_days: min days must be less than or equal to max days")
                
                if "video_release_ratio" in rs:
                    ratio = rs["video_release_ratio"]
                    if not isinstance(ratio, (int, float)) or ratio < 0 or ratio > 1:
                        errors.append("video_release_ratio must be a number between 0 and 1")
        
        # Check content plan consistency
        has_plan_id = "current_content_plan_id" in self.profile and self.profile["current_content_plan_id"] is not None
        has_end_date = "content_plan_end_date" in self.profile and self.profile["content_plan_end_date"] is not None
        
        if has_plan_id != has_end_date:
            errors.append("Both current_content_plan_id and content_plan_end_date must be provided together")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the artist profile to a dictionary.
        
        Returns:
            Dictionary representation of the artist profile
        """
        return self.profile.copy()
    
    def to_json(self, indent: int = 2) -> str:
        """
        Convert the artist profile to a JSON string.
        
        Args:
            indent: Number of spaces for indentation
            
        Returns:
            JSON string representation of the artist profile
        """
        return json.dumps(self.profile, indent=indent)
    
    def to_yaml(self) -> str:
        """
        Convert the artist profile to a YAML string.
        
        Returns:
            YAML string representation of the artist profile
        """
        return yaml.dump(self.profile, sort_keys=False)
    
    def save(self, file_path: str, format: str = "json") -> bool:
        """
        Save the artist profile to a file.
        
        Args:
            file_path: Path to save the file
            format: Format to save as ("json" or "yaml")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            if format.lower() == "json":
                with open(file_path, 'w') as f:
                    json.dump(self.profile, f, indent=2)
            elif format.lower() == "yaml":
                with open(file_path, 'w') as f:
                    yaml.dump(self.profile, f, sort_keys=False)
            else:
                logger.error(f"Unsupported format: {format}")
                return False
            
            logger.info(f"Saved artist profile to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving artist profile: {str(e)}")
            return False
    
    @classmethod
    def load(cls, file_path: str, schema_path: Optional[str] = None) -> 'Artist':
        """
        Load an artist profile from a file.
        
        Args:
            file_path: Path to the file (JSON or YAML)
            schema_path: Optional path to the schema file
            
        Returns:
            Artist instance with the loaded profile
        """
        try:
            # Determine file format from extension
            if file_path.lower().endswith('.json'):
                with open(file_path, 'r') as f:
                    profile_data = json.load(f)
            elif file_path.lower().endswith(('.yaml', '.yml')):
                with open(file_path, 'r') as f:
                    profile_data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            logger.info(f"Loaded artist profile from {file_path}")
            return cls(profile_data, schema_path)
        except Exception as e:
            logger.error(f"Error loading artist profile: {str(e)}")
            raise ValueError(f"Failed to load artist profile from {file_path}: {str(e)}")
    
    def update(self, updates: Dict[str, Any], update_reason: Optional[str] = None, update_source: Optional[str] = None) -> bool:
        """
        Update the artist profile with new values and record the update in history.
        
        Args:
            updates: Dictionary of fields to update
            update_reason: Optional reason for the update
            update_source: Optional source of the update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a copy of the profile for validation
            updated_profile = self.profile.copy()
            
            # Track which fields are being updated
            updated_fields = []
            
            # Apply updates
            for key, value in updates.items():
                if "." in key:
                    # Handle nested fields (e.g., "settings.release_strategy.video_release_ratio")
                    parts = key.split(".")
                    current = updated_profile
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
                    updated_fields.append(key)
                else:
                    # Handle top-level fields
                    updated_profile[key] = value
                    updated_fields.append(key)
            
            # Create update history item
            update_item = {
                "update_date": datetime.now().date().isoformat(),
                "updated_fields": updated_fields
            }
            
            if update_reason:
                update_item["update_reason"] = update_reason
            
            if update_source:
                update_item["update_source"] = update_source
            
            # Add to update history
            if "update_history" not in updated_profile:
                updated_profile["update_history"] = []
            
            updated_profile["update_history"].append(update_item)
            
            # Validate the updated profile
            temp_artist = Artist(updated_profile, self.schema_path)
            is_valid, errors = temp_artist.validate()
            
            if not is_valid:
                logger.error(f"Validation failed for updated profile: {errors}")
                return False
            
            # Apply the validated updates to the actual profile
            self.profile = updated_profile
            logger.info(f"Updated artist profile with {len(updated_fields)} fields")
            return True
        except Exception as e:
            logger.error(f"Error updating artist profile: {str(e)}")
            return False
    
    def get_value(self, field_path: str, default: Any = None) -> Any:
        """
        Get a value from the artist profile using dot notation for nested fields.
        
        Args:
            field_path: Path to the field (e.g., "settings.release_strategy.video_release_ratio")
            default: Default value to return if the field doesn't exist
            
        Returns:
            The field value or the default if not found
        """
        try:
            if "." in field_path:
                parts = field_path.split(".")
                current = self.profile
                for part in parts:
                    if part not in current:
                        return default
                    current = current[part]
                return current
            else:
                return self.profile.get(field_path, default)
        except Exception:
            return default
    
    def set_value(self, field_path: str, value: Any) -> bool:
        """
        Set a value in the artist profile using dot notation for nested fields.
        
        Args:
            field_path: Path to the field (e.g., "settings.release_strategy.video_release_ratio")
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            updates = {field_path: value}
            return self.update(updates)
        except Exception as e:
            logger.error(f"Error setting value: {str(e)}")
            return False
