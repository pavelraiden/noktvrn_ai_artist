# /home/ubuntu/workspace/project_root/release_chain/release_manager.py

import logging
import os
import json
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ReleaseStatus(Enum):
    PENDING_PREVIEW = "pending_preview"
    PREVIEW_READY = "preview_ready"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_UPLOAD = "pending_upload"
    UPLOADED = "uploaded"
    FAILED = "failed"

class ReleaseManagerError(Exception):
    """Custom exception for Release Manager errors."""
    pass

class ReleaseManager:
    """Manages the release pipeline for generated songs."""

    def __init__(self, config: dict):
        """Initializes the Release Manager.

        Args:
            config: Configuration dictionary. Expected keys:
                    - "release_metadata_dir": Directory to store release metadata.
                    - "preview_dir": Directory for preview files.
                    - "upload_dir": Directory for final upload-ready files.
        """
        logger.info("Initializing ReleaseManager.")
        self.config = config
        self.release_metadata_dir = config.get("release_metadata_dir", "./release_metadata")
        self.preview_dir = config.get("preview_dir", "./previews")
        self.upload_dir = config.get("upload_dir", "./upload_ready")

        os.makedirs(self.release_metadata_dir, exist_ok=True)
        os.makedirs(self.preview_dir, exist_ok=True)
        os.makedirs(self.upload_dir, exist_ok=True)
        logger.info("Release directories ensured.")

    def _generate_release_id(self, song_title: str) -> str:
        """Generates a unique release ID."""
        timestamp = datetime.now().strftime("%Y%m%d%HM%S%f")
        safe_title = "".join(c if c.isalnum() else "_" for c in song_title[:20])
        release_id = f"release_{safe_title}_{timestamp}"
        logger.debug(f"Generated release_id: {release_id}")
        return release_id

    def _get_metadata_path(self, release_id: str) -> str:
        return os.path.join(self.release_metadata_dir, f"{release_id}.json")

    def _load_metadata(self, release_id: str) -> dict:
        metadata_path = self._get_metadata_path(release_id)
        if not os.path.exists(metadata_path):
            raise ReleaseManagerError(f"Metadata for release_id 	{release_id}	 not found.")
        try:
            with open(metadata_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON for release_id {release_id}: {e}")
            raise ReleaseManagerError(f"Invalid metadata for release_id {release_id}.") from e

    def _save_metadata(self, release_id: str, metadata: dict):
        metadata_path = self._get_metadata_path(release_id)
        metadata["last_updated"] = datetime.now().isoformat()
        try:
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=4)
            logger.info(f"Saved metadata for release_id: {release_id}")
        except IOError as e:
            logger.error(f"Error saving metadata for release_id {release_id}: {e}")
            raise ReleaseManagerError(f"Could not save metadata for {release_id}.") from e

    def initiate_release(self, song_metadata: dict, generated_song_path: str) -> str:
        """Initiates a new release process for a generated song.

        Args:
            song_metadata: Metadata of the song from SunoOrchestrator (or other source).
            generated_song_path: Path to the generated song file.

        Returns:
            The unique release_id for this release.        """
        logger.info(f"Initiating new release for song: {song_metadata.get('title')}")
        release_id = self._generate_release_id(song_metadata.get("title", "untitled"))
        
        if not os.path.exists(generated_song_path):
            logger.error(f"Generated song file not found at {generated_song_path} for release {release_id}")
            raise ReleaseManagerError(f"Generated song file missing: {generated_song_path}")

        release_data = {
            "release_id": release_id,
            "song_metadata": song_metadata,
            "original_song_path": generated_song_path,
            "status": ReleaseStatus.PENDING_PREVIEW.value,
            "history": [{
                "timestamp": datetime.now().isoformat(),
                "status": ReleaseStatus.PENDING_PREVIEW.value,
                "notes": "Release initiated."
            }],
            "preview_path": None,
            "upload_path": None
        }
        self._save_metadata(release_id, release_data)
        logger.info(f"Release {release_id} initiated. Status: {ReleaseStatus.PENDING_PREVIEW.value}")
        return release_id

    def create_preview(self, release_id: str) -> str:
        """Creates a preview version of the song.

        For now, this might just copy the file to a preview location.
        In the future, it could involve watermarking, format conversion, etc.
        """
        logger.info(f"Creating preview for release_id: {release_id}")
        metadata = self._load_metadata(release_id)
        if metadata["status"] != ReleaseStatus.PENDING_PREVIEW.value:
            logger.warning(f"Cannot create preview for {release_id}. Current status: {metadata['status']}")
            raise ReleaseManagerError(f"Release {release_id} is not in PENDING_PREVIEW state.")

        original_song_path = metadata["original_song_path"]
        # Simulate preview creation (e.g., copy to preview_dir)
        # In a real scenario, this could involve processing.
        preview_filename = os.path.basename(original_song_path)
        preview_path = os.path.join(self.preview_dir, f"preview_{release_id}_{preview_filename}")
        
        try:
            # For simplicity, copying the file. Add more complex logic if needed.
            with open(original_song_path, "rb") as f_in, open(preview_path, "wb") as f_out:
                f_out.write(f_in.read())
            logger.info(f"Preview file created at: {preview_path}")
        except IOError as e:
            logger.error(f"Failed to create preview file for {release_id} at {preview_path}: {e}")
            metadata["status"] = ReleaseStatus.FAILED.value
            metadata["history"].append({
                "timestamp": datetime.now().isoformat(),
                "status": ReleaseStatus.FAILED.value,
                "notes": f"Preview creation failed: {e}"
            })
            self._save_metadata(release_id, metadata)
            raise ReleaseManagerError(f"Preview creation failed for {release_id}.") from e

        metadata["status"] = ReleaseStatus.PREVIEW_READY.value
        metadata["preview_path"] = preview_path
        metadata["history"].append({
            "timestamp": datetime.now().isoformat(),
            "status": ReleaseStatus.PREVIEW_READY.value,
            "notes": f"Preview created and ready at {preview_path}."
        })
        self._save_metadata(release_id, metadata)
        logger.info(f"Release {release_id} status updated to: {ReleaseStatus.PREVIEW_READY.value}")
        return preview_path

    def request_approval(self, release_id: str) -> bool:
        """Marks the release as pending approval."""
        logger.info(f"Requesting approval for release_id: {release_id}")
        metadata = self._load_metadata(release_id)
        if metadata["status"] != ReleaseStatus.PREVIEW_READY.value:
            logger.warning(f"Cannot request approval for {release_id}. Current status: {metadata['status']}")
            raise ReleaseManagerError(f"Release {release_id} is not in PREVIEW_READY state.")

        metadata["status"] = ReleaseStatus.PENDING_APPROVAL.value
        metadata["history"].append({
            "timestamp": datetime.now().isoformat(),
            "status": ReleaseStatus.PENDING_APPROVAL.value,
            "notes": "Approval requested."
        })
        self._save_metadata(release_id, metadata)
        logger.info(f"Release {release_id} status updated to: {ReleaseStatus.PENDING_APPROVAL.value}")
        return True

    def process_approval(self, release_id: str, approved: bool, approver_notes: str = "") -> bool:
        """Processes the approval decision."""
        logger.info(f"Processing approval for release_id: {release_id}. Approved: {approved}")
        metadata = self._load_metadata(release_id)
        if metadata["status"] != ReleaseStatus.PENDING_APPROVAL.value:
            logger.warning(f"Cannot process approval for {release_id}. Current status: {metadata['status']}")
            raise ReleaseManagerError(f"Release {release_id} is not in PENDING_APPROVAL state.")

        if approved:
            metadata["status"] = ReleaseStatus.APPROVED.value
            notes = f"Release approved. {approver_notes}"
        else:
            metadata["status"] = ReleaseStatus.REJECTED.value
            notes = f"Release rejected. {approver_notes}"
        
        metadata["history"].append({
            "timestamp": datetime.now().isoformat(),
            "status": metadata["status"],
            "notes": notes
        })
        self._save_metadata(release_id, metadata)
        logger.info(f"Release {release_id} status updated to: {metadata['status']}. Notes: {notes}")
        return True

    def prepare_for_upload(self, release_id: str) -> str:
        """Prepares the approved song for upload.
           This might involve moving it to a final upload directory or further processing.
        """
        logger.info(f"Preparing for upload for release_id: {release_id}")
        metadata = self._load_metadata(release_id)
        if metadata["status"] != ReleaseStatus.APPROVED.value:
            logger.warning(f"Cannot prepare for upload for {release_id}. Current status: {metadata["status"]}")
            raise ReleaseManagerError(f"Release {release_id} is not in APPROVED state.")

        # Use preview path if it exists and is valid, otherwise original path
        # This assumes preview is the one that was approved.
        source_song_path = metadata.get("preview_path") or metadata["original_song_path"]
        if not source_song_path or not os.path.exists(source_song_path):
            logger.error(f"Source song path ({source_song_path}) for upload is invalid or missing for {release_id}.")
            metadata["status"] = ReleaseStatus.FAILED.value
            metadata["history"].append({
                "timestamp": datetime.now().isoformat(),
                "status": ReleaseStatus.FAILED.value,
                "notes": f"Upload preparation failed: Source song path invalid."
            })
            self._save_metadata(release_id, metadata)
            raise ReleaseManagerError(f"Upload preparation failed for {release_id}: Source song path invalid.")

        upload_filename = os.path.basename(metadata["original_song_path"]) # Use original name for consistency
        upload_path = os.path.join(self.upload_dir, f"upload_{release_id}_{upload_filename}")

        try:
            with open(source_song_path, "rb") as f_in, open(upload_path, "wb") as f_out:
                f_out.write(f_in.read())
            logger.info(f"File prepared for upload at: {upload_path}")
        except IOError as e:
            logger.error(f"Failed to prepare file for upload for {release_id} at {upload_path}: {e}")
            metadata["status"] = ReleaseStatus.FAILED.value
            metadata["history"].append({
                "timestamp": datetime.now().isoformat(),
                "status": ReleaseStatus.FAILED.value,
                "notes": f"Upload preparation (file copy) failed: {e}"
            })
            self._save_metadata(release_id, metadata)
            raise ReleaseManagerError(f"Upload preparation failed for {release_id}.") from e

        metadata["status"] = ReleaseStatus.PENDING_UPLOAD.value
        metadata["upload_path"] = upload_path
        metadata["history"].append({
            "timestamp": datetime.now().isoformat(),
            "status": ReleaseStatus.PENDING_UPLOAD.value,
            "notes": f"File ready for upload at {upload_path}."
        })
        self._save_metadata(release_id, metadata)
        logger.info(f"Release {release_id} status updated to: {ReleaseStatus.PENDING_UPLOAD.value}")
        return upload_path

    def finalize_upload(self, release_id: str, upload_details: dict) -> bool:
        """Marks the release as uploaded and stores upload details."""
        logger.info(f"Finalizing upload for release_id: {release_id}")
        metadata = self._load_metadata(release_id)
        if metadata["status"] != ReleaseStatus.PENDING_UPLOAD.value:
            logger.warning(f"Cannot finalize upload for {release_id}. Current status: {metadata[	"status	"]}")
            raise ReleaseManagerError(f"Release {release_id} is not in PENDING_UPLOAD state.")

        metadata["status"] = ReleaseStatus.UPLOADED.value
        metadata["upload_details"] = upload_details # e.g., URL, platform_id
        metadata["history"].append({
            "timestamp": datetime.now().isoformat(),
            "status": ReleaseStatus.UPLOADED.value,
            "notes": f"Upload finalized. Details: {upload_details}"
        })
        self._save_metadata(release_id, metadata)
        logger.info(f"Release {release_id} status updated to: {ReleaseStatus.UPLOADED.value}")
        return True

    def get_release_status(self, release_id: str) -> dict:
        """Gets the current status and details of a release."""
        logger.debug(f"Getting status for release_id: {release_id}")
        return self._load_metadata(release_id)

