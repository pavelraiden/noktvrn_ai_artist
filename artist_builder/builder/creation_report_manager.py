"""
Creation Report Manager Module for Artist Profile Builder

This module handles the generation and storage of creation reports
for artist profiles, providing detailed information about the creation process.
"""

import logging
import json
import os
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.creation_report_manager")


class CreationReportManager:
    """
    Manages the generation and storage of creation reports for artist profiles.
    """

    def __init__(self, reports_dir: Optional[str] = None):
        """
        Initialize the creation report manager.

        Args:
            reports_dir: Optional path to the reports directory. If not provided,
                        defaults to /creation_reports in the project root.
        """
        # Set default reports directory if not provided
        if reports_dir is None:
            # Get the project root directory (two levels up from this file)
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            reports_dir = os.path.join(project_root, "creation_reports")

        self.reports_dir = reports_dir

        # Ensure reports directory exists
        self._ensure_reports_directory()

        logger.info(
            f"Initialized CreationReportManager with reports directory: {self.reports_dir}"
        )

    def _ensure_reports_directory(self) -> None:
        """Ensure the reports directory exists, creating it if necessary."""
        try:
            os.makedirs(self.reports_dir, exist_ok=True)
            logger.info(f"Ensured reports directory exists: {self.reports_dir}")
        except Exception as e:
            logger.error(f"Error creating reports directory: {e}")
            # Continue without file storage if directory creation fails

    def generate_creation_report(
        self, profile: Dict[str, Any], validation_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a creation report for an artist profile.

        Args:
            profile: The artist profile
            validation_report: Validation report for the profile

        Returns:
            Dictionary containing the creation report
        """
        # Extract key information from profile
        artist_id = profile.get("artist_id", str(uuid.uuid4()))
        stage_name = profile.get("stage_name", "Unknown Artist")

        # Create report
        creation_report = {
            "artist_id": artist_id,
            "artist_name": stage_name,
            "timestamp": datetime.now().isoformat(),
            "validation_status": (
                "valid"
                if validation_report.get("is_valid", False)
                else "issues_corrected"
            ),
            "validation_details": {
                "is_valid": validation_report.get("is_valid", False),
                "errors": validation_report.get("errors", []),
                "warnings": validation_report.get("warnings", []),
            },
            "auto_generated_defaults": self._extract_auto_generated_fields(
                profile, validation_report
            ),
            "profile_summary": {
                "genre": profile.get("genre", "Unknown"),
                "subgenres": profile.get("subgenres", []),
                "creation_method": profile.get("creation_method", "standard"),
                "total_fields": len(profile),
            },
        }

        logger.info(f"Generated creation report for artist {stage_name} ({artist_id})")
        return creation_report

    def _extract_auto_generated_fields(
        self, profile: Dict[str, Any], validation_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract information about auto-generated fields.

        Args:
            profile: The artist profile
            validation_report: Validation report for the profile

        Returns:
            Dictionary containing information about auto-generated fields
        """
        auto_generated = {}

        # Extract from validation report
        if "auto_generated" in validation_report:
            auto_generated = validation_report["auto_generated"]
        else:
            # Try to extract from profile metadata
            if "metadata" in profile and "auto_generated_fields" in profile["metadata"]:
                auto_generated = profile["metadata"]["auto_generated_fields"]

        return auto_generated

    def save_creation_report(self, report: Dict[str, Any]) -> str:
        """
        Save a creation report to file.

        Args:
            report: The creation report to save

        Returns:
            Path to the saved report file
        """
        # Get artist ID and name
        artist_id = report.get("artist_id", str(uuid.uuid4()))
        artist_name = report.get("artist_name", "Unknown").replace(" ", "_")

        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{artist_name}_{artist_id}_{timestamp}_creation_report.json"
        file_path = os.path.join(self.reports_dir, filename)

        # Save report
        try:
            with open(file_path, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"Saved creation report to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving creation report: {e}")
            raise

    def get_creation_report(self, artist_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent creation report for an artist.

        Args:
            artist_id: ID of the artist

        Returns:
            Dictionary containing the creation report, or None if not found
        """
        try:
            # List all report files
            report_files = [
                f
                for f in os.listdir(self.reports_dir)
                if f.endswith("_creation_report.json")
            ]

            # Filter by artist ID
            artist_reports = [f for f in report_files if artist_id in f]

            if not artist_reports:
                logger.warning(f"No creation reports found for artist {artist_id}")
                return None

            # Sort by timestamp (newest first)
            sorted_reports = sorted(artist_reports, reverse=True)
            latest_report_file = sorted_reports[0]

            # Load report
            with open(os.path.join(self.reports_dir, latest_report_file), "r") as f:
                report = json.load(f)

            logger.info(f"Retrieved creation report for artist {artist_id}")
            return report
        except Exception as e:
            logger.error(f"Error retrieving creation report: {e}")
            return None

    def list_creation_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List the most recent creation reports.

        Args:
            limit: Maximum number of reports to retrieve

        Returns:
            List of dictionaries containing creation reports
        """
        try:
            # List all report files
            report_files = [
                f
                for f in os.listdir(self.reports_dir)
                if f.endswith("_creation_report.json")
            ]

            if not report_files:
                logger.warning("No creation reports found")
                return []

            # Sort by timestamp (newest first)
            sorted_reports = sorted(report_files, reverse=True)
            latest_reports = sorted_reports[:limit]

            # Load reports
            reports = []
            for report_file in latest_reports:
                with open(os.path.join(self.reports_dir, report_file), "r") as f:
                    report = json.load(f)
                reports.append(report)

            logger.info(f"Retrieved {len(reports)} creation reports")
            return reports
        except Exception as e:
            logger.error(f"Error listing creation reports: {e}")
            return []

    def delete_creation_report(self, artist_id: str) -> bool:
        """
        Delete all creation reports for an artist.

        Args:
            artist_id: ID of the artist

        Returns:
            Boolean indicating success
        """
        try:
            # List all report files
            report_files = [
                f
                for f in os.listdir(self.reports_dir)
                if f.endswith("_creation_report.json")
            ]

            # Filter by artist ID
            artist_reports = [f for f in report_files if artist_id in f]

            if not artist_reports:
                logger.warning(f"No creation reports found for artist {artist_id}")
                return False

            # Delete reports
            for report_file in artist_reports:
                os.remove(os.path.join(self.reports_dir, report_file))

            logger.info(
                f"Deleted {len(artist_reports)} creation reports for artist {artist_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting creation reports: {e}")
            return False
