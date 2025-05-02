"""
Expanded Artist Analytics Module

This module provides comprehensive analytics for AI artists, including
trend analysis, performance metrics, evolution tracking, and audience insights.
"""

import logging
import json
import os
import time
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta
import uuid
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import Counter

from ..trend_analyzer import TrendAnalyzer
from ..llm_metrics import LLMMetrics
from ..llm_collaboration import LLMCollaboration

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.artist_analytics")


class ArtistAnalyticsError(Exception):
    """Exception raised for errors in the artist analytics system."""

    pass


class ArtistAnalytics:
    """
    Comprehensive analytics for AI artists.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the artist analytics system.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Initialize components
        self.trend_analyzer = TrendAnalyzer(self.config.get("trend_analyzer_config"))
        self.llm_metrics = LLMMetrics(self.config.get("llm_metrics_config"))
        self.llm_collaboration = LLMCollaboration(
            self.config.get("llm_collaboration_config")
        )

        # Set up base directories
        self.artists_dir = self.config.get("artists_dir", "artists")
        self.analytics_dir = self.config.get("analytics_dir", "analytics")

        os.makedirs(self.artists_dir, exist_ok=True)
        os.makedirs(self.analytics_dir, exist_ok=True)

        logger.info("Initialized expanded artist analytics system")

    def generate_artist_analytics_report(
        self,
        artist_slug: str,
        report_type: str = "comprehensive",
        time_period: str = "all",
        output_format: str = "json",
        save_report: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive analytics report for an artist.

        Args:
            artist_slug: Slug of the artist
            report_type: Type of report ('comprehensive', 'trend', 'performance', 'evolution', 'audience')
            time_period: Time period for the report ('all', 'last_week', 'last_month', 'last_year')
            output_format: Format of the report ('json', 'html', 'markdown')
            save_report: Whether to save the report to disk

        Returns:
            Dictionary containing the analytics report
        """
        try:
            logger.info(
                f"Generating {report_type} analytics report for artist: {artist_slug}"
            )

            # Load artist profile
            profile = self._load_artist_profile(artist_slug)

            # Determine date range based on time period
            date_range = self._get_date_range(time_period)

            # Initialize report
            report = {
                "artist_slug": artist_slug,
                "artist_name": profile.get("name", artist_slug),
                "report_type": report_type,
                "time_period": time_period,
                "generated_at": datetime.now().isoformat(),
                "date_range": {
                    "start": date_range[0].isoformat() if date_range[0] else None,
                    "end": date_range[1].isoformat() if date_range[1] else None,
                },
            }

            # Generate report sections based on report type
            if report_type == "comprehensive" or report_type == "trend":
                report["trend_analysis"] = self._generate_trend_analysis(
                    profile, date_range
                )

            if report_type == "comprehensive" or report_type == "performance":
                report["performance_metrics"] = self._generate_performance_metrics(
                    artist_slug, date_range
                )

            if report_type == "comprehensive" or report_type == "evolution":
                report["evolution_tracking"] = self._generate_evolution_tracking(
                    artist_slug, profile, date_range
                )

            if report_type == "comprehensive" or report_type == "audience":
                report["audience_insights"] = self._generate_audience_insights(
                    profile, date_range
                )

            if report_type == "comprehensive":
                report["recommendations"] = self._generate_recommendations(
                    profile,
                    report["trend_analysis"],
                    report["performance_metrics"],
                    report["evolution_tracking"],
                    report["audience_insights"],
                )

            # Generate visualizations if needed
            if output_format in ["html", "markdown"]:
                report["visualizations"] = self._generate_visualizations(
                    artist_slug, profile, report, output_format
                )

            # Format report based on output format
            formatted_report = self._format_report(report, output_format)

            # Save report if requested
            if save_report:
                save_path = self._save_report(
                    artist_slug, formatted_report, report_type, output_format
                )
                report["save_path"] = save_path

            logger.info(
                f"Successfully generated analytics report for artist: {artist_slug}"
            )
            return report

        except Exception as e:
            logger.error(
                f"Error generating analytics report for artist {artist_slug}: {str(e)}"
            )
            raise ArtistAnalyticsError(f"Failed to generate analytics report: {str(e)}")

    def compare_artists(
        self,
        artist_slugs: List[str],
        comparison_aspects: Optional[List[str]] = None,
        output_format: str = "json",
        save_report: bool = True,
    ) -> Dict[str, Any]:
        """
        Compare multiple artists across various aspects.

        Args:
            artist_slugs: List of artist slugs to compare
            comparison_aspects: Optional list of specific aspects to compare
            output_format: Format of the report ('json', 'html', 'markdown')
            save_report: Whether to save the report to disk

        Returns:
            Dictionary containing the comparison report
        """
        try:
            if not artist_slugs or len(artist_slugs) < 2:
                raise ArtistAnalyticsError(
                    "At least two artists are required for comparison"
                )

            logger.info(f"Comparing artists: {', '.join(artist_slugs)}")

            # Default comparison aspects if not specified
            if not comparison_aspects:
                comparison_aspects = [
                    "genre",
                    "style",
                    "trends",
                    "performance",
                    "evolution",
                    "audience",
                ]

            # Load artist profiles
            artist_profiles = {}
            for slug in artist_slugs:
                artist_profiles[slug] = self._load_artist_profile(slug)

            # Initialize comparison report
            report = {
                "artist_slugs": artist_slugs,
                "artist_names": {
                    slug: profile.get("name", slug)
                    for slug, profile in artist_profiles.items()
                },
                "comparison_aspects": comparison_aspects,
                "generated_at": datetime.now().isoformat(),
            }

            # Generate comparison for each aspect
            for aspect in comparison_aspects:
                if aspect == "genre":
                    report["genre_comparison"] = self._compare_genres(artist_profiles)

                elif aspect == "style":
                    report["style_comparison"] = self._compare_styles(artist_profiles)

                elif aspect == "trends":
                    report["trend_comparison"] = self._compare_trends(artist_profiles)

                elif aspect == "performance":
                    report["performance_comparison"] = self._compare_performance(
                        artist_slugs
                    )

                elif aspect == "evolution":
                    report["evolution_comparison"] = self._compare_evolution(
                        artist_slugs, artist_profiles
                    )

                elif aspect == "audience":
                    report["audience_comparison"] = self._compare_audience(
                        artist_profiles
                    )

            # Generate overall comparison summary
            report["comparison_summary"] = self._generate_comparison_summary(report)

            # Generate visualizations if needed
            if output_format in ["html", "markdown"]:
                report["visualizations"] = self._generate_comparison_visualizations(
                    artist_slugs, artist_profiles, report, output_format
                )

            # Format report based on output format
            formatted_report = self._format_report(report, output_format)

            # Save report if requested
            if save_report:
                save_path = self._save_comparison_report(
                    artist_slugs, formatted_report, output_format
                )
                report["save_path"] = save_path

            logger.info(
                f"Successfully generated comparison report for artists: {', '.join(artist_slugs)}"
            )
            return report

        except Exception as e:
            logger.error(f"Error comparing artists {', '.join(artist_slugs)}: {str(e)}")
            raise ArtistAnalyticsError(f"Failed to compare artists: {str(e)}")

    def track_artist_evolution(
        self,
        artist_slug: str,
        track_period: str = "all",
        include_metrics: bool = True,
        include_trends: bool = True,
        output_format: str = "json",
        save_report: bool = True,
    ) -> Dict[str, Any]:
        """
        Track the evolution of an artist over time.

        Args:
            artist_slug: Slug of the artist
            track_period: Time period for tracking ('all', 'last_week', 'last_month', 'last_year')
            include_metrics: Whether to include performance metrics
            include_trends: Whether to include trend analysis
            output_format: Format of the report ('json', 'html', 'markdown')
            save_report: Whether to save the report to disk

        Returns:
            Dictionary containing the evolution tracking report
        """
        try:
            logger.info(f"Tracking evolution for artist: {artist_slug}")

            # Load artist profile
            profile = self._load_artist_profile(artist_slug)

            # Determine date range based on track period
            date_range = self._get_date_range(track_period)

            # Get version history
            version_history = self._get_artist_version_history(artist_slug)

            # Filter version history by date range
            if date_range[0]:
                version_history = [
                    v
                    for v in version_history
                    if datetime.fromisoformat(v["date"]) >= date_range[0]
                ]

            if date_range[1]:
                version_history = [
                    v
                    for v in version_history
                    if datetime.fromisoformat(v["date"]) <= date_range[1]
                ]

            # Initialize tracking report
            report = {
                "artist_slug": artist_slug,
                "artist_name": profile.get("name", artist_slug),
                "track_period": track_period,
                "generated_at": datetime.now().isoformat(),
                "date_range": {
                    "start": date_range[0].isoformat() if date_range[0] else None,
                    "end": date_range[1].isoformat() if date_range[1] else None,
                },
                "version_history": version_history,
                "evolution_timeline": self._generate_evolution_timeline(
                    artist_slug, version_history
                ),
            }

            # Include metrics if requested
            if include_metrics:
                report["performance_metrics"] = self._generate_performance_metrics(
                    artist_slug, date_range
                )

            # Include trends if requested
            if include_trends:
                report["trend_analysis"] = self._generate_trend_analysis(
                    profile, date_range
                )
                report["trend_alignment"] = self._analyze_trend_alignment(
                    artist_slug, version_history
                )

            # Generate evolution insights
            report["evolution_insights"] = self._generate_evolution_insights(
                artist_slug,
                profile,
                version_history,
                report.get("trend_analysis", {}),
                report.get("performance_metrics", {}),
            )

            # Generate visualizations if needed
            if output_format in ["html", "markdown"]:
                report["visualizations"] = self._generate_evolution_visualizations(
                    artist_slug, profile, report, output_format
                )

            # Format report based on output format
            formatted_report = self._format_report(report, output_format)

            # Save report if requested
            if save_report:
                save_path = self._save_evolution_report(
                    artist_slug, formatted_report, output_format
                )
                report["save_path"] = save_path

            logger.info(f"Successfully tracked evolution for artist: {artist_slug}")
            return report

        except Exception as e:
            logger.error(f"Error tracking evolution for artist {artist_slug}: {str(e)}")
            raise ArtistAnalyticsError(f"Failed to track artist evolution: {str(e)}")

    def analyze_trend_compatibility(
        self,
        artist_slug: str,
        trend_categories: Optional[List[str]] = None,
        output_format: str = "json",
        save_report: bool = True,
    ) -> Dict[str, Any]:
        """
        Analyze the compatibility of an artist with current trends.

        Args:
            artist_slug: Slug of the artist
            trend_categories: Optional list of specific trend categories to analyze
            output_format: Format of the report ('json', 'html', 'markdown')
            save_report: Whether to save the report to disk

        Returns:
            Dictionary containing the trend compatibility report
        """
        try:
            logger.info(f"Analyzing trend compatibility for artist: {artist_slug}")

            # Load artist profile
            profile = self._load_artist_profile(artist_slug)

            # Default trend categories if not specified
            if not trend_categories:
                trend_categories = [
                    "genre",
                    "style",
                    "production",
                    "visual",
                    "lyrical",
                    "marketing",
                ]

            # Get current trends
            main_genre = profile.get("genre", {}).get("main", "")
            subgenres = profile.get("genre", {}).get("subgenres", [])
            style_tags = profile.get("style_tags", [])

            current_trends = self.trend_analyzer.analyze_trends(
                main_genre=main_genre, subgenres=subgenres, style_tags=style_tags
            )

            # Analyze compatibility with current trends
            compatibility = self.trend_analyzer.analyze_artist_compatibility(
                artist_profile=profile, trend_data=current_trends
            )

            # Initialize compatibility report
            report = {
                "artist_slug": artist_slug,
                "artist_name": profile.get("name", artist_slug),
                "trend_categories": trend_categories,
                "generated_at": datetime.now().isoformat(),
                "current_trends": current_trends,
                "overall_compatibility": compatibility.get("overall_score", 0),
                "category_compatibility": {},
            }

            # Extract compatibility scores for each category
            aspect_scores = compatibility.get("aspect_scores", {})
            for category in trend_categories:
                if category in aspect_scores:
                    report["category_compatibility"][category] = aspect_scores[category]
                else:
                    report["category_compatibility"][category] = 0

            # Generate detailed compatibility analysis for each category
            report["detailed_analysis"] = {}
            for category in trend_categories:
                report["detailed_analysis"][category] = (
                    self._analyze_category_compatibility(
                        profile, current_trends, category
                    )
                )

            # Generate recommendations based on compatibility
            report["trend_recommendations"] = self._generate_trend_recommendations(
                profile, current_trends, compatibility
            )

            # Generate visualizations if needed
            if output_format in ["html", "markdown"]:
                report["visualizations"] = self._generate_compatibility_visualizations(
                    artist_slug, profile, report, output_format
                )

            # Format report based on output format
            formatted_report = self._format_report(report, output_format)

            # Save report if requested
            if save_report:
                save_path = self._save_compatibility_report(
                    artist_slug, formatted_report, output_format
                )
                report["save_path"] = save_path

            logger.info(
                f"Successfully analyzed trend compatibility for artist: {artist_slug}"
            )
            return report

        except Exception as e:
            logger.error(
                f"Error analyzing trend compatibility for artist {artist_slug}: {str(e)}"
            )
            raise ArtistAnalyticsError(
                f"Failed to analyze trend compatibility: {str(e)}"
            )

    def generate_artist_dashboard(
        self,
        artist_slug: str,
        dashboard_sections: Optional[List[str]] = None,
        time_period: str = "last_month",
        output_format: str = "html",
        save_dashboard: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive dashboard for an artist.

        Args:
            artist_slug: Slug of the artist
            dashboard_sections: Optional list of specific sections to include
            time_period: Time period for the dashboard ('all', 'last_week', 'last_month', 'last_year')
            output_format: Format of the dashboard ('html', 'markdown')
            save_dashboard: Whether to save the dashboard to disk

        Returns:
            Dictionary containing the dashboard data and path
        """
        try:
            logger.info(f"Generating dashboard for artist: {artist_slug}")

            # Load artist profile
            profile = self._load_artist_profile(artist_slug)

            # Default dashboard sections if not specified
            if not dashboard_sections:
                dashboard_sections = [
                    "overview",
                    "trends",
                    "performance",
                    "evolution",
                    "audience",
                    "recommendations",
                ]

            # Determine date range based on time period
            date_range = self._get_date_range(time_period)

            # Initialize dashboard
            dashboard = {
                "artist_slug": artist_slug,
                "artist_name": profile.get("name", artist_slug),
                "dashboard_sections": dashboard_sections,
                "time_period": time_period,
                "generated_at": datetime.now().isoformat(),
                "date_range": {
                    "start": date_range[0].isoformat() if date_range[0] else None,
                    "end": date_range[1].isoformat() if date_range[1] else None,
                },
            }

            # Generate dashboard sections
            if "overview" in dashboard_sections:
                dashboard["overview"] = self._generate_dashboard_overview(
                    artist_slug, profile
                )

            if "trends" in dashboard_sections:
                dashboard["trends"] = self._generate_trend_analysis(profile, date_range)

            if "performance" in dashboard_sections:
                dashboard["performance"] = self._generate_performance_metrics(
                    artist_slug, date_range
                )

            if "evolution" in dashboard_sections:
                dashboard["evolution"] = self._generate_evolution_tracking(
                    artist_slug, profile, date_range
                )

            if "audience" in dashboard_sections:
                dashboard["audience"] = self._generate_audience_insights(
                    profile, date_range
                )

            if "recommendations" in dashboard_sections:
                dashboard["recommendations"] = self._generate_recommendations(
                    profile,
                    dashboard.get("trends", {}),
                    dashboard.get("performance", {}),
                    dashboard.get("evolution", {}),
                    dashboard.get("audience", {}),
                )

            # Generate visualizations
            dashboard["visualizations"] = self._generate_dashboard_visualizations(
                artist_slug, profile, dashboard, output_format
            )

            # Format dashboard based on output format
            formatted_dashboard = self._format_dashboard(dashboard, output_format)

            # Save dashboard if requested
            if save_dashboard:
                save_path = self._save_dashboard(
                    artist_slug, formatted_dashboard, output_format
                )
                dashboard["save_path"] = save_path

            logger.info(f"Successfully generated dashboard for artist: {artist_slug}")
            return dashboard

        except Exception as e:
            logger.error(
                f"Error generating dashboard for artist {artist_slug}: {str(e)}"
            )
            raise ArtistAnalyticsError(f"Failed to generate artist dashboard: {str(e)}")

    def _load_artist_profile(self, artist_slug: str) -> Dict[str, Any]:
        """
        Load an artist profile from disk.

        Args:
            artist_slug: Slug of the artist

        Returns:
            Artist profile dictionary
        """
        profile_path = os.path.join(self.artists_dir, artist_slug, "profile.json")

        if not os.path.exists(profile_path):
            raise ArtistAnalyticsError(f"Artist profile not found: {profile_path}")

        try:
            with open(profile_path, "r") as f:
                profile = json.load(f)

            return profile

        except Exception as e:
            raise ArtistAnalyticsError(f"Failed to load artist profile: {str(e)}")

    def _get_date_range(
        self, time_period: str
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Get start and end dates based on time period.

        Args:
            time_period: Time period ('all', 'last_week', 'last_month', 'last_year')

        Returns:
            Tuple of (start_date, end_date)
        """
        end_date = datetime.now()

        if time_period == "all":
            return None, end_date
        elif time_period == "last_week":
            start_date = end_date - timedelta(days=7)
        elif time_period == "last_month":
            start_date = end_date - timedelta(days=30)
        elif time_period == "last_year":
            start_date = end_date - timedelta(days=365)
        else:
            # Default to all time
            return None, end_date

        return start_date, end_date

    def _generate_trend_analysis(
        self,
        profile: Dict[str, Any],
        date_range: Tuple[Optional[datetime], Optional[datetime]],
    ) -> Dict[str, Any]:
        """
        Generate trend analysis for an artist.

        Args:
            profile: Artist profile
            date_range: Tuple of (start_date, end_date)

        Returns:
            Dictionary containing trend analysis
        """
        # Extract relevant information from profile
        main_genre = profile.get("genre", {}).get("main", "")
        subgenres = profile.get("genre", {}).get("subgenres", [])
        style_tags = profile.get("style_tags", [])

        # Get current trends
        current_trends = self.trend_analyzer.analyze_trends(
            main_genre=main_genre, subgenres=subgenres, style_tags=style_tags
        )

        # Analyze compatibility with current trends
        compatibility = self.trend_analyzer.analyze_artist_compatibility(
            artist_profile=profile, trend_data=current_trends
        )

        # Get historical trends if available
        historical_trends = profile.get("metadata", {}).get("trend_data", {})

        # Analyze trend evolution
        trend_evolution = self._analyze_trend_evolution(
            current_trends, historical_trends
        )

        return {
            "current_trends": current_trends,
            "compatibility": compatibility,
            "historical_trends": historical_trends,
            "trend_evolution": trend_evolution,
        }

    def _generate_performance_metrics(
        self,
        artist_slug: str,
        date_range: Tuple[Optional[datetime], Optional[datetime]],
    ) -> Dict[str, Any]:
        """
        Generate performance metrics for an artist.

        Args:
            artist_slug: Slug of the artist
            date_range: Tuple of (start_date, end_date)

        Returns:
            Dictionary containing performance metrics
        """
        # Get LLM efficiency metrics for the artist
        llm_metrics = self.llm_metrics.get_artist_efficiency_metrics(
            artist_id=artist_slug, start_time=date_range[0], end_time=date_range[1]
        )

        # Get LLM interactions
        interactions = self.llm_metrics.get_interactions(
            artist_id=artist_slug,
            start_time=date_range[0],
            end_time=date_range[1],
            limit=100,
        )

        # Calculate aggregate metrics
        if date_range[0] and date_range[1]:
            aggregate_metrics = self.llm_metrics.calculate_aggregate_metrics(
                start_time=date_range[0], end_time=date_range[1], time_period="daily"
            )
        else:
            aggregate_metrics = {}

        # Calculate success rates
        success_rates = self._calculate_success_rates(interactions)

        # Calculate cost efficiency
        cost_efficiency = self._calculate_cost_efficiency(llm_metrics)

        return {
            "llm_metrics": llm_metrics,
            "interactions_summary": self._summarize_interactions(interactions),
            "aggregate_metrics": aggregate_metrics,
            "success_rates": success_rates,
            "cost_efficiency": cost_efficiency,
        }

    def _generate_evolution_tracking(
        self,
        artist_slug: str,
        profile: Dict[str, Any],
        date_range: Tuple[Optional[datetime], Optional[datetime]],
    ) -> Dict[str, Any]:
        """
        Generate evolution tracking for an artist.

        Args:
            artist_slug: Slug of the artist
            profile: Artist profile
            date_range: Tuple of (start_date, end_date)

        Returns:
            Dictionary containing evolution tracking
        """
        # Get version history
        version_history = self._get_artist_version_history(artist_slug)

        # Filter version history by date range
        if date_range[0]:
            version_history = [
                v
                for v in version_history
                if datetime.fromisoformat(v["date"]) >= date_range[0]
            ]

        if date_range[1]:
            version_history = [
                v
                for v in version_history
                if datetime.fromisoformat(v["date"]) <= date_range[1]
            ]

        # Generate evolution timeline
        evolution_timeline = self._generate_evolution_timeline(
            artist_slug, version_history
        )

        # Analyze trend alignment
        trend_alignment = self._analyze_trend_alignment(artist_slug, version_history)

        # Calculate evolution metrics
        evolution_metrics = self._calculate_evolution_metrics(
            artist_slug, version_history
        )

        return {
            "version_history": version_history,
            "evolution_timeline": evolution_timeline,
            "trend_alignment": trend_alignment,
            "evolution_metrics": evolution_metrics,
        }

    def _generate_audience_insights(
        self,
        profile: Dict[str, Any],
        date_range: Tuple[Optional[datetime], Optional[datetime]],
    ) -> Dict[str, Any]:
        """
        Generate audience insights for an artist.

        Args:
            profile: Artist profile
            date_range: Tuple of (start_date, end_date)

        Returns:
            Dictionary containing audience insights
        """
        # Extract target audience from profile
        target_audience = profile.get("target_audience", "")

        # Analyze target audience
        audience_analysis = self._analyze_target_audience(target_audience)

        # Analyze audience compatibility with artist style
        style_compatibility = self._analyze_audience_style_compatibility(
            profile.get("style_tags", []), audience_analysis
        )

        # Analyze audience trends
        audience_trends = self._analyze_audience_trends(audience_analysis)

        return {
            "target_audience": target_audience,
            "audience_analysis": audience_analysis,
            "style_compatibility": style_compatibility,
            "audience_trends": audience_trends,
        }

    def _generate_recommendations(
        self,
        profile: Dict[str, Any],
        trend_analysis: Dict[str, Any],
        performance_metrics: Dict[str, Any],
        evolution_tracking: Dict[str, Any],
        audience_insights: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate recommendations based on analytics.

        Args:
            profile: Artist profile
            trend_analysis: Trend analysis data
            performance_metrics: Performance metrics data
            evolution_tracking: Evolution tracking data
            audience_insights: Audience insights data

        Returns:
            Dictionary containing recommendations
        """
        # Initialize recommendations
        recommendations = {
            "trend_recommendations": [],
            "performance_recommendations": [],
            "evolution_recommendations": [],
            "audience_recommendations": [],
            "priority_actions": [],
        }

        # Generate trend recommendations
        if trend_analysis:
            compatibility = trend_analysis.get("compatibility", {})
            current_trends = trend_analysis.get("current_trends", {})

            if compatibility and current_trends:
                recommendations["trend_recommendations"] = (
                    self._generate_trend_recommendations(
                        profile, current_trends, compatibility
                    )
                )

        # Generate performance recommendations
        if performance_metrics:
            success_rates = performance_metrics.get("success_rates", {})
            cost_efficiency = performance_metrics.get("cost_efficiency", {})

            if success_rates and cost_efficiency:
                recommendations["performance_recommendations"] = (
                    self._generate_performance_recommendations(
                        profile, success_rates, cost_efficiency
                    )
                )

        # Generate evolution recommendations
        if evolution_tracking:
            evolution_metrics = evolution_tracking.get("evolution_metrics", {})
            trend_alignment = evolution_tracking.get("trend_alignment", {})

            if evolution_metrics and trend_alignment:
                recommendations["evolution_recommendations"] = (
                    self._generate_evolution_recommendations(
                        profile, evolution_metrics, trend_alignment
                    )
                )

        # Generate audience recommendations
        if audience_insights:
            audience_analysis = audience_insights.get("audience_analysis", {})
            style_compatibility = audience_insights.get("style_compatibility", {})

            if audience_analysis and style_compatibility:
                recommendations["audience_recommendations"] = (
                    self._generate_audience_recommendations(
                        profile, audience_analysis, style_compatibility
                    )
                )

        # Determine priority actions
        all_recommendations = (
            recommendations["trend_recommendations"]
            + recommendations["performance_recommendations"]
            + recommendations["evolution_recommendations"]
            + recommendations["audience_recommendations"]
        )

        # Sort by importance and select top 3
        sorted_recommendations = sorted(
            all_recommendations, key=lambda x: x.get("importance", 0), reverse=True
        )

        recommendations["priority_actions"] = sorted_recommendations[:3]

        return recommendations

    def _generate_visualizations(
        self,
        artist_slug: str,
        profile: Dict[str, Any],
        report: Dict[str, Any],
        output_format: str,
    ) -> Dict[str, Any]:
        """
        Generate visualizations for an analytics report.

        Args:
            artist_slug: Slug of the artist
            profile: Artist profile
            report: Analytics report data
            output_format: Output format ('html', 'markdown')

        Returns:
            Dictionary containing visualization paths
        """
        # This is a placeholder implementation
        # In a real implementation, this would generate actual visualizations

        visualizations = {
            "trend_compatibility_chart": f"visualizations/{artist_slug}_trend_compatibility.png",
            "performance_metrics_chart": f"visualizations/{artist_slug}_performance_metrics.png",
            "evolution_timeline_chart": f"visualizations/{artist_slug}_evolution_timeline.png",
            "audience_insights_chart": f"visualizations/{artist_slug}_audience_insights.png",
        }

        return visualizations

    def _format_report(
        self, report: Dict[str, Any], output_format: str
    ) -> Union[Dict[str, Any], str]:
        """
        Format a report based on the specified output format.

        Args:
            report: Report data
            output_format: Output format ('json', 'html', 'markdown')

        Returns:
            Formatted report
        """
        if output_format == "json":
            return report
        elif output_format == "html":
            # This is a placeholder implementation
            # In a real implementation, this would generate actual HTML
            return f"<html><body><h1>Report for {report.get('artist_name', '')}</h1></body></html>"
        elif output_format == "markdown":
            # This is a placeholder implementation
            # In a real implementation, this would generate actual Markdown
            return f"# Report for {report.get('artist_name', '')}\n\n"
        else:
            return report

    def _save_report(
        self,
        artist_slug: str,
        report: Union[Dict[str, Any], str],
        report_type: str,
        output_format: str,
    ) -> str:
        """
        Save a report to disk.

        Args:
            artist_slug: Slug of the artist
            report: Formatted report
            report_type: Type of report
            output_format: Output format

        Returns:
            Path to the saved report
        """
        # Create directory for reports
        reports_dir = os.path.join(self.analytics_dir, artist_slug, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{artist_slug}_{report_type}_{timestamp}"

        if output_format == "json":
            filepath = os.path.join(reports_dir, f"{filename}.json")
            with open(filepath, "w") as f:
                json.dump(report, f, indent=2)
        elif output_format == "html":
            filepath = os.path.join(reports_dir, f"{filename}.html")
            with open(filepath, "w") as f:
                f.write(report)
        elif output_format == "markdown":
            filepath = os.path.join(reports_dir, f"{filename}.md")
            with open(filepath, "w") as f:
                f.write(report)
        else:
            filepath = os.path.join(reports_dir, f"{filename}.txt")
            with open(filepath, "w") as f:
                f.write(str(report))

        return filepath

    def _get_artist_version_history(self, artist_slug: str) -> List[Dict[str, Any]]:
        """
        Get version history for an artist.

        Args:
            artist_slug: Slug of the artist

        Returns:
            List of version history entries
        """
        versions_dir = os.path.join(self.artists_dir, artist_slug, "versions")

        if not os.path.exists(versions_dir):
            return []

        version_files = [
            f
            for f in os.listdir(versions_dir)
            if f.endswith(".json") and f.startswith("profile_v")
        ]

        version_history = []

        for file in version_files:
            try:
                # Extract version number from filename
                version_str = file.replace("profile_v", "").replace(".json", "")
                version = int(version_str)

                # Get file modification time
                file_path = os.path.join(versions_dir, file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                version_history.append(
                    {
                        "version": version,
                        "file": file,
                        "path": file_path,
                        "date": mod_time.isoformat(),
                    }
                )

            except Exception as e:
                logger.warning(f"Error processing version file {file}: {str(e)}")

        # Sort by version number
        version_history.sort(key=lambda x: x["version"])

        return version_history

    def _generate_evolution_timeline(
        self, artist_slug: str, version_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate an evolution timeline for an artist.

        Args:
            artist_slug: Slug of the artist
            version_history: Version history data

        Returns:
            List of timeline entries
        """
        timeline = []

        for i, version in enumerate(version_history):
            try:
                # Load version profile
                with open(version["path"], "r") as f:
                    profile = json.load(f)

                # Extract metadata
                metadata = profile.get("metadata", {})

                # Create timeline entry
                entry = {
                    "version": version["version"],
                    "date": version["date"],
                    "evolution_strength": metadata.get("evolution_strength"),
                    "trend_sensitivity": metadata.get("trend_sensitivity"),
                    "target_aspects": metadata.get("target_aspects", []),
                    "changes": {},
                }

                # Compare with previous version if available
                if i > 0:
                    prev_version = version_history[i - 1]

                    # Load previous version profile
                    with open(prev_version["path"], "r") as f:
                        prev_profile = json.load(f)

                    # Calculate changes
                    entry["changes"] = self._calculate_profile_changes(
                        prev_profile, profile
                    )

                timeline.append(entry)

            except Exception as e:
                logger.warning(
                    f"Error processing version {version['version']}: {str(e)}"
                )

        return timeline

    def _analyze_trend_alignment(
        self, artist_slug: str, version_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze how well artist evolution aligns with trends.

        Args:
            artist_slug: Slug of the artist
            version_history: Version history data

        Returns:
            Dictionary containing trend alignment analysis
        """
        alignment_scores = []

        for version in version_history:
            try:
                # Load version profile
                with open(version["path"], "r") as f:
                    profile = json.load(f)

                # Extract trend data from metadata
                metadata = profile.get("metadata", {})
                trend_data = metadata.get("trend_data", {})

                if not trend_data:
                    continue

                # Calculate alignment score
                compatibility = metadata.get("compatibility", {})
                overall_score = compatibility.get("overall_score", 0)

                alignment_scores.append(
                    {
                        "version": version["version"],
                        "date": version["date"],
                        "alignment_score": overall_score,
                        "trend_data": trend_data,
                    }
                )

            except Exception as e:
                logger.warning(
                    f"Error analyzing trend alignment for version {version['version']}: {str(e)}"
                )

        # Calculate trend alignment metrics
        avg_alignment = (
            sum(entry["alignment_score"] for entry in alignment_scores)
            / len(alignment_scores)
            if alignment_scores
            else 0
        )
        alignment_trend = self._calculate_trend(alignment_scores, "alignment_score")

        return {
            "alignment_scores": alignment_scores,
            "average_alignment": avg_alignment,
            "alignment_trend": alignment_trend,
        }

    def _calculate_evolution_metrics(
        self, artist_slug: str, version_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate metrics related to artist evolution.

        Args:
            artist_slug: Slug of the artist
            version_history: Version history data

        Returns:
            Dictionary containing evolution metrics
        """
        if not version_history:
            return {
                "total_versions": 0,
                "evolution_frequency": 0,
                "avg_evolution_strength": 0,
                "avg_trend_sensitivity": 0,
                "common_target_aspects": [],
            }

        # Calculate total versions
        total_versions = len(version_history)

        # Calculate evolution frequency (evolutions per month)
        if total_versions > 1:
            first_date = datetime.fromisoformat(version_history[0]["date"])
            last_date = datetime.fromisoformat(version_history[-1]["date"])

            # Calculate months between first and last version
            months = (last_date.year - first_date.year) * 12 + (
                last_date.month - first_date.month
            )
            months = max(1, months)  # Avoid division by zero

            evolution_frequency = total_versions / months
        else:
            evolution_frequency = 0

        # Calculate average evolution strength and trend sensitivity
        evolution_strengths = []
        trend_sensitivities = []
        all_target_aspects = []

        for version in version_history:
            try:
                # Load version profile
                with open(version["path"], "r") as f:
                    profile = json.load(f)

                # Extract metadata
                metadata = profile.get("metadata", {})

                # Collect evolution strength
                evolution_strength = metadata.get("evolution_strength")
                if evolution_strength is not None:
                    evolution_strengths.append(evolution_strength)

                # Collect trend sensitivity
                trend_sensitivity = metadata.get("trend_sensitivity")
                if trend_sensitivity is not None:
                    trend_sensitivities.append(trend_sensitivity)

                # Collect target aspects
                target_aspects = metadata.get("target_aspects", [])
                all_target_aspects.extend(target_aspects)

            except Exception as e:
                logger.warning(
                    f"Error calculating evolution metrics for version {version['version']}: {str(e)}"
                )

        # Calculate averages
        avg_evolution_strength = (
            sum(evolution_strengths) / len(evolution_strengths)
            if evolution_strengths
            else 0
        )
        avg_trend_sensitivity = (
            sum(trend_sensitivities) / len(trend_sensitivities)
            if trend_sensitivities
            else 0
        )

        # Find most common target aspects
        aspect_counter = Counter(all_target_aspects)
        common_target_aspects = [
            aspect for aspect, count in aspect_counter.most_common(5)
        ]

        return {
            "total_versions": total_versions,
            "evolution_frequency": evolution_frequency,
            "avg_evolution_strength": avg_evolution_strength,
            "avg_trend_sensitivity": avg_trend_sensitivity,
            "common_target_aspects": common_target_aspects,
        }

    def _analyze_target_audience(self, target_audience: str) -> Dict[str, Any]:
        """
        Analyze the target audience description.

        Args:
            target_audience: Target audience description

        Returns:
            Dictionary containing audience analysis
        """
        # This is a placeholder implementation
        # In a real implementation, this would use NLP to analyze the audience description

        # Extract age range (simple regex-based approach)
        age_range = "18-35"  # Default

        # Extract demographics (simple keyword-based approach)
        demographics = ["young adults", "urban"]

        # Extract interests (simple keyword-based approach)
        interests = ["music", "technology", "social media"]

        # Extract platforms (simple keyword-based approach)
        platforms = ["Instagram", "TikTok", "Spotify"]

        return {
            "age_range": age_range,
            "demographics": demographics,
            "interests": interests,
            "platforms": platforms,
            "original_description": target_audience,
        }

    def _analyze_audience_style_compatibility(
        self, style_tags: List[str], audience_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze compatibility between artist style and target audience.

        Args:
            style_tags: Artist style tags
            audience_analysis: Audience analysis data

        Returns:
            Dictionary containing style compatibility analysis
        """
        # This is a placeholder implementation
        # In a real implementation, this would use more sophisticated analysis

        # Calculate simple compatibility score
        compatibility_score = 0.75  # Default

        # Identify compatible style elements
        compatible_elements = ["modern", "digital"]

        # Identify potential style gaps
        style_gaps = ["interactive", "community-driven"]

        return {
            "compatibility_score": compatibility_score,
            "compatible_elements": compatible_elements,
            "style_gaps": style_gaps,
        }

    def _analyze_audience_trends(
        self, audience_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze trends related to the target audience.

        Args:
            audience_analysis: Audience analysis data

        Returns:
            Dictionary containing audience trend analysis
        """
        # This is a placeholder implementation
        # In a real implementation, this would use trend data specific to the audience

        # Identify trending platforms for this audience
        trending_platforms = ["TikTok", "Discord", "Twitch"]

        # Identify trending content types
        trending_content = [
            "Short-form video",
            "Interactive content",
            "Behind-the-scenes",
        ]

        # Identify trending engagement methods
        trending_engagement = [
            "Community challenges",
            "Live streaming",
            "Collaborative creation",
        ]

        return {
            "trending_platforms": trending_platforms,
            "trending_content": trending_content,
            "trending_engagement": trending_engagement,
        }

    def _analyze_trend_evolution(
        self, current_trends: Dict[str, Any], historical_trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze how trends have evolved over time.

        Args:
            current_trends: Current trend data
            historical_trends: Historical trend data

        Returns:
            Dictionary containing trend evolution analysis
        """
        # This is a placeholder implementation
        # In a real implementation, this would compare trends over time

        # Identify emerging trends
        emerging_trends = [
            "AI-generated content",
            "Virtual concerts",
            "Cross-platform integration",
        ]

        # Identify declining trends
        declining_trends = [
            "Traditional album releases",
            "Physical merchandise",
            "Single-platform focus",
        ]

        # Calculate trend velocity
        trend_velocity = 0.65  # Default

        return {
            "emerging_trends": emerging_trends,
            "declining_trends": declining_trends,
            "trend_velocity": trend_velocity,
        }

    def _calculate_profile_changes(
        self, prev_profile: Dict[str, Any], curr_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate changes between two artist profile versions.

        Args:
            prev_profile: Previous profile version
            curr_profile: Current profile version

        Returns:
            Dictionary containing profile changes
        """
        changes = {}

        # Compare genre
        prev_genre = prev_profile.get("genre", {})
        curr_genre = curr_profile.get("genre", {})

        if prev_genre != curr_genre:
            changes["genre"] = {"previous": prev_genre, "current": curr_genre}

        # Compare style tags
        prev_tags = set(prev_profile.get("style_tags", []))
        curr_tags = set(curr_profile.get("style_tags", []))

        if prev_tags != curr_tags:
            changes["style_tags"] = {
                "added": list(curr_tags - prev_tags),
                "removed": list(prev_tags - curr_tags),
            }

        # Compare other key attributes
        for key in ["vibe", "visual", "production", "target_audience"]:
            prev_value = prev_profile.get(key)
            curr_value = curr_profile.get(key)

            if prev_value != curr_value:
                changes[key] = {"previous": prev_value, "current": curr_value}

        return changes

    def _calculate_success_rates(
        self, interactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate success rates from LLM interactions.

        Args:
            interactions: List of LLM interactions

        Returns:
            Dictionary containing success rates
        """
        if not interactions:
            return {
                "overall_success_rate": 0,
                "success_by_module": {},
                "success_by_operation": {},
            }

        # Calculate overall success rate
        successful = sum(1 for i in interactions if i.get("success", False))
        overall_success_rate = successful / len(interactions) if interactions else 0

        # Calculate success rates by module
        modules = {}
        for interaction in interactions:
            module = interaction.get("module", "unknown")
            success = interaction.get("success", False)

            if module not in modules:
                modules[module] = {"total": 0, "successful": 0}

            modules[module]["total"] += 1
            if success:
                modules[module]["successful"] += 1

        success_by_module = {
            module: data["successful"] / data["total"] if data["total"] > 0 else 0
            for module, data in modules.items()
        }

        # Calculate success rates by operation
        operations = {}
        for interaction in interactions:
            operation = interaction.get("operation", "unknown")
            success = interaction.get("success", False)

            if operation not in operations:
                operations[operation] = {"total": 0, "successful": 0}

            operations[operation]["total"] += 1
            if success:
                operations[operation]["successful"] += 1

        success_by_operation = {
            operation: data["successful"] / data["total"] if data["total"] > 0 else 0
            for operation, data in operations.items()
        }

        return {
            "overall_success_rate": overall_success_rate,
            "success_by_module": success_by_module,
            "success_by_operation": success_by_operation,
        }

    def _calculate_cost_efficiency(self, llm_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate cost efficiency metrics.

        Args:
            llm_metrics: LLM metrics data

        Returns:
            Dictionary containing cost efficiency metrics
        """
        # Extract relevant metrics
        total_cost = llm_metrics.get("total_cost", 0)
        total_tokens = llm_metrics.get("total_tokens", 0)
        total_interactions = llm_metrics.get("total_interactions", 0)

        # Calculate cost per token
        cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0

        # Calculate cost per interaction
        cost_per_interaction = (
            total_cost / total_interactions if total_interactions > 0 else 0
        )

        # Calculate cost efficiency score (lower is better)
        cost_efficiency_score = cost_per_token * 1000  # Normalize to a reasonable range

        return {
            "total_cost": total_cost,
            "cost_per_token": cost_per_token,
            "cost_per_interaction": cost_per_interaction,
            "cost_efficiency_score": cost_efficiency_score,
        }

    def _summarize_interactions(
        self, interactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Summarize LLM interactions.

        Args:
            interactions: List of LLM interactions

        Returns:
            Dictionary containing interaction summary
        """
        if not interactions:
            return {
                "total_interactions": 0,
                "successful_interactions": 0,
                "modules": [],
                "operations": [],
            }

        # Count total and successful interactions
        total_interactions = len(interactions)
        successful_interactions = sum(
            1 for i in interactions if i.get("success", False)
        )

        # Count interactions by module
        module_counter = Counter(i.get("module", "unknown") for i in interactions)
        modules = [
            {"module": module, "count": count}
            for module, count in module_counter.most_common()
        ]

        # Count interactions by operation
        operation_counter = Counter(i.get("operation", "unknown") for i in interactions)
        operations = [
            {"operation": op, "count": count}
            for op, count in operation_counter.most_common()
        ]

        return {
            "total_interactions": total_interactions,
            "successful_interactions": successful_interactions,
            "modules": modules,
            "operations": operations,
        }

    def _generate_trend_recommendations(
        self,
        profile: Dict[str, Any],
        current_trends: Dict[str, Any],
        compatibility: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on trend analysis.

        Args:
            profile: Artist profile
            current_trends: Current trend data
            compatibility: Compatibility data

        Returns:
            List of recommendations
        """
        recommendations = []

        # Extract aspect scores
        aspect_scores = compatibility.get("aspect_scores", {})

        # Find aspects with low compatibility
        low_compatibility_aspects = [
            aspect for aspect, score in aspect_scores.items() if score < 0.5
        ]

        # Generate recommendations for each low compatibility aspect
        for aspect in low_compatibility_aspects:
            if aspect == "genre":
                # Recommend genre adjustments
                trending_genres = current_trends.get("trending_genres", [])[:3]

                if trending_genres:
                    recommendations.append(
                        {
                            "aspect": "genre",
                            "recommendation": f"Consider incorporating elements from trending genres: {', '.join(trending_genres)}",
                            "importance": 0.8,
                            "difficulty": "medium",
                        }
                    )

            elif aspect == "style":
                # Recommend style adjustments
                trending_styles = current_trends.get("trending_styles", [])[:3]

                if trending_styles:
                    recommendations.append(
                        {
                            "aspect": "style",
                            "recommendation": f"Explore trending style elements: {', '.join(trending_styles)}",
                            "importance": 0.7,
                            "difficulty": "medium",
                        }
                    )

            elif aspect == "production":
                # Recommend production adjustments
                recommendations.append(
                    {
                        "aspect": "production",
                        "recommendation": "Update production techniques to align with current trends",
                        "importance": 0.6,
                        "difficulty": "high",
                    }
                )

            elif aspect == "visual":
                # Recommend visual adjustments
                recommendations.append(
                    {
                        "aspect": "visual",
                        "recommendation": "Refresh visual aesthetic to better align with current visual trends",
                        "importance": 0.5,
                        "difficulty": "medium",
                    }
                )

        return recommendations

    def _generate_performance_recommendations(
        self,
        profile: Dict[str, Any],
        success_rates: Dict[str, Any],
        cost_efficiency: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on performance metrics.

        Args:
            profile: Artist profile
            success_rates: Success rate data
            cost_efficiency: Cost efficiency data

        Returns:
            List of recommendations
        """
        recommendations = []

        # Check overall success rate
        overall_success_rate = success_rates.get("overall_success_rate", 0)

        if overall_success_rate < 0.8:
            recommendations.append(
                {
                    "aspect": "success_rate",
                    "recommendation": "Improve LLM interaction success rate by refining prompts and input validation",
                    "importance": 0.9,
                    "difficulty": "medium",
                }
            )

        # Check cost efficiency
        cost_efficiency_score = cost_efficiency.get("cost_efficiency_score", 0)

        if cost_efficiency_score > 0.05:  # Threshold for high cost
            recommendations.append(
                {
                    "aspect": "cost_efficiency",
                    "recommendation": "Optimize token usage to reduce costs by implementing caching and prompt compression",
                    "importance": 0.8,
                    "difficulty": "medium",
                }
            )

        # Check module-specific success rates
        success_by_module = success_rates.get("success_by_module", {})

        for module, rate in success_by_module.items():
            if rate < 0.7:
                recommendations.append(
                    {
                        "aspect": f"{module}_success",
                        "recommendation": f"Improve success rate in the {module} module by reviewing and optimizing interactions",
                        "importance": 0.7,
                        "difficulty": "medium",
                    }
                )

        return recommendations

    def _generate_evolution_recommendations(
        self,
        profile: Dict[str, Any],
        evolution_metrics: Dict[str, Any],
        trend_alignment: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on evolution tracking.

        Args:
            profile: Artist profile
            evolution_metrics: Evolution metrics data
            trend_alignment: Trend alignment data

        Returns:
            List of recommendations
        """
        recommendations = []

        # Check evolution frequency
        evolution_frequency = evolution_metrics.get("evolution_frequency", 0)

        if evolution_frequency < 0.5:  # Less than once every two months
            recommendations.append(
                {
                    "aspect": "evolution_frequency",
                    "recommendation": "Increase evolution frequency to better adapt to changing trends",
                    "importance": 0.7,
                    "difficulty": "low",
                }
            )

        # Check trend alignment
        average_alignment = trend_alignment.get("average_alignment", 0)

        if average_alignment < 0.6:
            recommendations.append(
                {
                    "aspect": "trend_alignment",
                    "recommendation": "Improve trend alignment by increasing trend sensitivity during evolution",
                    "importance": 0.8,
                    "difficulty": "medium",
                }
            )

        # Check evolution strength
        avg_evolution_strength = evolution_metrics.get("avg_evolution_strength", 0)

        if avg_evolution_strength < 0.3:
            recommendations.append(
                {
                    "aspect": "evolution_strength",
                    "recommendation": "Increase evolution strength to make more significant adaptations",
                    "importance": 0.6,
                    "difficulty": "medium",
                }
            )
        elif avg_evolution_strength > 0.7:
            recommendations.append(
                {
                    "aspect": "evolution_strength",
                    "recommendation": "Decrease evolution strength to maintain more consistency in the artist identity",
                    "importance": 0.5,
                    "difficulty": "low",
                }
            )

        return recommendations

    def _generate_audience_recommendations(
        self,
        profile: Dict[str, Any],
        audience_analysis: Dict[str, Any],
        style_compatibility: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on audience insights.

        Args:
            profile: Artist profile
            audience_analysis: Audience analysis data
            style_compatibility: Style compatibility data

        Returns:
            List of recommendations
        """
        recommendations = []

        # Check style compatibility
        compatibility_score = style_compatibility.get("compatibility_score", 0)

        if compatibility_score < 0.7:
            recommendations.append(
                {
                    "aspect": "audience_compatibility",
                    "recommendation": "Adjust artist style to better align with target audience preferences",
                    "importance": 0.8,
                    "difficulty": "medium",
                }
            )

        # Check for style gaps
        style_gaps = style_compatibility.get("style_gaps", [])

        if style_gaps:
            recommendations.append(
                {
                    "aspect": "style_gaps",
                    "recommendation": f"Address style gaps in: {', '.join(style_gaps)}",
                    "importance": 0.7,
                    "difficulty": "medium",
                }
            )

        # Check audience platforms
        platforms = audience_analysis.get("platforms", [])

        if not platforms or len(platforms) < 2:
            recommendations.append(
                {
                    "aspect": "audience_platforms",
                    "recommendation": "Expand presence to more platforms where the target audience is active",
                    "importance": 0.6,
                    "difficulty": "high",
                }
            )

        return recommendations

    def _compare_genres(
        self, artist_profiles: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare genres across multiple artists.

        Args:
            artist_profiles: Dictionary of artist profiles

        Returns:
            Dictionary containing genre comparison
        """
        genre_comparison = {
            "main_genres": {},
            "subgenres": {},
            "genre_overlap": {},
            "genre_uniqueness": {},
        }

        # Extract main genres and subgenres
        for slug, profile in artist_profiles.items():
            genre_data = profile.get("genre", {})
            main_genre = genre_data.get("main", "")
            subgenres = genre_data.get("subgenres", [])

            genre_comparison["main_genres"][slug] = main_genre
            genre_comparison["subgenres"][slug] = subgenres

        # Calculate genre overlap between each pair of artists
        artist_slugs = list(artist_profiles.keys())

        for i, slug1 in enumerate(artist_slugs):
            for slug2 in artist_slugs[i + 1 :]:
                subgenres1 = set(genre_comparison["subgenres"].get(slug1, []))
                subgenres2 = set(genre_comparison["subgenres"].get(slug2, []))

                overlap = subgenres1.intersection(subgenres2)

                pair_key = f"{slug1}_vs_{slug2}"
                genre_comparison["genre_overlap"][pair_key] = list(overlap)

        # Calculate genre uniqueness for each artist
        for slug, profile in artist_profiles.items():
            subgenres = set(genre_comparison["subgenres"].get(slug, []))
            other_subgenres = set()

            for other_slug, other_profile in artist_profiles.items():
                if other_slug != slug:
                    other_subgenres.update(
                        other_profile.get("genre", {}).get("subgenres", [])
                    )

            unique_subgenres = subgenres - other_subgenres
            genre_comparison["genre_uniqueness"][slug] = list(unique_subgenres)

        return genre_comparison

    def _compare_styles(
        self, artist_profiles: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare styles across multiple artists.

        Args:
            artist_profiles: Dictionary of artist profiles

        Returns:
            Dictionary containing style comparison
        """
        style_comparison = {
            "style_tags": {},
            "style_overlap": {},
            "style_uniqueness": {},
            "style_similarity_scores": {},
        }

        # Extract style tags
        for slug, profile in artist_profiles.items():
            style_tags = profile.get("style_tags", [])
            style_comparison["style_tags"][slug] = style_tags

        # Calculate style overlap between each pair of artists
        artist_slugs = list(artist_profiles.keys())

        for i, slug1 in enumerate(artist_slugs):
            for slug2 in artist_slugs[i + 1 :]:
                tags1 = set(style_comparison["style_tags"].get(slug1, []))
                tags2 = set(style_comparison["style_tags"].get(slug2, []))

                overlap = tags1.intersection(tags2)

                pair_key = f"{slug1}_vs_{slug2}"
                style_comparison["style_overlap"][pair_key] = list(overlap)

                # Calculate similarity score (Jaccard similarity)
                union = tags1.union(tags2)
                similarity = len(overlap) / len(union) if union else 0

                style_comparison["style_similarity_scores"][pair_key] = similarity

        # Calculate style uniqueness for each artist
        for slug, profile in artist_profiles.items():
            tags = set(style_comparison["style_tags"].get(slug, []))
            other_tags = set()

            for other_slug, other_profile in artist_profiles.items():
                if other_slug != slug:
                    other_tags.update(other_profile.get("style_tags", []))

            unique_tags = tags - other_tags
            style_comparison["style_uniqueness"][slug] = list(unique_tags)

        return style_comparison

    def _compare_trends(
        self, artist_profiles: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare trend alignment across multiple artists.

        Args:
            artist_profiles: Dictionary of artist profiles

        Returns:
            Dictionary containing trend comparison
        """
        trend_comparison = {
            "trend_compatibility": {},
            "trend_alignment_ranking": [],
            "trend_adaptation_potential": {},
        }

        # Calculate trend compatibility for each artist
        for slug, profile in artist_profiles.items():
            # Extract relevant information
            main_genre = profile.get("genre", {}).get("main", "")
            subgenres = profile.get("genre", {}).get("subgenres", [])
            style_tags = profile.get("style_tags", [])

            # Get current trends
            current_trends = self.trend_analyzer.analyze_trends(
                main_genre=main_genre, subgenres=subgenres, style_tags=style_tags
            )

            # Analyze compatibility
            compatibility = self.trend_analyzer.analyze_artist_compatibility(
                artist_profile=profile, trend_data=current_trends
            )

            trend_comparison["trend_compatibility"][slug] = {
                "overall_score": compatibility.get("overall_score", 0),
                "aspect_scores": compatibility.get("aspect_scores", {}),
            }

        # Create trend alignment ranking
        ranking = sorted(
            trend_comparison["trend_compatibility"].items(),
            key=lambda x: x[1]["overall_score"],
            reverse=True,
        )

        trend_comparison["trend_alignment_ranking"] = [
            {"artist_slug": slug, "score": data["overall_score"]}
            for slug, data in ranking
        ]

        # Calculate trend adaptation potential
        for slug, profile in artist_profiles.items():
            # This is a placeholder implementation
            # In a real implementation, this would use more sophisticated analysis

            # Use metadata to estimate adaptability
            metadata = profile.get("metadata", {})
            evolution_strength = metadata.get("evolution_strength", 0.5)
            trend_sensitivity = metadata.get("trend_sensitivity", 0.5)

            # Simple formula for adaptation potential
            adaptation_potential = (evolution_strength + trend_sensitivity) / 2

            trend_comparison["trend_adaptation_potential"][slug] = adaptation_potential

        return trend_comparison

    def _compare_performance(self, artist_slugs: List[str]) -> Dict[str, Any]:
        """
        Compare performance metrics across multiple artists.

        Args:
            artist_slugs: List of artist slugs

        Returns:
            Dictionary containing performance comparison
        """
        performance_comparison = {
            "llm_metrics": {},
            "success_rates": {},
            "cost_efficiency": {},
            "performance_ranking": {},
        }

        # Get LLM metrics for each artist
        for slug in artist_slugs:
            # Get LLM efficiency metrics
            llm_metrics = self.llm_metrics.get_artist_efficiency_metrics(artist_id=slug)

            # Get interactions
            interactions = self.llm_metrics.get_interactions(artist_id=slug, limit=100)

            # Calculate success rates
            success_rates = self._calculate_success_rates(interactions)

            # Calculate cost efficiency
            cost_efficiency = self._calculate_cost_efficiency(llm_metrics)

            # Store metrics
            performance_comparison["llm_metrics"][slug] = llm_metrics
            performance_comparison["success_rates"][slug] = success_rates
            performance_comparison["cost_efficiency"][slug] = cost_efficiency

        # Create performance rankings
        # Success rate ranking
        success_ranking = sorted(
            [
                (slug, data["overall_success_rate"])
                for slug, data in performance_comparison["success_rates"].items()
            ],
            key=lambda x: x[1],
            reverse=True,
        )

        # Cost efficiency ranking (lower is better)
        cost_ranking = sorted(
            [
                (slug, data["cost_efficiency_score"])
                for slug, data in performance_comparison["cost_efficiency"].items()
            ],
            key=lambda x: x[1],
        )

        performance_comparison["performance_ranking"] = {
            "success_rate": [
                {"artist_slug": slug, "score": score} for slug, score in success_ranking
            ],
            "cost_efficiency": [
                {"artist_slug": slug, "score": score} for slug, score in cost_ranking
            ],
        }

        return performance_comparison

    def _compare_evolution(
        self, artist_slugs: List[str], artist_profiles: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare evolution patterns across multiple artists.

        Args:
            artist_slugs: List of artist slugs
            artist_profiles: Dictionary of artist profiles

        Returns:
            Dictionary containing evolution comparison
        """
        evolution_comparison = {
            "evolution_metrics": {},
            "evolution_frequency_ranking": [],
            "trend_alignment_ranking": [],
            "evolution_patterns": {},
        }

        # Calculate evolution metrics for each artist
        for slug in artist_slugs:
            # Get version history
            version_history = self._get_artist_version_history(slug)

            # Calculate evolution metrics
            evolution_metrics = self._calculate_evolution_metrics(slug, version_history)

            # Analyze trend alignment
            trend_alignment = self._analyze_trend_alignment(slug, version_history)

            # Store metrics
            evolution_comparison["evolution_metrics"][slug] = {
                "metrics": evolution_metrics,
                "trend_alignment": trend_alignment,
            }

        # Create evolution frequency ranking
        frequency_ranking = sorted(
            [
                (slug, data["metrics"]["evolution_frequency"])
                for slug, data in evolution_comparison["evolution_metrics"].items()
            ],
            key=lambda x: x[1],
            reverse=True,
        )

        evolution_comparison["evolution_frequency_ranking"] = [
            {"artist_slug": slug, "frequency": freq} for slug, freq in frequency_ranking
        ]

        # Create trend alignment ranking
        alignment_ranking = sorted(
            [
                (slug, data["trend_alignment"]["average_alignment"])
                for slug, data in evolution_comparison["evolution_metrics"].items()
            ],
            key=lambda x: x[1],
            reverse=True,
        )

        evolution_comparison["trend_alignment_ranking"] = [
            {"artist_slug": slug, "alignment": align}
            for slug, align in alignment_ranking
        ]

        # Analyze evolution patterns
        for slug, profile in artist_profiles.items():
            # This is a placeholder implementation
            # In a real implementation, this would use more sophisticated analysis

            # Use metadata to identify patterns
            metadata = profile.get("metadata", {})
            target_aspects = metadata.get("target_aspects", [])

            # Get evolution metrics
            metrics = (
                evolution_comparison["evolution_metrics"]
                .get(slug, {})
                .get("metrics", {})
            )
            common_aspects = metrics.get("common_target_aspects", [])

            evolution_comparison["evolution_patterns"][slug] = {
                "current_target_aspects": target_aspects,
                "common_target_aspects": common_aspects,
                "pattern_type": "consistent" if common_aspects else "varied",
            }

        return evolution_comparison

    def _compare_audience(
        self, artist_profiles: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare target audiences across multiple artists.

        Args:
            artist_profiles: Dictionary of artist profiles

        Returns:
            Dictionary containing audience comparison
        """
        audience_comparison = {
            "audience_analysis": {},
            "audience_overlap": {},
            "audience_uniqueness": {},
            "audience_similarity_scores": {},
        }

        # Analyze target audience for each artist
        for slug, profile in artist_profiles.items():
            target_audience = profile.get("target_audience", "")
            audience_analysis = self._analyze_target_audience(target_audience)

            audience_comparison["audience_analysis"][slug] = audience_analysis

        # Calculate audience overlap between each pair of artists
        artist_slugs = list(artist_profiles.keys())

        for i, slug1 in enumerate(artist_slugs):
            for slug2 in artist_slugs[i + 1 :]:
                analysis1 = audience_comparison["audience_analysis"].get(slug1, {})
                analysis2 = audience_comparison["audience_analysis"].get(slug2, {})

                # Compare demographics
                demographics1 = set(analysis1.get("demographics", []))
                demographics2 = set(analysis2.get("demographics", []))
                demographics_overlap = demographics1.intersection(demographics2)

                # Compare interests
                interests1 = set(analysis1.get("interests", []))
                interests2 = set(analysis2.get("interests", []))
                interests_overlap = interests1.intersection(interests2)

                # Compare platforms
                platforms1 = set(analysis1.get("platforms", []))
                platforms2 = set(analysis2.get("platforms", []))
                platforms_overlap = platforms1.intersection(platforms2)

                pair_key = f"{slug1}_vs_{slug2}"
                audience_comparison["audience_overlap"][pair_key] = {
                    "demographics": list(demographics_overlap),
                    "interests": list(interests_overlap),
                    "platforms": list(platforms_overlap),
                }

                # Calculate similarity score (average Jaccard similarity across categories)
                demographic_similarity = (
                    len(demographics_overlap) / len(demographics1.union(demographics2))
                    if demographics1.union(demographics2)
                    else 0
                )
                interests_similarity = (
                    len(interests_overlap) / len(interests1.union(interests2))
                    if interests1.union(interests2)
                    else 0
                )
                platforms_similarity = (
                    len(platforms_overlap) / len(platforms1.union(platforms2))
                    if platforms1.union(platforms2)
                    else 0
                )

                avg_similarity = (
                    demographic_similarity + interests_similarity + platforms_similarity
                ) / 3
                audience_comparison["audience_similarity_scores"][
                    pair_key
                ] = avg_similarity

        # Calculate audience uniqueness for each artist
        for slug, profile in artist_profiles.items():
            analysis = audience_comparison["audience_analysis"].get(slug, {})

            # Collect all demographics, interests, and platforms from other artists
            other_demographics = set()
            other_interests = set()
            other_platforms = set()

            for other_slug, other_profile in artist_profiles.items():
                if other_slug != slug:
                    other_analysis = audience_comparison["audience_analysis"].get(
                        other_slug, {}
                    )
                    other_demographics.update(other_analysis.get("demographics", []))
                    other_interests.update(other_analysis.get("interests", []))
                    other_platforms.update(other_analysis.get("platforms", []))

            # Calculate unique elements
            demographics = set(analysis.get("demographics", []))
            interests = set(analysis.get("interests", []))
            platforms = set(analysis.get("platforms", []))

            unique_demographics = demographics - other_demographics
            unique_interests = interests - other_interests
            unique_platforms = platforms - other_platforms

            audience_comparison["audience_uniqueness"][slug] = {
                "demographics": list(unique_demographics),
                "interests": list(unique_interests),
                "platforms": list(unique_platforms),
            }

        return audience_comparison

    def _generate_comparison_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of the comparison report.

        Args:
            report: Comparison report data

        Returns:
            Dictionary containing comparison summary
        """
        summary = {
            "most_similar_pair": None,
            "most_different_pair": None,
            "most_trend_aligned": None,
            "most_unique_artist": None,
            "key_findings": [],
        }

        # Find most similar and different pairs based on style
        if (
            "style_comparison" in report
            and "style_similarity_scores" in report["style_comparison"]
        ):
            similarity_scores = report["style_comparison"]["style_similarity_scores"]

            if similarity_scores:
                most_similar_pair = max(similarity_scores.items(), key=lambda x: x[1])
                most_different_pair = min(similarity_scores.items(), key=lambda x: x[1])

                summary["most_similar_pair"] = {
                    "pair": most_similar_pair[0],
                    "similarity_score": most_similar_pair[1],
                }

                summary["most_different_pair"] = {
                    "pair": most_different_pair[0],
                    "similarity_score": most_different_pair[1],
                }

        # Find most trend-aligned artist
        if (
            "trend_comparison" in report
            and "trend_alignment_ranking" in report["trend_comparison"]
        ):
            ranking = report["trend_comparison"]["trend_alignment_ranking"]

            if ranking:
                summary["most_trend_aligned"] = ranking[0]

        # Find most unique artist based on style uniqueness
        if (
            "style_comparison" in report
            and "style_uniqueness" in report["style_comparison"]
        ):
            uniqueness = report["style_comparison"]["style_uniqueness"]

            if uniqueness:
                most_unique = max(uniqueness.items(), key=lambda x: len(x[1]))

                summary["most_unique_artist"] = {
                    "artist_slug": most_unique[0],
                    "unique_elements": len(most_unique[1]),
                }

        # Generate key findings
        summary["key_findings"] = self._generate_comparison_findings(report)

        return summary

    def _generate_comparison_findings(self, report: Dict[str, Any]) -> List[str]:
        """
        Generate key findings from a comparison report.

        Args:
            report: Comparison report data

        Returns:
            List of key findings
        """
        findings = []

        # Add finding about genre overlap
        if (
            "genre_comparison" in report
            and "genre_overlap" in report["genre_comparison"]
        ):
            genre_overlap = report["genre_comparison"]["genre_overlap"]

            if any(len(overlap) > 0 for overlap in genre_overlap.values()):
                findings.append(
                    "Artists share some common genres, indicating potential for collaboration or cross-promotion."
                )
            else:
                findings.append(
                    "Artists have distinct genres with minimal overlap, suggesting a diverse portfolio."
                )

        # Add finding about style similarity
        if (
            "style_comparison" in report
            and "style_similarity_scores" in report["style_comparison"]
        ):
            similarity_scores = report["style_comparison"]["style_similarity_scores"]

            if similarity_scores:
                avg_similarity = sum(similarity_scores.values()) / len(
                    similarity_scores
                )

                if avg_similarity > 0.7:
                    findings.append(
                        "Artists have highly similar styles, which may lead to brand confusion."
                    )
                elif avg_similarity < 0.3:
                    findings.append(
                        "Artists have very distinct styles, creating a diverse portfolio."
                    )

        # Add finding about trend alignment
        if (
            "trend_comparison" in report
            and "trend_compatibility" in report["trend_comparison"]
        ):
            trend_compatibility = report["trend_comparison"]["trend_compatibility"]

            if trend_compatibility:
                scores = [
                    data["overall_score"] for data in trend_compatibility.values()
                ]
                avg_score = sum(scores) / len(scores)

                if avg_score > 0.7:
                    findings.append(
                        "Artists are well-aligned with current trends, positioning the portfolio for current market success."
                    )
                elif avg_score < 0.4:
                    findings.append(
                        "Artists show low trend alignment, suggesting a need for strategic evolution."
                    )

        # Add finding about audience overlap
        if (
            "audience_comparison" in report
            and "audience_similarity_scores" in report["audience_comparison"]
        ):
            similarity_scores = report["audience_comparison"][
                "audience_similarity_scores"
            ]

            if similarity_scores:
                avg_similarity = sum(similarity_scores.values()) / len(
                    similarity_scores
                )

                if avg_similarity > 0.7:
                    findings.append(
                        "Artists target very similar audiences, which may lead to internal competition."
                    )
                elif avg_similarity < 0.3:
                    findings.append(
                        "Artists target distinct audiences, maximizing market coverage."
                    )

        return findings

    def _save_comparison_report(
        self,
        artist_slugs: List[str],
        report: Union[Dict[str, Any], str],
        output_format: str,
    ) -> str:
        """
        Save a comparison report to disk.

        Args:
            artist_slugs: List of artist slugs
            report: Formatted report
            output_format: Output format

        Returns:
            Path to the saved report
        """
        # Create directory for comparison reports
        reports_dir = os.path.join(self.analytics_dir, "comparisons")
        os.makedirs(reports_dir, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slugs_str = "_".join(artist_slugs[:3])  # Use first 3 slugs in filename
        if len(artist_slugs) > 3:
            slugs_str += f"_and_{len(artist_slugs) - 3}_more"

        filename = f"comparison_{slugs_str}_{timestamp}"

        if output_format == "json":
            filepath = os.path.join(reports_dir, f"{filename}.json")
            with open(filepath, "w") as f:
                json.dump(report, f, indent=2)
        elif output_format == "html":
            filepath = os.path.join(reports_dir, f"{filename}.html")
            with open(filepath, "w") as f:
                f.write(report)
        elif output_format == "markdown":
            filepath = os.path.join(reports_dir, f"{filename}.md")
            with open(filepath, "w") as f:
                f.write(report)
        else:
            filepath = os.path.join(reports_dir, f"{filename}.txt")
            with open(filepath, "w") as f:
                f.write(str(report))

        return filepath

    def _save_evolution_report(
        self, artist_slug: str, report: Union[Dict[str, Any], str], output_format: str
    ) -> str:
        """
        Save an evolution tracking report to disk.

        Args:
            artist_slug: Slug of the artist
            report: Formatted report
            output_format: Output format

        Returns:
            Path to the saved report
        """
        # Create directory for evolution reports
        reports_dir = os.path.join(self.analytics_dir, artist_slug, "evolution")
        os.makedirs(reports_dir, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{artist_slug}_evolution_{timestamp}"

        if output_format == "json":
            filepath = os.path.join(reports_dir, f"{filename}.json")
            with open(filepath, "w") as f:
                json.dump(report, f, indent=2)
        elif output_format == "html":
            filepath = os.path.join(reports_dir, f"{filename}.html")
            with open(filepath, "w") as f:
                f.write(report)
        elif output_format == "markdown":
            filepath = os.path.join(reports_dir, f"{filename}.md")
            with open(filepath, "w") as f:
                f.write(report)
        else:
            filepath = os.path.join(reports_dir, f"{filename}.txt")
            with open(filepath, "w") as f:
                f.write(str(report))

        return filepath

    def _save_compatibility_report(
        self, artist_slug: str, report: Union[Dict[str, Any], str], output_format: str
    ) -> str:
        """
        Save a trend compatibility report to disk.

        Args:
            artist_slug: Slug of the artist
            report: Formatted report
            output_format: Output format

        Returns:
            Path to the saved report
        """
        # Create directory for compatibility reports
        reports_dir = os.path.join(self.analytics_dir, artist_slug, "trends")
        os.makedirs(reports_dir, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{artist_slug}_trend_compatibility_{timestamp}"

        if output_format == "json":
            filepath = os.path.join(reports_dir, f"{filename}.json")
            with open(filepath, "w") as f:
                json.dump(report, f, indent=2)
        elif output_format == "html":
            filepath = os.path.join(reports_dir, f"{filename}.html")
            with open(filepath, "w") as f:
                f.write(report)
        elif output_format == "markdown":
            filepath = os.path.join(reports_dir, f"{filename}.md")
            with open(filepath, "w") as f:
                f.write(report)
        else:
            filepath = os.path.join(reports_dir, f"{filename}.txt")
            with open(filepath, "w") as f:
                f.write(str(report))

        return filepath

    def _generate_dashboard_overview(
        self, artist_slug: str, profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate an overview section for an artist dashboard.

        Args:
            artist_slug: Slug of the artist
            profile: Artist profile

        Returns:
            Dictionary containing dashboard overview
        """
        # Extract basic information
        artist_name = profile.get("name", artist_slug)
        main_genre = profile.get("genre", {}).get("main", "")
        subgenres = profile.get("genre", {}).get("subgenres", [])
        style_tags = profile.get("style_tags", [])

        # Extract metadata
        metadata = profile.get("metadata", {})
        created_at = metadata.get("created_at")
        last_evolved = metadata.get("evolved_at")
        version = metadata.get("version", 1)

        # Get version history
        version_history = self._get_artist_version_history(artist_slug)

        return {
            "artist_name": artist_name,
            "artist_slug": artist_slug,
            "main_genre": main_genre,
            "subgenres": subgenres,
            "style_tags": style_tags,
            "created_at": created_at,
            "last_evolved": last_evolved,
            "version": version,
            "total_versions": len(version_history),
        }

    def _generate_dashboard_visualizations(
        self,
        artist_slug: str,
        profile: Dict[str, Any],
        dashboard: Dict[str, Any],
        output_format: str,
    ) -> Dict[str, Any]:
        """
        Generate visualizations for an artist dashboard.

        Args:
            artist_slug: Slug of the artist
            profile: Artist profile
            dashboard: Dashboard data
            output_format: Output format

        Returns:
            Dictionary containing visualization paths
        """
        # This is a placeholder implementation
        # In a real implementation, this would generate actual visualizations

        visualizations = {
            "trend_compatibility_chart": f"visualizations/{artist_slug}_trend_compatibility.png",
            "performance_metrics_chart": f"visualizations/{artist_slug}_performance_metrics.png",
            "evolution_timeline_chart": f"visualizations/{artist_slug}_evolution_timeline.png",
            "audience_insights_chart": f"visualizations/{artist_slug}_audience_insights.png",
        }

        return visualizations

    def _format_dashboard(
        self, dashboard: Dict[str, Any], output_format: str
    ) -> Union[Dict[str, Any], str]:
        """
        Format a dashboard based on the specified output format.

        Args:
            dashboard: Dashboard data
            output_format: Output format ('html', 'markdown')

        Returns:
            Formatted dashboard
        """
        if output_format == "html":
            # This is a placeholder implementation
            # In a real implementation, this would generate actual HTML
            return f"<html><body><h1>Dashboard for {dashboard.get('artist_name', '')}</h1></body></html>"
        elif output_format == "markdown":
            # This is a placeholder implementation
            # In a real implementation, this would generate actual Markdown
            return f"# Dashboard for {dashboard.get('artist_name', '')}\n\n"
        else:
            return dashboard

    def _save_dashboard(
        self,
        artist_slug: str,
        dashboard: Union[Dict[str, Any], str],
        output_format: str,
    ) -> str:
        """
        Save a dashboard to disk.

        Args:
            artist_slug: Slug of the artist
            dashboard: Formatted dashboard
            output_format: Output format

        Returns:
            Path to the saved dashboard
        """
        # Create directory for dashboards
        dashboards_dir = os.path.join(self.analytics_dir, artist_slug, "dashboards")
        os.makedirs(dashboards_dir, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{artist_slug}_dashboard_{timestamp}"

        if output_format == "html":
            filepath = os.path.join(dashboards_dir, f"{filename}.html")
            with open(filepath, "w") as f:
                f.write(dashboard)
        elif output_format == "markdown":
            filepath = os.path.join(dashboards_dir, f"{filename}.md")
            with open(filepath, "w") as f:
                f.write(dashboard)
        else:
            filepath = os.path.join(dashboards_dir, f"{filename}.txt")
            with open(filepath, "w") as f:
                f.write(str(dashboard))

        return filepath

    def _analyze_category_compatibility(
        self, profile: Dict[str, Any], current_trends: Dict[str, Any], category: str
    ) -> Dict[str, Any]:
        """
        Analyze compatibility between an artist and trends for a specific category.

        Args:
            profile: Artist profile
            current_trends: Current trend data
            category: Category to analyze

        Returns:
            Dictionary containing category compatibility analysis
        """
        # This is a placeholder implementation
        # In a real implementation, this would use more sophisticated analysis

        if category == "genre":
            # Extract artist genres
            main_genre = profile.get("genre", {}).get("main", "")
            subgenres = profile.get("genre", {}).get("subgenres", [])

            # Extract trending genres
            trending_genres = current_trends.get("trending_genres", [])

            # Calculate compatibility
            genre_match = main_genre in trending_genres
            subgenre_matches = [sg for sg in subgenres if sg in trending_genres]

            return {
                "category": "genre",
                "artist_values": [main_genre] + subgenres,
                "trending_values": trending_genres,
                "matches": [main_genre] if genre_match else [] + subgenre_matches,
                "compatibility_score": (
                    1
                    if genre_match
                    else 0 + len(subgenre_matches) / max(1, len(subgenres))
                )
                / 2,
            }

        elif category == "style":
            # Extract artist style tags
            style_tags = profile.get("style_tags", [])

            # Extract trending styles
            trending_styles = current_trends.get("trending_styles", [])

            # Calculate compatibility
            style_matches = [st for st in style_tags if st in trending_styles]

            return {
                "category": "style",
                "artist_values": style_tags,
                "trending_values": trending_styles,
                "matches": style_matches,
                "compatibility_score": len(style_matches) / max(1, len(style_tags)),
            }

        else:
            # Default implementation for other categories
            return {
                "category": category,
                "compatibility_score": 0.5,  # Default score
                "analysis": f"Detailed analysis for {category} not implemented",
            }

    def _generate_evolution_insights(
        self,
        artist_slug: str,
        profile: Dict[str, Any],
        version_history: List[Dict[str, Any]],
        trend_analysis: Dict[str, Any],
        performance_metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate insights about an artist's evolution.

        Args:
            artist_slug: Slug of the artist
            profile: Artist profile
            version_history: Version history data
            trend_analysis: Trend analysis data
            performance_metrics: Performance metrics data

        Returns:
            Dictionary containing evolution insights
        """
        insights = {
            "evolution_effectiveness": 0,
            "trend_responsiveness": 0,
            "identity_consistency": 0,
            "key_insights": [],
        }

        # Skip if no version history
        if not version_history or len(version_history) < 2:
            insights["key_insights"].append(
                "Insufficient version history for meaningful evolution analysis."
            )
            return insights

        # Calculate evolution effectiveness
        if trend_analysis and "compatibility" in trend_analysis:
            compatibility = trend_analysis["compatibility"]
            overall_score = compatibility.get("overall_score", 0)

            # Higher compatibility indicates more effective evolution
            insights["evolution_effectiveness"] = overall_score

        # Calculate trend responsiveness
        if "trend_alignment" in locals() and trend_alignment:
            alignment_scores = trend_alignment.get("alignment_scores", [])

            if alignment_scores:
                # Calculate trend in alignment scores
                alignment_trend = self._calculate_trend(
                    alignment_scores, "alignment_score"
                )

                # Positive trend indicates good responsiveness
                insights["trend_responsiveness"] = max(0, min(1, 0.5 + alignment_trend))

        # Calculate identity consistency
        if len(version_history) >= 2:
            # Load first and latest version profiles
            try:
                with open(version_history[0]["path"], "r") as f:
                    first_profile = json.load(f)

                with open(version_history[-1]["path"], "r") as f:
                    latest_profile = json.load(f)

                # Calculate changes
                changes = self._calculate_profile_changes(first_profile, latest_profile)

                # More changes indicate less consistency
                change_count = len(changes)
                consistency = max(0, min(1, 1 - (change_count / 10)))  # Normalize

                insights["identity_consistency"] = consistency

            except Exception as e:
                logger.warning(f"Error calculating identity consistency: {str(e)}")

        # Generate key insights
        insights["key_insights"] = self._generate_evolution_key_insights(
            profile, version_history, insights
        )

        return insights

    def _generate_evolution_key_insights(
        self,
        profile: Dict[str, Any],
        version_history: List[Dict[str, Any]],
        metrics: Dict[str, Any],
    ) -> List[str]:
        """
        Generate key insights about an artist's evolution.

        Args:
            profile: Artist profile
            version_history: Version history data
            metrics: Evolution metrics

        Returns:
            List of key insights
        """
        key_insights = []

        # Insight about evolution effectiveness
        effectiveness = metrics.get("evolution_effectiveness", 0)
        if effectiveness > 0.7:
            key_insights.append(
                "Evolution has been highly effective in aligning with current trends."
            )
        elif effectiveness < 0.4:
            key_insights.append(
                "Evolution has not effectively aligned the artist with current trends."
            )

        # Insight about trend responsiveness
        responsiveness = metrics.get("trend_responsiveness", 0)
        if responsiveness > 0.7:
            key_insights.append(
                "Artist shows strong responsiveness to changing trends."
            )
        elif responsiveness < 0.4:
            key_insights.append(
                "Artist shows limited responsiveness to changing trends."
            )

        # Insight about identity consistency
        consistency = metrics.get("identity_consistency", 0)
        if consistency > 0.7:
            key_insights.append(
                "Artist has maintained strong identity consistency throughout evolution."
            )
        elif consistency < 0.4:
            key_insights.append(
                "Artist has undergone significant identity changes during evolution."
            )

        # Insight about evolution frequency
        if len(version_history) > 3:
            # Calculate average time between versions
            dates = [datetime.fromisoformat(v["date"]) for v in version_history]
            intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
            avg_interval = sum(intervals) / len(intervals) if intervals else 0

            if avg_interval < 30:
                key_insights.append(
                    "Artist evolves frequently, with an average of less than 30 days between versions."
                )
            elif avg_interval > 90:
                key_insights.append(
                    "Artist evolves infrequently, with an average of more than 90 days between versions."
                )

        return key_insights

    def _calculate_trend(self, data: List[Dict[str, Any]], value_key: str) -> float:
        """
        Calculate the trend in a series of values.

        Args:
            data: List of data points
            value_key: Key for the value to analyze

        Returns:
            Trend value (positive for upward trend, negative for downward)
        """
        if not data or len(data) < 2:
            return 0

        # Extract values
        values = [entry.get(value_key, 0) for entry in data]

        # Calculate simple trend (difference between last and first)
        trend = values[-1] - values[0]

        # Normalize
        max_diff = max(abs(values[-1]), abs(values[0]))
        if max_diff > 0:
            trend = trend / max_diff

        return trend

    def _generate_comparison_visualizations(
        self,
        artist_slugs: List[str],
        artist_profiles: Dict[str, Dict[str, Any]],
        report: Dict[str, Any],
        output_format: str,
    ) -> Dict[str, Any]:
        """
        Generate visualizations for a comparison report.

        Args:
            artist_slugs: List of artist slugs
            artist_profiles: Dictionary of artist profiles
            report: Comparison report data
            output_format: Output format

        Returns:
            Dictionary containing visualization paths
        """
        # This is a placeholder implementation
        # In a real implementation, this would generate actual visualizations

        visualizations = {
            "style_similarity_chart": "visualizations/style_similarity_chart.png",
            "trend_alignment_chart": "visualizations/trend_alignment_chart.png",
            "audience_overlap_chart": "visualizations/audience_overlap_chart.png",
        }

        return visualizations

    def _generate_evolution_visualizations(
        self,
        artist_slug: str,
        profile: Dict[str, Any],
        report: Dict[str, Any],
        output_format: str,
    ) -> Dict[str, Any]:
        """
        Generate visualizations for an evolution tracking report.

        Args:
            artist_slug: Slug of the artist
            profile: Artist profile
            report: Evolution tracking report data
            output_format: Output format

        Returns:
            Dictionary containing visualization paths
        """
        # This is a placeholder implementation
        # In a real implementation, this would generate actual visualizations

        visualizations = {
            "evolution_timeline_chart": f"visualizations/{artist_slug}_evolution_timeline.png",
            "trend_alignment_chart": f"visualizations/{artist_slug}_trend_alignment.png",
            "aspect_evolution_chart": f"visualizations/{artist_slug}_aspect_evolution.png",
        }

        return visualizations

    def _generate_compatibility_visualizations(
        self,
        artist_slug: str,
        profile: Dict[str, Any],
        report: Dict[str, Any],
        output_format: str,
    ) -> Dict[str, Any]:
        """
        Generate visualizations for a trend compatibility report.

        Args:
            artist_slug: Slug of the artist
            profile: Artist profile
            report: Trend compatibility report data
            output_format: Output format

        Returns:
            Dictionary containing visualization paths
        """
        # This is a placeholder implementation
        # In a real implementation, this would generate actual visualizations

        visualizations = {
            "category_compatibility_chart": f"visualizations/{artist_slug}_category_compatibility.png",
            "trend_gap_chart": f"visualizations/{artist_slug}_trend_gap.png",
            "adaptation_potential_chart": f"visualizations/{artist_slug}_adaptation_potential.png",
        }

        return visualizations