# Example Usage (for testing or direct script execution)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Create dummy config and directories for testing
    test_config = {
        "release_metadata_dir": "./test_release_metadata",
        "preview_dir": "./test_previews",
        "upload_dir": "./test_upload_ready"
    }
    os.makedirs(test_config["release_metadata_dir"], exist_ok=True)
    os.makedirs(test_config["preview_dir"], exist_ok=True)
    os.makedirs(test_config["upload_dir"], exist_ok=True)

    # Create a dummy song file
    dummy_song_content = b"This is a dummy MP3 file content."
    dummy_song_filename = "dummy_song_for_release.mp3"
    with open(dummy_song_filename, "wb") as f:
        f.write(dummy_song_content)

    manager = ReleaseManager(config=test_config)

    song_meta = {
        "title": "My Awesome Test Song",
        "artist": "AI Release Bot",
        "genre": "Test Pop",
        "suno_song_id": "test_suno_123"
    }

    try:
        # 1. Initiate Release
        release1_id = manager.initiate_release(song_meta, dummy_song_filename)
        print(f"Initiated release: {release1_id}")
        print(f"Status: {manager.get_release_status(release1_id)[	"status	"]}")

        # 2. Create Preview
        preview1_path = manager.create_preview(release1_id)
        print(f"Preview created at: {preview1_path}")
        print(f"Status: {manager.get_release_status(release1_id)[	"status	"]}")

        # 3. Request Approval
        manager.request_approval(release1_id)
        print(f"Approval requested for {release1_id}")
        print(f"Status: {manager.get_release_status(release1_id)[	"status	"]}")

        # 4. Process Approval (Approve)
        manager.process_approval(release1_id, approved=True, approver_notes="Looks great!")
        print(f"Release {release1_id} approved.")
        print(f"Status: {manager.get_release_status(release1_id)[	"status	"]}")

        # 5. Prepare for Upload
        upload1_path = manager.prepare_for_upload(release1_id)
        print(f"File prepared for upload at: {upload1_path}")
        print(f"Status: {manager.get_release_status(release1_id)[	"status	"]}")

        # 6. Finalize Upload
        upload_info = {"platform": "TestMusicService", "url": "http://example.com/song/test123"}
        manager.finalize_upload(release1_id, upload_info)
        print(f"Upload finalized for {release1_id}.")
        print(f"Status: {manager.get_release_status(release1_id)[	"status	"]}")
        print(f"Final metadata: {json.dumps(manager.get_release_status(release1_id), indent=2)}")

        # Example of a rejected release
        release2_id = manager.initiate_release({"title": "Rejected Song"}, dummy_song_filename)
        manager.create_preview(release2_id)
        manager.request_approval(release2_id)
        manager.process_approval(release2_id, approved=False, approver_notes="Needs more cowbell.")
        print(f"Release {release2_id} rejected. Status: {manager.get_release_status(release2_id)[	"status	"]}")

    except ReleaseManagerError as e:
        print(f"Release Manager Error: {e}")
    finally:
        # Clean up dummy files and dirs
        if os.path.exists(dummy_song_filename): os.remove(dummy_song_filename)
        # Add more cleanup for test directories if needed, e.g., shutil.rmtree
        print("Test finished. Manual cleanup of test directories might be needed.")


