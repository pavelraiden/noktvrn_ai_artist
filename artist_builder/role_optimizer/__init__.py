"""
Role Optimizer Package Initialization

This module initializes the role optimizer package and provides
a unified interface for role optimization functionality.
"""

import logging
from typing import Dict, Any, List, Optional

from .role_dynamic_optimizer import RoleDynamicOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.role_optimizer")


class RoleOptimizer:
    """
    Main interface for the role optimizer system.
    Coordinates the analysis, optimization, and application of artist roles and behaviors.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the role optimizer system.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Initialize components
        self.dynamic_optimizer = RoleDynamicOptimizer(
            self.config.get("dynamic_optimizer_config")
        )

        logger.info("Initialized RoleOptimizer system")

    def optimize_artist_roles(
        self,
        artist_profile: Dict[str, Any],
        performance_data: Dict[str, Any],
        trend_analysis: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform a complete role optimization for an artist.

        Args:
            artist_profile: The artist's profile
            performance_data: Performance metrics and feedback data
            trend_analysis: Optional trend analysis results

        Returns:
            Dictionary containing updated artist profile and optimization details
        """
        try:
            logger.info(
                f"Starting role optimization for artist {artist_profile.get('stage_name', 'Unknown')}"
            )

            # Analyze artist performance
            performance_analysis = self.dynamic_optimizer.analyze_artist_performance(
                artist_profile, performance_data
            )

            # Generate optimization plan
            optimization_plan = self.dynamic_optimizer.generate_role_optimization_plan(
                artist_profile, performance_analysis, trend_analysis
            )

            # Apply optimization plan
            updated_profile = self.dynamic_optimizer.apply_optimization_plan(
                artist_profile, optimization_plan
            )

            # Prepare result
            result = {
                "artist_id": artist_profile.get("artist_id", "unknown"),
                "artist_name": artist_profile.get("stage_name", "Unknown"),
                "original_profile": artist_profile,
                "updated_profile": updated_profile,
                "performance_analysis": performance_analysis,
                "optimization_plan": optimization_plan,
                "summary": optimization_plan.get(
                    "summary", "Role optimization completed"
                ),
            }

            logger.info(
                f"Completed role optimization for artist {artist_profile.get('stage_name', 'Unknown')}"
            )
            return result

        except Exception as e:
            logger.error(f"Error in role optimization: {str(e)}")
            raise Exception(f"Failed to complete role optimization: {str(e)}")

    def get_optimization_history(
        self, artist_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get the optimization history for an artist.

        Args:
            artist_profile: The artist's profile

        Returns:
            List of optimization history entries
        """
        try:
            history = artist_profile.get("optimization_history", [])

            logger.info(
                f"Retrieved {len(history)} optimization history entries for artist {artist_profile.get('stage_name', 'Unknown')}"
            )
            return history

        except Exception as e:
            logger.error(f"Error retrieving optimization history: {str(e)}")
            raise Exception(f"Failed to retrieve optimization history: {str(e)}")

    def compare_artist_versions(
        self, original_profile: Dict[str, Any], updated_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two versions of an artist profile to identify changes.

        Args:
            original_profile: The original artist profile
            updated_profile: The updated artist profile

        Returns:
            Dictionary containing comparison results
        """
        try:
            logger.info(
                f"Comparing artist versions for {original_profile.get('stage_name', 'Unknown')}"
            )

            # Initialize comparison result
            comparison = {
                "artist_id": original_profile.get("artist_id", "unknown"),
                "artist_name": original_profile.get("stage_name", "Unknown"),
                "role_changes": [],
                "behavior_changes": [],
                "other_changes": [],
            }

            # Compare roles
            original_roles = original_profile.get("roles", [])
            updated_roles = updated_profile.get("roles", [])

            added_roles = [role for role in updated_roles if role not in original_roles]
            removed_roles = [
                role for role in original_roles if role not in updated_roles
            ]

            for role in added_roles:
                comparison["role_changes"].append(
                    {
                        "type": "added",
                        "role": role,
                        "emphasis": updated_profile.get("role_emphasis", {}).get(
                            role, "standard"
                        ),
                    }
                )

            for role in removed_roles:
                comparison["role_changes"].append(
                    {
                        "type": "removed",
                        "role": role,
                        "emphasis": original_profile.get("role_emphasis", {}).get(
                            role, "standard"
                        ),
                    }
                )

            # Compare role emphasis for roles that exist in both versions
            common_roles = [role for role in original_roles if role in updated_roles]

            for role in common_roles:
                original_emphasis = original_profile.get("role_emphasis", {}).get(
                    role, "standard"
                )
                updated_emphasis = updated_profile.get("role_emphasis", {}).get(
                    role, "standard"
                )

                if original_emphasis != updated_emphasis:
                    comparison["role_changes"].append(
                        {
                            "type": "modified",
                            "role": role,
                            "original_emphasis": original_emphasis,
                            "updated_emphasis": updated_emphasis,
                        }
                    )

            # Compare behavior patterns
            original_behaviors = original_profile.get("behavior_patterns", {})
            updated_behaviors = updated_profile.get("behavior_patterns", {})

            all_behaviors = set(
                list(original_behaviors.keys()) + list(updated_behaviors.keys())
            )

            for behavior in all_behaviors:
                original_level = original_behaviors.get(behavior, 0.0)
                updated_level = updated_behaviors.get(behavior, 0.0)

                if behavior not in original_behaviors:
                    comparison["behavior_changes"].append(
                        {"type": "added", "behavior": behavior, "level": updated_level}
                    )
                elif behavior not in updated_behaviors:
                    comparison["behavior_changes"].append(
                        {
                            "type": "removed",
                            "behavior": behavior,
                            "level": original_level,
                        }
                    )
                elif original_level != updated_level:
                    comparison["behavior_changes"].append(
                        {
                            "type": "modified",
                            "behavior": behavior,
                            "original_level": original_level,
                            "updated_level": updated_level,
                            "change": round(updated_level - original_level, 1),
                        }
                    )

            # Compare other relevant fields
            # This could be expanded based on what other fields are important to track

            logger.info(
                f"Completed artist version comparison with {len(comparison['role_changes'])} role changes and {len(comparison['behavior_changes'])} behavior changes"
            )
            return comparison

        except Exception as e:
            logger.error(f"Error comparing artist versions: {str(e)}")
            raise Exception(f"Failed to compare artist versions: {str(e)}")
