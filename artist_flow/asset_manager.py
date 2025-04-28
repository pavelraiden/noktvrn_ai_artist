"""
Asset management module for organizing and storing generated assets.

This module provides utilities for managing file paths, directory structures,
asset metadata, and bundling assets together for the artist creation flow.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import os
import json
import shutil
import uuid
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("asset_manager")


class AssetManager:
    """
    Manages the organization and storage of all generated assets.

    This class provides utilities for handling file paths, directory structures,
    asset metadata, and bundling assets together for the artist creation flow.
    """

    def __init__(
        self, base_dir: str = "/tmp/artist_flow/assets", create_dirs: bool = True
    ):
        """
        Initialize the asset manager.

        Args:
            base_dir: Base directory for storing assets
            create_dirs: Whether to create directories if they don't exist
        """
        self.base_dir = base_dir

        # Define standard subdirectories
        self.structure = {
            "profiles": os.path.join(base_dir, "profiles"),
            "music": os.path.join(base_dir, "music"),
            "images": os.path.join(base_dir, "images"),
            "bundles": os.path.join(base_dir, "bundles"),
            "metadata": os.path.join(base_dir, "metadata"),
        }

        # Create directories if needed
        if create_dirs:
            for directory in self.structure.values():
                os.makedirs(directory, exist_ok=True)

        logger.info(f"Initialized AssetManager with base directory: {base_dir}")

    def get_asset_path(
        self, asset_type: str, session_id: str, filename: Optional[str] = None
    ) -> str:
        """
        Get the path for an asset.

        Args:
            asset_type: Type of asset (profile, music, image, bundle, metadata)
            session_id: Session ID
            filename: Optional filename (if None, just returns the directory)

        Returns:
            Path to the asset or directory
        """
        # Get the base directory for this asset type
        if asset_type in self.structure:
            base_path = self.structure[asset_type]
        else:
            base_path = os.path.join(self.base_dir, asset_type)

        # Create session directory
        session_dir = os.path.join(base_path, session_id)
        os.makedirs(session_dir, exist_ok=True)

        # Return full path if filename provided, otherwise just the directory
        if filename:
            return os.path.join(session_dir, filename)
        else:
            return session_dir

    def save_artist_profile(
        self, artist_profile: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """
        Save an artist profile.

        Args:
            artist_profile: The artist profile to save
            session_id: Session ID

        Returns:
            Updated artist profile with file paths
        """
        logger.info(f"Saving artist profile for session {session_id}")

        # Create a copy of the profile to avoid modifying the original
        profile = artist_profile.copy()

        # Add timestamp if not present
        if "created_at" not in profile:
            profile["created_at"] = datetime.now().isoformat()

        # Add session ID if not present
        if "session_id" not in profile:
            profile["session_id"] = session_id

        # Get the path for the profile JSON
        profile_path = self.get_asset_path(
            asset_type="profiles",
            session_id=session_id,
            filename=f"{profile.get('name', 'artist').replace(' ', '_')}_profile.json",
        )

        # Save the profile as JSON
        with open(profile_path, "w") as f:
            json.dump(profile, f, indent=2)

        # Update the profile with the file path
        profile["file_path"] = profile_path

        logger.info(f"Saved artist profile to {profile_path}")
        return profile

    def save_music_assets(
        self, music_assets: List[Dict[str, Any]], session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Save music assets.

        Args:
            music_assets: List of music assets to save
            session_id: Session ID

        Returns:
            Updated music assets with file paths
        """
        logger.info(f"Saving {len(music_assets)} music assets for session {session_id}")

        updated_assets = []
        for asset in music_assets:
            # Create a copy of the asset to avoid modifying the original
            updated_asset = asset.copy()

            # Get the source file path
            source_path = updated_asset.get("file_path")
            if not source_path or not os.path.exists(source_path):
                logger.warning(f"Source file not found: {source_path}")
                updated_assets.append(updated_asset)
                continue

            # Get the destination path
            filename = os.path.basename(source_path)
            dest_path = self.get_asset_path(
                asset_type="music", session_id=session_id, filename=filename
            )

            # Copy the file if source and destination are different
            if source_path != dest_path:
                shutil.copy2(source_path, dest_path)
                logger.info(f"Copied music asset from {source_path} to {dest_path}")

            # Update the asset with the new file path
            updated_asset["file_path"] = dest_path
            updated_assets.append(updated_asset)

        return updated_assets

    def save_image_assets(
        self, image_assets: List[Dict[str, Any]], session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Save image assets.

        Args:
            image_assets: List of image assets to save
            session_id: Session ID

        Returns:
            Updated image assets with file paths
        """
        logger.info(f"Saving {len(image_assets)} image assets for session {session_id}")

        updated_assets = []
        for asset in image_assets:
            # Create a copy of the asset to avoid modifying the original
            updated_asset = asset.copy()

            # Get the source file path
            source_path = updated_asset.get("file_path")
            if not source_path or not os.path.exists(source_path):
                logger.warning(f"Source file not found: {source_path}")
                updated_assets.append(updated_asset)
                continue

            # Get the destination path
            filename = os.path.basename(source_path)
            dest_path = self.get_asset_path(
                asset_type="images", session_id=session_id, filename=filename
            )

            # Copy the file if source and destination are different
            if source_path != dest_path:
                shutil.copy2(source_path, dest_path)
                logger.info(f"Copied image asset from {source_path} to {dest_path}")

            # Update the asset with the new file path
            updated_asset["file_path"] = dest_path
            updated_assets.append(updated_asset)

        return updated_assets

    def create_asset_bundle(
        self,
        artist_profile: Dict[str, Any],
        music_assets: List[Dict[str, Any]],
        image_assets: List[Dict[str, Any]],
        session_id: str,
        bundle_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a bundle of all assets for an artist.

        Args:
            artist_profile: The artist profile
            music_assets: List of music assets
            image_assets: List of image assets
            session_id: Session ID
            bundle_name: Optional name for the bundle (generated if None)

        Returns:
            Dictionary containing the bundle information
        """
        logger.info(f"Creating asset bundle for session {session_id}")

        # Generate bundle name if not provided
        if not bundle_name:
            artist_name = artist_profile.get("name", "artist").replace(" ", "_")
            bundle_name = (
                f"{artist_name}_bundle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

        # Create bundle directory
        bundle_dir = self.get_asset_path(
            asset_type="bundles", session_id=session_id, filename=bundle_name
        )
        os.makedirs(bundle_dir, exist_ok=True)

        # Create subdirectories
        os.makedirs(os.path.join(bundle_dir, "music"), exist_ok=True)
        os.makedirs(os.path.join(bundle_dir, "images"), exist_ok=True)

        # Save artist profile to bundle
        profile_path = os.path.join(bundle_dir, "artist_profile.json")
        with open(profile_path, "w") as f:
            json.dump(artist_profile, f, indent=2)

        # Copy music assets to bundle
        bundled_music = []
        for asset in music_assets:
            source_path = asset.get("file_path")
            if source_path and os.path.exists(source_path):
                filename = os.path.basename(source_path)
                dest_path = os.path.join(bundle_dir, "music", filename)
                shutil.copy2(source_path, dest_path)

                # Update asset with bundle path
                bundled_asset = asset.copy()
                bundled_asset["bundle_path"] = dest_path
                bundled_music.append(bundled_asset)

        # Copy image assets to bundle
        bundled_images = []
        for asset in image_assets:
            source_path = asset.get("file_path")
            if source_path and os.path.exists(source_path):
                filename = os.path.basename(source_path)
                dest_path = os.path.join(bundle_dir, "images", filename)
                shutil.copy2(source_path, dest_path)

                # Update asset with bundle path
                bundled_asset = asset.copy()
                bundled_asset["bundle_path"] = dest_path
                bundled_images.append(bundled_asset)

        # Create bundle metadata
        bundle_metadata = {
            "bundle_id": f"{session_id}_{bundle_name}",
            "artist_name": artist_profile.get("name", "Unknown Artist"),
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "profile_path": profile_path,
            "music_assets": bundled_music,
            "image_assets": bundled_images,
            "bundle_dir": bundle_dir,
        }

        # Save bundle metadata
        metadata_path = os.path.join(bundle_dir, "bundle_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(bundle_metadata, f, indent=2)

        logger.info(f"Created asset bundle at {bundle_dir}")
        return bundle_metadata

    def load_asset_bundle(
        self, bundle_id: str, session_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Load an asset bundle.

        Args:
            bundle_id: ID of the bundle to load
            session_id: Optional session ID (extracted from bundle_id if None)

        Returns:
            Dictionary containing the bundle information, or None if not found
        """
        # Extract session ID from bundle ID if not provided
        if not session_id:
            parts = bundle_id.split("_", 1)
            if len(parts) > 1:
                session_id = parts[0]
            else:
                logger.error(
                    f"Could not extract session ID from bundle ID: {bundle_id}"
                )
                return None

        # Try to find the bundle metadata file
        bundle_dir = self.get_asset_path(asset_type="bundles", session_id=session_id)

        # Look for bundle metadata file
        for root, _, files in os.walk(bundle_dir):
            for file in files:
                if file == "bundle_metadata.json":
                    metadata_path = os.path.join(root, file)
                    try:
                        with open(metadata_path, "r") as f:
                            bundle_metadata = json.load(f)
                            if bundle_metadata.get("bundle_id") == bundle_id:
                                logger.info(f"Loaded asset bundle: {bundle_id}")
                                return bundle_metadata
                    except Exception as e:
                        logger.error(f"Error loading bundle metadata: {str(e)}")

        logger.warning(f"Asset bundle not found: {bundle_id}")
        return None


# Factory function to create an asset manager
def create_asset_manager(base_dir: str = "/tmp/artist_flow/assets") -> AssetManager:
    """
    Factory function to create an asset manager.

    Args:
        base_dir: Base directory for storing assets

    Returns:
        An asset manager instance
    """
    return AssetManager(base_dir=base_dir)


# Example usage
if __name__ == "__main__":
    # Create an asset manager
    manager = create_asset_manager()

    # Example artist profile
    example_profile = {
        "name": "NightShade",
        "genre": "Dark Trap",
        "style": "Mysterious, Cold",
    }

    # Example session ID
    session_id = "test_session_123"

    # Save the artist profile
    saved_profile = manager.save_artist_profile(example_profile, session_id)

    # Print the result
    import json

    print(json.dumps(saved_profile, indent=2))
