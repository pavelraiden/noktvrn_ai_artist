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
        self.config = config
        self.release_metadata_dir = config.get(
            "release_metadata_dir", "./release_metadata"
        )
        self.preview_dir = config.get("preview_dir", "./preview")
        self.upload_dir = config.get("upload_dir", "./upload_ready")

        os.makedirs(self.release_metadata_dir, exist_ok=True)
        os.makedirs(self.preview_dir, exist_ok=True)
        os.makedirs(self.upload_dir, exist_ok=True)

        logger.info("Release directories ensured.")

    def _get_metadata_path(self, release_id: str) -> str:
        return os.path.join(self.release_metadata_dir, f"{release_id}.json")

    def _load_metadata(self, release_id: str) -> dict:
        path = self._get_metadata_path(release_id)
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ReleaseManagerError(
                f"Failed to load metadata for release_id '{release_id}'"
            ) from e

    def _save_metadata(self, release_id: str, metadata: dict):
        path = self._get_metadata_path(release_id)
        metadata["last_updated"] = datetime.now().isoformat()
        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)

    def _update_status(self, release_id: str, status: ReleaseStatus):
        metadata = self._load_metadata(release_id)
        metadata["status"] = status.value
        self._save_metadata(release_id, metadata)

    def get_release_status(self, release_id: str) -> str:
        metadata = self._load_metadata(release_id)
        return metadata.get("status", "unknown")

    def initiate_release(
        self, song_meta: dict, dummy_song_filename: str
    ) -> str:
        release_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        metadata = {
            "release_id": release_id,
            "created_at": datetime.utcnow().isoformat(),
            "song_meta": song_meta,
            "status": ReleaseStatus.PENDING_PREVIEW.value,
        }
        self._save_metadata(release_id, metadata)
        logger.info(f"Release initiated with ID: {release_id}")

        song_path = os.path.join(self.preview_dir, dummy_song_filename)
        with open(song_path, "w") as f:
            f.write("This is a dummy MP3 file for preview.")

        return release_id

    def create_preview(self, release_id: str) -> str:
        self._update_status(release_id, ReleaseStatus.PREVIEW_READY)
        return os.path.join(self.preview_dir, f"{release_id}_preview.mp3")

    def request_approval(
        self, release_id: str, approved: bool = True, notes: str = ""
    ):
        new_status = (
            ReleaseStatus.APPROVED if approved else ReleaseStatus.REJECTED
        )
        self._update_status(release_id, new_status)

    def prepare_for_upload(self, release_id: str) -> str:
        self._update_status(release_id, ReleaseStatus.PENDING_UPLOAD)
        return os.path.join(self.upload_dir, f"{release_id}_upload.mp3")

    def finalize_upload(self, release_id: str) -> dict:
        self._update_status(release_id, ReleaseStatus.UPLOADED)
        return {
            "platform": "TestMusicService",
            "url": f"http://example.com/song/{release_id}",
            "status": "success",
        }
