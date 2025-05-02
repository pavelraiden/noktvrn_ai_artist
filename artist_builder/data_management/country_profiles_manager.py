"""
Country Profiles Manager Module

This module provides an interface for managing and accessing country-specific
music consumption data stored in the Country Profiles Database.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple, Any


class CountryProfilesManager:
    """
    Class for managing the Country Profiles Database.
    Assumes a JSON file-based storage structure.
    """

    def __init__(self, data_dir: str = "/home/ubuntu/country_profiles_data"):
        """
        Initialize with the base data directory.

        Args:
            data_dir (str): Path to the root directory of the country profiles data.
        """
        self.data_dir = data_dir
        self._ensure_base_dirs_exist()

    def _ensure_base_dirs_exist(self):
        """Ensure base directories for data storage exist."""
        for subdir in [
            "countries",
            "daily_profiles",
            "genre_trends",
            "audience_trends",
            "historical_aggregates",
        ]:
            os.makedirs(os.path.join(self.data_dir, subdir), exist_ok=True)

    def _get_profile_path(
        self, country_code: str, date: Optional[str] = None, period: str = "daily"
    ) -> str:
        """Construct the path for a country profile file."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        if period == "daily":
            return os.path.join(
                self.data_dir, "daily_profiles", date, f"{country_code}.json"
            )
        # Add logic for weekly/monthly if needed
        else:
            raise ValueError(f"Unsupported period: {period}")

    def _get_genre_trend_path(
        self,
        country_code: str,
        genre: str,
        date: Optional[str] = None,
        period: str = "daily",
    ) -> str:
        """Construct the path for a genre trend file."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        genre_slug = genre.lower().replace(" ", "-")

        if period == "daily":
            return os.path.join(
                self.data_dir, "genre_trends", date, f"{country_code}-{genre_slug}.json"
            )
        # Add logic for weekly/monthly if needed
        else:
            raise ValueError(f"Unsupported period: {period}")

    def _get_audience_trend_path(
        self,
        country_code: str,
        cluster: str,
        date: Optional[str] = None,
        period: str = "daily",
    ) -> str:
        """Construct the path for an audience cluster trend file."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        cluster_slug = cluster.lower().replace(" ", "-")

        if period == "daily":
            return os.path.join(
                self.data_dir,
                "audience_trends",
                date,
                f"{country_code}-{cluster_slug}.json",
            )
        # Add logic for weekly/monthly if needed
        else:
            raise ValueError(f"Unsupported period: {period}")

    def _get_historical_aggregate_path(
        self, country_code: str, period_type: str, end_date: Optional[str] = None
    ) -> str:
        """Construct the path for a historical aggregate file."""
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        return os.path.join(
            self.data_dir,
            "historical_aggregates",
            country_code,
            period_type,
            f"{end_date}.json",
        )

    def _read_json(self, file_path: str) -> Optional[Dict]:
        """Read data from a JSON file."""
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading JSON file {file_path}: {str(e)}")
            return None

    def _write_json(self, file_path: str, data: Dict) -> bool:
        """Write data to a JSON file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error writing JSON file {file_path}: {str(e)}")
            return False

    def get_country_info(self, country_code: str) -> Optional[Dict]:
        """Get static information for a specific country."""
        file_path = os.path.join(self.data_dir, "countries", f"{country_code}.json")
        return self._read_json(file_path)

    def update_country_info(self, country_code: str, data: Dict) -> bool:
        """Add or update static country information."""
        file_path = os.path.join(self.data_dir, "countries", f"{country_code}.json")
        return self._write_json(file_path, data)

    def get_country_profile(
        self, country_code: str, date: Optional[str] = None, period: str = "daily"
    ) -> Optional[Dict]:
        """Get a country profile for the specified country and date (or most recent if date is None)."""
        file_path = self._get_profile_path(country_code, date, period)
        return self._read_json(file_path)

    def update_country_profile(
        self, country_code: str, date: str, data: Dict, period: str = "daily"
    ) -> bool:
        """Add or update a country profile."""
        file_path = self._get_profile_path(country_code, date, period)
        # Add metadata to data
        data["country_code"] = country_code
        data["timestamp"] = (
            date + "T00:00:00Z"
        )  # Assuming daily profiles are for the start of the day
        data["period"] = period
        return self._write_json(file_path, data)

    def get_genre_trends(
        self,
        country_code: str,
        genre: Optional[str] = None,
        date: Optional[str] = None,
        period: str = "daily",
    ) -> Union[Dict, List[Dict], None]:
        """Get genre trends for the specified country, genre, date, and period type."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        if genre:
            # Get specific genre trend
            file_path = self._get_genre_trend_path(country_code, genre, date, period)
            return self._read_json(file_path)
        else:
            # Get all genre trends for the country and date
            trends = []
            genre_dir = os.path.join(self.data_dir, "genre_trends", date)
            if not os.path.isdir(genre_dir):
                return []

            prefix = f"{country_code}-"
            for filename in os.listdir(genre_dir):
                if filename.startswith(prefix) and filename.endswith(".json"):
                    file_path = os.path.join(genre_dir, filename)
                    trend_data = self._read_json(file_path)
                    if trend_data:
                        trends.append(trend_data)
            return trends

    def update_genre_trend(
        self,
        country_code: str,
        genre: str,
        date: str,
        data: Dict,
        period: str = "daily",
    ) -> bool:
        """Add or update a genre trend."""
        file_path = self._get_genre_trend_path(country_code, genre, date, period)
        # Add metadata to data
        data["country_code"] = country_code
        data["genre"] = genre
        data["date"] = date
        data["period"] = period
        return self._write_json(file_path, data)

    def get_audience_trends(
        self,
        country_code: str,
        cluster: Optional[str] = None,
        date: Optional[str] = None,
        period: str = "daily",
    ) -> Union[Dict, List[Dict], None]:
        """Get audience cluster trends for the specified country, cluster, and date."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        if cluster:
            # Get specific cluster trend
            file_path = self._get_audience_trend_path(
                country_code, cluster, date, period
            )
            return self._read_json(file_path)
        else:
            # Get all cluster trends for the country and date
            trends = []
            cluster_dir = os.path.join(self.data_dir, "audience_trends", date)
            if not os.path.isdir(cluster_dir):
                return []

            prefix = f"{country_code}-"
            for filename in os.listdir(cluster_dir):
                if filename.startswith(prefix) and filename.endswith(".json"):
                    file_path = os.path.join(cluster_dir, filename)
                    trend_data = self._read_json(file_path)
                    if trend_data:
                        trends.append(trend_data)
            return trends

    def update_audience_trend(
        self,
        country_code: str,
        cluster: str,
        date: str,
        data: Dict,
        period: str = "daily",
    ) -> bool:
        """Add or update an audience cluster trend."""
        file_path = self._get_audience_trend_path(country_code, cluster, date, period)
        # Add metadata to data
        data["country_code"] = country_code
        data["cluster_name"] = cluster
        data["date"] = date
        data["period"] = period
        return self._write_json(file_path, data)

    def get_historical_aggregate(
        self, country_code: str, period_type: str, end_date: Optional[str] = None
    ) -> Optional[Dict]:
        """Get historical aggregate for the specified country, period type, and end date."""
        file_path = self._get_historical_aggregate_path(
            country_code, period_type, end_date
        )
        return self._read_json(file_path)

    def update_historical_aggregate(
        self, country_code: str, period_type: str, end_date: str, data: Dict
    ) -> bool:
        """Add or update a historical aggregate."""
        file_path = self._get_historical_aggregate_path(
            country_code, period_type, end_date
        )
        # Add metadata to data
        data["country_code"] = country_code
        data["period_type"] = period_type
        data["end_date"] = end_date
        # Calculate start_date based on period_type and end_date
        try:
            end = datetime.fromisoformat(end_date)
            if period_type == "1day":
                start = end - timedelta(days=0)
            elif period_type == "3day":
                start = end - timedelta(days=2)
            elif period_type == "7day":
                start = end - timedelta(days=6)
            elif period_type == "14day":
                start = end - timedelta(days=13)
            elif period_type == "30day":
                start = end - timedelta(days=29)
            elif period_type == "60day":
                start = end - timedelta(days=59)
            else:
                raise ValueError("Invalid period_type")
            data["start_date"] = start.strftime("%Y-%m-%d") + "T00:00:00Z"
            data["end_date"] = end_date + "T23:59:59Z"
        except ValueError as e:
            print(f"Error calculating start date: {e}")
            return False

        return self._write_json(file_path, data)

    def compare_countries(
        self,
        country_codes: List[str],
        metrics: List[str],
        date: Optional[str] = None,
        period: str = "daily",
    ) -> Dict:
        """Compare specified metrics across multiple countries."""
        comparison = {}
        for country_code in country_codes:
            profile = self.get_country_profile(country_code, date, period)
            if profile:
                country_data = {}
                for metric in metrics:
                    # Simple dot notation access (e.g., "streaming_stats.total_streams")
                    value = profile
                    try:
                        for key in metric.split("."):
                            value = value[key]
                        country_data[metric] = value
                    except KeyError:
                        country_data[metric] = None
                comparison[country_code] = country_data
            else:
                comparison[country_code] = {metric: None for metric in metrics}
        return comparison

    def track_trend_evolution(
        self,
        country_code: str,
        trend_type: str,
        trend_name: str,
        start_date: str,
        end_date: str,
        period: str = "daily",
    ) -> List[Dict]:
        """Track the evolution of a specific trend over time."""
        evolution = []
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            print("Invalid date format. Use ISO format (YYYY-MM-DD).")
            return []

        current_date = start
        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            data_point = None

            if trend_type == "genre":
                data_point = self.get_genre_trends(
                    country_code, trend_name, date_str, period
                )
            elif trend_type == "audience":
                data_point = self.get_audience_trends(
                    country_code, trend_name, date_str, period
                )
            # Add more trend types if needed

            if data_point:
                evolution.append({"date": date_str, "data": data_point})

            # Increment date
            current_date += timedelta(days=1)  # Assuming daily for now

        return evolution
