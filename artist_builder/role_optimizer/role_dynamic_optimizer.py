"""
Role Dynamic Optimization Module

This module manages the dynamic optimization of artist roles and behaviors
based on performance data, audience feedback, and trend analysis.
"""

import logging
import json
import os
import sys
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import uuid
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.role_optimizer")


class RoleOptimizerError(Exception):
    """Exception raised for errors in the role optimization process."""
    pass


class RoleDynamicOptimizer:
    """
    Manages the dynamic optimization of artist roles and behaviors.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the role dynamic optimizer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.role_definitions = self.config.get("role_definitions", {})
        self.behavior_patterns = self.config.get("behavior_patterns", {})
        self.optimization_threshold = self.config.get("optimization_threshold", 0.6)
        
        # Load default role definitions if not provided
        if not self.role_definitions:
            self._load_default_role_definitions()
        
        # Load default behavior patterns if not provided
        if not self.behavior_patterns:
            self._load_default_behavior_patterns()
        
        logger.info(f"Initialized RoleDynamicOptimizer with {len(self.role_definitions)} role definitions")

    def analyze_artist_performance(
        self, 
        artist_profile: Dict[str, Any],
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze artist performance data to identify optimization opportunities.
        
        Args:
            artist_profile: The artist's profile
            performance_data: Performance metrics and feedback data
            
        Returns:
            Dictionary containing performance analysis
        """
        try:
            logger.info(f"Analyzing performance for artist {artist_profile.get('stage_name', 'Unknown')}")
            
            # Extract current roles and behaviors
            current_roles = artist_profile.get("roles", [])
            current_behaviors = artist_profile.get("behavior_patterns", {})
            
            # Initialize analysis result
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "artist_id": artist_profile.get("artist_id", "unknown"),
                "artist_name": artist_profile.get("stage_name", "Unknown"),
                "current_roles": current_roles,
                "current_behaviors": current_behaviors,
                "performance_metrics": self._extract_performance_metrics(performance_data),
                "audience_feedback": self._extract_audience_feedback(performance_data),
                "role_performance": {},
                "behavior_performance": {},
                "optimization_opportunities": []
            }
            
            # Analyze performance of each role
            for role in current_roles:
                role_performance = self._analyze_role_performance(
                    role, 
                    analysis["performance_metrics"],
                    analysis["audience_feedback"]
                )
                analysis["role_performance"][role] = role_performance
            
            # Analyze performance of each behavior pattern
            for behavior, level in current_behaviors.items():
                behavior_performance = self._analyze_behavior_performance(
                    behavior,
                    level,
                    analysis["performance_metrics"],
                    analysis["audience_feedback"]
                )
                analysis["behavior_performance"][behavior] = behavior_performance
            
            # Identify optimization opportunities
            analysis["optimization_opportunities"] = self._identify_optimization_opportunities(
                analysis["role_performance"],
                analysis["behavior_performance"],
                current_roles,
                current_behaviors
            )
            
            logger.info(f"Completed performance analysis with {len(analysis['optimization_opportunities'])} opportunities")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing artist performance: {str(e)}")
            raise RoleOptimizerError(f"Failed to analyze artist performance: {str(e)}")

    def generate_role_optimization_plan(
        self,
        artist_profile: Dict[str, Any],
        performance_analysis: Dict[str, Any],
        trend_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a plan for optimizing artist roles and behaviors.
        
        Args:
            artist_profile: The artist's profile
            performance_analysis: Performance analysis results
            trend_analysis: Optional trend analysis results
            
        Returns:
            Dictionary containing optimization plan
        """
        try:
            logger.info(f"Generating optimization plan for artist {artist_profile.get('stage_name', 'Unknown')}")
            
            # Extract current roles and behaviors
            current_roles = artist_profile.get("roles", [])
            current_behaviors = artist_profile.get("behavior_patterns", {})
            
            # Initialize optimization plan
            plan = {
                "timestamp": datetime.now().isoformat(),
                "artist_id": artist_profile.get("artist_id", "unknown"),
                "artist_name": artist_profile.get("stage_name", "Unknown"),
                "current_roles": current_roles,
                "current_behaviors": current_behaviors,
                "recommended_role_changes": [],
                "recommended_behavior_changes": [],
                "new_role_recommendations": [],
                "rationale": {}
            }
            
            # Process optimization opportunities
            opportunities = performance_analysis.get("optimization_opportunities", [])
            
            for opportunity in opportunities:
                if opportunity["type"] == "role_adjustment":
                    plan["recommended_role_changes"].append({
                        "role": opportunity["role"],
                        "current_emphasis": opportunity.get("current_emphasis", "standard"),
                        "recommended_emphasis": opportunity["recommended_emphasis"],
                        "confidence": opportunity["confidence"],
                        "expected_impact": opportunity["expected_impact"]
                    })
                    
                    plan["rationale"][f"role:{opportunity['role']}"] = opportunity["rationale"]
                
                elif opportunity["type"] == "behavior_adjustment":
                    plan["recommended_behavior_changes"].append({
                        "behavior": opportunity["behavior"],
                        "current_level": opportunity["current_level"],
                        "recommended_level": opportunity["recommended_level"],
                        "confidence": opportunity["confidence"],
                        "expected_impact": opportunity["expected_impact"]
                    })
                    
                    plan["rationale"][f"behavior:{opportunity['behavior']}"] = opportunity["rationale"]
                
                elif opportunity["type"] == "new_role":
                    plan["new_role_recommendations"].append({
                        "role": opportunity["role"],
                        "recommended_emphasis": opportunity["recommended_emphasis"],
                        "confidence": opportunity["confidence"],
                        "expected_impact": opportunity["expected_impact"]
                    })
                    
                    plan["rationale"][f"new_role:{opportunity['role']}"] = opportunity["rationale"]
            
            # Incorporate trend analysis if available
            if trend_analysis:
                self._incorporate_trend_analysis(plan, trend_analysis, artist_profile)
            
            # Generate implementation steps
            plan["implementation_steps"] = self._generate_implementation_steps(plan, artist_profile)
            
            # Generate summary
            plan["summary"] = self._generate_optimization_summary(plan)
            
            logger.info(f"Completed optimization plan with {len(plan['implementation_steps'])} steps")
            return plan
            
        except Exception as e:
            logger.error(f"Error generating optimization plan: {str(e)}")
            raise RoleOptimizerError(f"Failed to generate optimization plan: {str(e)}")

    def apply_optimization_plan(
        self,
        artist_profile: Dict[str, Any],
        optimization_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply an optimization plan to an artist profile.
        
        Args:
            artist_profile: The artist's profile to update
            optimization_plan: The optimization plan to apply
            
        Returns:
            Updated artist profile
        """
        try:
            logger.info(f"Applying optimization plan to artist {artist_profile.get('stage_name', 'Unknown')}")
            
            # Create a deep copy of the artist profile
            updated_profile = json.loads(json.dumps(artist_profile))
            
            # Initialize roles and behaviors if they don't exist
            if "roles" not in updated_profile:
                updated_profile["roles"] = []
            
            if "behavior_patterns" not in updated_profile:
                updated_profile["behavior_patterns"] = {}
            
            if "role_emphasis" not in updated_profile:
                updated_profile["role_emphasis"] = {}
            
            # Apply role changes
            for change in optimization_plan.get("recommended_role_changes", []):
                role = change["role"]
                emphasis = change["recommended_emphasis"]
                
                # Update role emphasis
                updated_profile["role_emphasis"][role] = emphasis
            
            # Apply behavior changes
            for change in optimization_plan.get("recommended_behavior_changes", []):
                behavior = change["behavior"]
                level = change["recommended_level"]
                
                # Update behavior level
                updated_profile["behavior_patterns"][behavior] = level
            
            # Add new roles
            for new_role in optimization_plan.get("new_role_recommendations", []):
                role = new_role["role"]
                emphasis = new_role["recommended_emphasis"]
                
                # Add role if it doesn't exist
                if role not in updated_profile["roles"]:
                    updated_profile["roles"].append(role)
                
                # Set role emphasis
                updated_profile["role_emphasis"][role] = emphasis
            
            # Add optimization history
            if "optimization_history" not in updated_profile:
                updated_profile["optimization_history"] = []
            
            # Record this optimization
            updated_profile["optimization_history"].append({
                "timestamp": datetime.now().isoformat(),
                "plan_id": optimization_plan.get("plan_id", str(uuid.uuid4())),
                "changes": {
                    "role_changes": len(optimization_plan.get("recommended_role_changes", [])),
                    "behavior_changes": len(optimization_plan.get("recommended_behavior_changes", [])),
                    "new_roles": len(optimization_plan.get("new_role_recommendations", []))
                },
                "summary": optimization_plan.get("summary", "Role and behavior optimization applied")
            })
            
            # Update last_optimized timestamp
            updated_profile["last_optimized"] = datetime.now().isoformat()
            
            logger.info(f"Successfully applied optimization plan to artist profile")
            return updated_profile
            
        except Exception as e:
            logger.error(f"Error applying optimization plan: {str(e)}")
            raise RoleOptimizerError(f"Failed to apply optimization plan: {str(e)}")

    def _extract_performance_metrics(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant performance metrics from performance data.
        
        Args:
            performance_data: Raw performance data
            
        Returns:
            Dictionary of relevant performance metrics
        """
        metrics = {}
        
        # Extract engagement metrics
        engagement = performance_data.get("engagement", {})
        metrics["engagement"] = {
            "average_likes": engagement.get("average_likes", 0),
            "average_comments": engagement.get("average_comments", 0),
            "average_shares": engagement.get("average_shares", 0),
            "follower_growth_rate": engagement.get("follower_growth_rate", 0),
            "engagement_rate": engagement.get("engagement_rate", 0)
        }
        
        # Extract content performance metrics
        content = performance_data.get("content", {})
        metrics["content"] = {
            "song_performance": content.get("song_performance", {}),
            "video_performance": content.get("video_performance", {}),
            "post_performance": content.get("post_performance", {})
        }
        
        # Extract audience metrics
        audience = performance_data.get("audience", {})
        metrics["audience"] = {
            "demographic_distribution": audience.get("demographic_distribution", {}),
            "geographic_distribution": audience.get("geographic_distribution", {}),
            "platform_distribution": audience.get("platform_distribution", {})
        }
        
        return metrics

    def _extract_audience_feedback(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract audience feedback from performance data.
        
        Args:
            performance_data: Raw performance data
            
        Returns:
            Dictionary of audience feedback
        """
        feedback = {}
        
        # Extract sentiment analysis
        sentiment = performance_data.get("sentiment_analysis", {})
        feedback["sentiment"] = {
            "overall_sentiment": sentiment.get("overall_sentiment", 0),
            "positive_comments_ratio": sentiment.get("positive_comments_ratio", 0),
            "negative_comments_ratio": sentiment.get("negative_comments_ratio", 0),
            "neutral_comments_ratio": sentiment.get("neutral_comments_ratio", 0)
        }
        
        # Extract common themes in feedback
        feedback["themes"] = performance_data.get("feedback_themes", {})
        
        # Extract specific role-related feedback
        feedback["role_specific"] = performance_data.get("role_specific_feedback", {})
        
        return feedback

    def _analyze_role_performance(
        self,
        role: str,
        performance_metrics: Dict[str, Any],
        audience_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze performance of a specific role.
        
        Args:
            role: The role to analyze
            performance_metrics: Performance metrics
            audience_feedback: Audience feedback
            
        Returns:
            Dictionary containing role performance analysis
        """
        # Get role definition
        role_def = self.role_definitions.get(role, {})
        
        # Initialize result
        result = {
            "role": role,
            "performance_score": 0.0,
            "audience_reception": 0.0,
            "strengths": [],
            "weaknesses": [],
            "overall_assessment": ""
        }
        
        # Calculate performance score based on relevant metrics
        relevant_metrics = role_def.get("relevant_metrics", [])
        if relevant_metrics:
            scores = []
            
            for metric_path in relevant_metrics:
                # Parse metric path (e.g., "engagement.average_likes")
                parts = metric_path.split(".")
                
                # Navigate to the metric value
                value = performance_metrics
                for part in parts:
                    if part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                
                if value is not None and isinstance(value, (int, float)):
                    # Normalize to 0-1 scale based on expected ranges
                    expected_min = role_def.get("metric_ranges", {}).get(metric_path, {}).get("min", 0)
                    expected_max = role_def.get("metric_ranges", {}).get(metric_path, {}).get("max", 100)
                    
                    if expected_max > expected_min:
                        normalized = (value - expected_min) / (expected_max - expected_min)
                        normalized = max(0.0, min(1.0, normalized))
                        scores.append(normalized)
            
            if scores:
                result["performance_score"] = round(sum(scores) / len(scores), 2)
        
        # Calculate audience reception
        role_specific_feedback = audience_feedback.get("role_specific", {}).get(role, {})
        sentiment_score = role_specific_feedback.get("sentiment_score", 0.5)
        
        # Combine with overall sentiment if role-specific is not available
        if sentiment_score == 0.5 and "sentiment" in audience_feedback:
            sentiment_score = audience_feedback["sentiment"].get("overall_sentiment", 0.5)
        
        result["audience_reception"] = round(sentiment_score, 2)
        
        # Identify strengths and weaknesses
        if result["performance_score"] >= 0.7:
            result["strengths"].append("Strong performance metrics")
        elif result["performance_score"] <= 0.4:
            result["weaknesses"].append("Underperforming metrics")
        
        if result["audience_reception"] >= 0.7:
            result["strengths"].append("Positive audience reception")
        elif result["audience_reception"] <= 0.4:
            result["weaknesses"].append("Negative audience reception")
        
        # Add role-specific strengths/weaknesses
        for theme, score in audience_feedback.get("themes", {}).items():
            if theme in role_def.get("related_themes", []):
                if score >= 0.7:
                    result["strengths"].append(f"Strong reception for '{theme}'")
                elif score <= 0.3:
                    result["weaknesses"].append(f"Poor reception for '{theme}'")
        
        # Generate overall assessment
        combined_score = (result["performance_score"] + result["audience_reception"]) / 2
        
        if combined_score >= 0.7:
            result["overall_assessment"] = "performing well"
        elif combined_score >= 0.5:
            result["overall_assessment"] = "performing adequately"
        else:
            result["overall_assessment"] = "underperforming"
        
        return result

    def _analyze_behavior_performance(
        self,
        behavior: str,
        current_level: float,
        performance_metrics: Dict[str, Any],
        audience_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze performance of a specific behavior pattern.
        
        Args:
            behavior: The behavior to analyze
            current_level: Current level of the behavior (0.0 to 1.0)
            performance_metrics: Performance metrics
            audience_feedback: Audience feedback
            
        Returns:
            Dictionary containing behavior performance analysis
        """
        # Get behavior definition
        behavior_def = self.behavior_patterns.get(behavior, {})
        
        # Initialize result
        result = {
            "behavior": behavior,
            "current_level": current_level,
            "performance_impact": 0.0,
            "audience_reception": 0.0,
            "optimal_level": current_level,  # Default to current level
            "assessment": ""
        }
        
        # Calculate performance impact
        impact_metrics = behavior_def.get("impact_metrics", [])
        if impact_metrics:
            impact_scores = []
            
            for metric_path in impact_metrics:
                # Similar to role performance analysis
                parts = metric_path.split(".")
                value = performance_metrics
                for part in parts:
                    if part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                
                if value is not None and isinstance(value, (int, float)):
                    # Get expected impact direction (positive or negative)
                    direction = behavior_def.get("impact_direction", {}).get(metric_path, 1)
                    
                    # Normalize value
                    expected_min = behavior_def.get("metric_ranges", {}).get(metric_path, {}).get("min", 0)
                    expected_max = behavior_def.get("metric_ranges", {}).get(metric_path, {}).get("max", 100)
                    
                    if expected_max > expected_min:
                        normalized = (value - expected_min) / (expected_max - expected_min)
                        normalized = max(0.0, min(1.0, normalized))
                        
                        # Apply direction
                        impact = normalized * direction
                        impact_scores.append(impact)
            
            if impact_scores:
                result["performance_impact"] = round(sum(impact_scores) / len(impact_scores), 2)
        
        # Calculate audience reception
        behavior_feedback = audience_feedback.get("themes", {}).get(behavior, 0.5)
        result["audience_reception"] = round(behavior_feedback, 2)
        
        # Determine optimal level
        # This is a simplified model - in a real system, this would be more sophisticated
        if result["performance_impact"] > 0.6 and result["audience_reception"] > 0.6:
            # Behavior is working well, increase level
            result["optimal_level"] = min(1.0, current_level + 0.2)
            result["assessment"] = "performing well, consider increasing"
        elif result["performance_impact"] < 0.4 and result["audience_reception"] < 0.4:
            # Behavior is not working well, decrease level
            result["optimal_level"] = max(0.0, current_level - 0.2)
            result["assessment"] = "underperforming, consider decreasing"
        else:
            # Behavior is performing adequately, maintain level
            result["optimal_level"] = current_level
            result["assessment"] = "performing adequately, maintain current level"
        
        # Round optimal level
        result["optimal_level"] = round(result["optimal_level"], 1)
        
        return result

    def _identify_optimization_opportunities(
        self,
        role_performance: Dict[str, Dict[str, Any]],
        behavior_performance: Dict[str, Dict[str, Any]],
        current_roles: List[str],
        current_behaviors: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Identify opportunities for role and behavior optimization.
        
        Args:
            role_performance: Performance analysis for each role
            behavior_performance: Performance analysis for each behavior
            current_roles: Current roles of the artist
            current_behaviors: Current behavior patterns of the artist
            
        Returns:
            List of optimization opportunities
        """
        opportunities = []
        
        # Analyze role optimization opportunities
        for role, performance in role_performance.items():
            combined_score = (performance["performance_score"] + performance["audience_reception"]) / 2
            
            if combined_score >= 0.7:
                # Role is performing well, consider emphasizing
                opportunities.append({
                    "type": "role_adjustment",
                    "role": role,
                    "current_emphasis": "standard",  # Assuming standard emphasis by default
                    "recommended_emphasis": "emphasized",
                    "confidence": "high" if combined_score >= 0.8 else "medium",
                    "expected_impact": "positive",
                    "rationale": f"Role is {performance['overall_assessment']} with strong metrics and audience reception"
                })
            elif combined_score <= 0.4:
                # Role is underperforming, consider de-emphasizing
                opportunities.append({
                    "type": "role_adjustment",
                    "role": role,
                    "current_emphasis": "standard",  # Assuming standard emphasis by default
                    "recommended_emphasis": "de-emphasized",
                    "confidence": "high" if combined_score <= 0.3 else "medium",
                    "expected_impact": "positive",
                    "rationale": f"Role is {performance['overall_assessment']} with weak metrics and audience reception"
                })
        
        # Analyze behavior optimization opportunities
        for behavior, performance in behavior_performance.items():
            current_level = performance["current_level"]
            optimal_level = performance["optimal_level"]
            
            # Only suggest changes if the difference is significant
            if abs(optimal_level - current_level) >= 0.2:
                opportunities.append({
                    "type": "behavior_adjustment",
                    "behavior": behavior,
                    "current_level": current_level,
                    "recommended_level": optimal_level,
                    "confidence": "high" if abs(optimal_level - current_level) >= 0.3 else "medium",
                    "expected_impact": "positive",
                    "rationale": f"Behavior is {performance['assessment']}"
                })
        
        # Identify potential new roles
        all_roles = set(self.role_definitions.keys())
        missing_roles = all_roles - set(current_roles)
        
        # For each missing role, evaluate if it should be added
        for role in missing_roles:
            # This is a simplified evaluation - in a real system, this would be more sophisticated
            # based on artist profile, genre, audience, etc.
            role_def = self.role_definitions.get(role, {})
            
            # Skip roles that don't match the artist's genre or style
            # (This would be a more complex check in a real system)
            if random.random() > 0.8:  # Simplified evaluation
                opportunities.append({
                    "type": "new_role",
                    "role": role,
                    "recommended_emphasis": "standard",
                    "confidence": "medium",
                    "expected_impact": "positive",
                    "rationale": f"Adding the {role} role could expand artist appeal and engagement"
                })
        
        return opportunities

    def _incorporate_trend_analysis(
        self,
        plan: Dict[str, Any],
        trend_analysis: Dict[str, Any],
        artist_profile: Dict[str, Any]
    ) -> None:
        """
        Incorporate trend analysis into the optimization plan.
        
        Args:
            plan: The optimization plan to update
            trend_analysis: Trend analysis results
            artist_profile: The artist's profile
        """
        # Extract trend recommendations
        trend_recommendations = trend_analysis.get("evolution_recommendations", [])
        
        # Map trend types to roles and behaviors
        trend_role_map = {
            "subgenre": ["innovator", "trendsetter", "genre_specialist"],
            "technique": ["producer", "sound_designer", "technical_innovator"],
            "theme": ["storyteller", "social_commentator", "thematic_artist"],
            "visual": ["visual_artist", "aesthetic_curator", "brand_manager"]
        }
        
        trend_behavior_map = {
            "subgenre": ["experimentation", "genre_fusion", "trend_adoption"],
            "technique": ["technical_innovation", "production_quality", "sound_design"],
            "theme": ["thematic_consistency", "storytelling", "message_focus"],
            "visual": ["visual_consistency", "aesthetic_evolution", "brand_identity"]
        }
        
        # For each trend recommendation, adjust related roles and behaviors
        for rec in trend_recommendations:
            trend_type = rec.get("type")
            trend_name = rec.get("name")
            
            if not trend_type or not trend_name:
                continue
            
            # Adjust related roles
            for role in trend_role_map.get(trend_type, []):
                # Check if role is already in the plan
                existing_change = next(
                    (r for r in plan["recommended_role_changes"] if r["role"] == role),
                    None
                )
                
                if existing_change:
                    # Update existing change with trend information
                    existing_change["trend_influenced"] = True
                    existing_change["trend_info"] = {
                        "type": trend_type,
                        "name": trend_name
                    }
                    
                    # Update rationale
                    role_rationale = plan["rationale"].get(f"role:{role}", "")
                    plan["rationale"][f"role:{role}"] = f"{role_rationale}\nInfluenced by trending {trend_type}: {trend_name}"
                else:
                    # Check if role is already in the artist's roles
                    if role in artist_profile.get("roles", []):
                        # Add new role change
                        plan["recommended_role_changes"].append({
                            "role": role,
                            "current_emphasis": "standard",
                            "recommended_emphasis": "emphasized",
                            "confidence": "medium",
                            "expected_impact": "positive",
                            "trend_influenced": True,
                            "trend_info": {
                                "type": trend_type,
                                "name": trend_name
                            }
                        })
                        
                        plan["rationale"][f"role:{role}"] = f"Emphasis recommended due to trending {trend_type}: {trend_name}"
                    else:
                        # Add new role recommendation
                        plan["new_role_recommendations"].append({
                            "role": role,
                            "recommended_emphasis": "standard",
                            "confidence": "medium",
                            "expected_impact": "positive",
                            "trend_influenced": True,
                            "trend_info": {
                                "type": trend_type,
                                "name": trend_name
                            }
                        })
                        
                        plan["rationale"][f"new_role:{role}"] = f"New role recommended due to trending {trend_type}: {trend_name}"
            
            # Adjust related behaviors
            for behavior in trend_behavior_map.get(trend_type, []):
                # Check if behavior is already in the plan
                existing_change = next(
                    (b for b in plan["recommended_behavior_changes"] if b["behavior"] == behavior),
                    None
                )
                
                if existing_change:
                    # Update existing change with trend information
                    existing_change["trend_influenced"] = True
                    existing_change["trend_info"] = {
                        "type": trend_type,
                        "name": trend_name
                    }
                    
                    # Update rationale
                    behavior_rationale = plan["rationale"].get(f"behavior:{behavior}", "")
                    plan["rationale"][f"behavior:{behavior}"] = f"{behavior_rationale}\nInfluenced by trending {trend_type}: {trend_name}"
                else:
                    # Get current behavior level
                    current_level = artist_profile.get("behavior_patterns", {}).get(behavior, 0.5)
                    
                    # Add new behavior change
                    plan["recommended_behavior_changes"].append({
                        "behavior": behavior,
                        "current_level": current_level,
                        "recommended_level": min(1.0, current_level + 0.2),
                        "confidence": "medium",
                        "expected_impact": "positive",
                        "trend_influenced": True,
                        "trend_info": {
                            "type": trend_type,
                            "name": trend_name
                        }
                    })
                    
                    plan["rationale"][f"behavior:{behavior}"] = f"Increase recommended due to trending {trend_type}: {trend_name}"

    def _generate_implementation_steps(
        self,
        plan: Dict[str, Any],
        artist_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate implementation steps for the optimization plan.
        
        Args:
            plan: The optimization plan
            artist_profile: The artist's profile
            
        Returns:
            List of implementation steps
        """
        steps = []
        
        # Add steps for role changes
        for i, change in enumerate(plan["recommended_role_changes"]):
            steps.append({
                "step_number": len(steps) + 1,
                "type": "role_adjustment",
                "description": f"Adjust emphasis of '{change['role']}' role from {change['current_emphasis']} to {change['recommended_emphasis']}",
                "implementation_details": self._get_role_implementation_details(change, artist_profile),
                "priority": "high" if change["confidence"] == "high" else "medium"
            })
        
        # Add steps for behavior changes
        for i, change in enumerate(plan["recommended_behavior_changes"]):
            steps.append({
                "step_number": len(steps) + 1,
                "type": "behavior_adjustment",
                "description": f"Adjust '{change['behavior']}' behavior from level {change['current_level']} to {change['recommended_level']}",
                "implementation_details": self._get_behavior_implementation_details(change, artist_profile),
                "priority": "high" if change["confidence"] == "high" else "medium"
            })
        
        # Add steps for new roles
        for i, new_role in enumerate(plan["new_role_recommendations"]):
            steps.append({
                "step_number": len(steps) + 1,
                "type": "new_role",
                "description": f"Add new '{new_role['role']}' role with {new_role['recommended_emphasis']} emphasis",
                "implementation_details": self._get_new_role_implementation_details(new_role, artist_profile),
                "priority": "medium"  # New roles are typically medium priority
            })
        
        # Sort steps by priority
        steps.sort(key=lambda x: 0 if x["priority"] == "high" else 1)
        
        # Update step numbers after sorting
        for i, step in enumerate(steps):
            step["step_number"] = i + 1
        
        return steps

    def _get_role_implementation_details(
        self,
        change: Dict[str, Any],
        artist_profile: Dict[str, Any]
    ) -> str:
        """
        Generate implementation details for a role adjustment.
        
        Args:
            change: The role change
            artist_profile: The artist's profile
            
        Returns:
            Implementation details text
        """
        role = change["role"]
        emphasis = change["recommended_emphasis"]
        role_def = self.role_definitions.get(role, {})
        
        details = f"Implementation details for adjusting the '{role}' role:\n\n"
        
        if emphasis == "emphasized":
            details += "1. Increase prominence of this role in artist communications\n"
            details += "2. Highlight this aspect in upcoming content\n"
            details += f"3. Incorporate more {role}-specific elements in creative output\n"
            
            # Add role-specific implementation details
            if "emphasis_implementation" in role_def:
                details += "\nSpecific actions:\n"
                for action in role_def["emphasis_implementation"]:
                    details += f"- {action}\n"
        
        elif emphasis == "de-emphasized":
            details += "1. Reduce prominence of this role in artist communications\n"
            details += "2. Focus on other roles in upcoming content\n"
            details += f"3. Gradually reduce {role}-specific elements in creative output\n"
            
            # Add role-specific implementation details
            if "de_emphasis_implementation" in role_def:
                details += "\nSpecific actions:\n"
                for action in role_def["de_emphasis_implementation"]:
                    details += f"- {action}\n"
        
        return details

    def _get_behavior_implementation_details(
        self,
        change: Dict[str, Any],
        artist_profile: Dict[str, Any]
    ) -> str:
        """
        Generate implementation details for a behavior adjustment.
        
        Args:
            change: The behavior change
            artist_profile: The artist's profile
            
        Returns:
            Implementation details text
        """
        behavior = change["behavior"]
        current_level = change["current_level"]
        recommended_level = change["recommended_level"]
        behavior_def = self.behavior_patterns.get(behavior, {})
        
        details = f"Implementation details for adjusting the '{behavior}' behavior:\n\n"
        
        if recommended_level > current_level:
            details += f"1. Increase '{behavior}' behavior from level {current_level} to {recommended_level}\n"
            details += "2. Gradually implement changes over the next content cycle\n"
            details += f"3. Monitor audience response to increased {behavior}\n"
            
            # Add behavior-specific implementation details
            if "increase_implementation" in behavior_def:
                details += "\nSpecific actions:\n"
                for action in behavior_def["increase_implementation"]:
                    details += f"- {action}\n"
        
        else:
            details += f"1. Decrease '{behavior}' behavior from level {current_level} to {recommended_level}\n"
            details += "2. Gradually implement changes over the next content cycle\n"
            details += f"3. Monitor audience response to decreased {behavior}\n"
            
            # Add behavior-specific implementation details
            if "decrease_implementation" in behavior_def:
                details += "\nSpecific actions:\n"
                for action in behavior_def["decrease_implementation"]:
                    details += f"- {action}\n"
        
        return details

    def _get_new_role_implementation_details(
        self,
        new_role: Dict[str, Any],
        artist_profile: Dict[str, Any]
    ) -> str:
        """
        Generate implementation details for adding a new role.
        
        Args:
            new_role: The new role
            artist_profile: The artist's profile
            
        Returns:
            Implementation details text
        """
        role = new_role["role"]
        emphasis = new_role["recommended_emphasis"]
        role_def = self.role_definitions.get(role, {})
        
        details = f"Implementation details for adding the new '{role}' role:\n\n"
        details += "1. Introduce this role gradually in artist communications\n"
        details += "2. Develop content that showcases this new aspect\n"
        details += f"3. Incorporate {role}-specific elements in upcoming creative output\n"
        
        # Add role-specific implementation details
        if "introduction_implementation" in role_def:
            details += "\nSpecific actions:\n"
            for action in role_def["introduction_implementation"]:
                details += f"- {action}\n"
        
        return details

    def _generate_optimization_summary(self, plan: Dict[str, Any]) -> str:
        """
        Generate a summary of the optimization plan.
        
        Args:
            plan: The optimization plan
            
        Returns:
            Summary text
        """
        role_changes = len(plan["recommended_role_changes"])
        behavior_changes = len(plan["recommended_behavior_changes"])
        new_roles = len(plan["new_role_recommendations"])
        
        summary = f"Optimization plan with {role_changes} role adjustments, "
        summary += f"{behavior_changes} behavior adjustments, and {new_roles} new roles. "
        
        # Add high-priority changes
        high_priority_changes = [
            change for change in plan["recommended_role_changes"] 
            if change.get("confidence") == "high"
        ]
        high_priority_changes.extend([
            change for change in plan["recommended_behavior_changes"] 
            if change.get("confidence") == "high"
        ])
        
        if high_priority_changes:
            summary += f"High-priority changes include: "
            
            for i, change in enumerate(high_priority_changes[:3]):  # Limit to 3 for brevity
                if "role" in change:
                    summary += f"{change['role']} role ({change['recommended_emphasis']})"
                else:
                    summary += f"{change['behavior']} behavior (level {change['recommended_level']})"
                
                if i < len(high_priority_changes[:3]) - 1:
                    summary += ", "
            
            if len(high_priority_changes) > 3:
                summary += f", and {len(high_priority_changes) - 3} more"
        
        return summary

    def _load_default_role_definitions(self) -> None:
        """Load default role definitions."""
        self.role_definitions = {
            "innovator": {
                "description": "Pushes boundaries and introduces new ideas",
                "relevant_metrics": [
                    "engagement.average_shares",
                    "content.song_performance.innovation_score"
                ],
                "metric_ranges": {
                    "engagement.average_shares": {"min": 0, "max": 1000},
                    "content.song_performance.innovation_score": {"min": 0, "max": 10}
                },
                "related_themes": ["innovation", "experimental", "unique", "fresh"],
                "emphasis_implementation": [
                    "Incorporate more experimental elements in upcoming tracks",
                    "Highlight innovative aspects in promotional materials",
                    "Collaborate with other innovative artists"
                ],
                "de_emphasis_implementation": [
                    "Focus on more accessible elements in upcoming tracks",
                    "Emphasize consistency and reliability in promotional materials"
                ],
                "introduction_implementation": [
                    "Begin with subtle experimental elements in upcoming tracks",
                    "Introduce innovative aspects gradually in promotional materials",
                    "Start small collaborations with innovative artists"
                ]
            },
            "trendsetter": {
                "description": "Leads and influences trends in music and culture",
                "relevant_metrics": [
                    "engagement.follower_growth_rate",
                    "content.post_performance.trend_influence_score"
                ],
                "metric_ranges": {
                    "engagement.follower_growth_rate": {"min": 0, "max": 0.2},
                    "content.post_performance.trend_influence_score": {"min": 0, "max": 10}
                },
                "related_themes": ["trendy", "influential", "cutting-edge", "popular"],
                "emphasis_implementation": [
                    "Increase early adoption of emerging trends",
                    "Be more bold and definitive in style choices",
                    "Increase frequency of style updates and evolution"
                ],
                "de_emphasis_implementation": [
                    "Focus on timeless elements rather than trends",
                    "Emphasize authenticity over trend-following"
                ],
                "introduction_implementation": [
                    "Begin incorporating current trends in a unique way",
                    "Develop a signature take on popular styles",
                    "Start monitoring trend forecasts more closely"
                ]
            },
            "storyteller": {
                "description": "Focuses on narrative and emotional storytelling",
                "relevant_metrics": [
                    "engagement.average_comments",
                    "content.song_performance.lyrical_impact_score"
                ],
                "metric_ranges": {
                    "engagement.average_comments": {"min": 0, "max": 500},
                    "content.song_performance.lyrical_impact_score": {"min": 0, "max": 10}
                },
                "related_themes": ["narrative", "emotional", "lyrical", "meaningful"],
                "emphasis_implementation": [
                    "Develop more cohesive narratives across releases",
                    "Emphasize lyrical content in promotional materials",
                    "Create more content that explains the stories behind songs"
                ],
                "de_emphasis_implementation": [
                    "Focus more on sound and production than narrative",
                    "Simplify lyrical content to be more accessible"
                ],
                "introduction_implementation": [
                    "Begin incorporating narrative elements in upcoming releases",
                    "Start sharing the stories behind creative decisions",
                    "Develop a narrative arc for the next release cycle"
                ]
            },
            "visual_artist": {
                "description": "Emphasizes visual aesthetics and artistic presentation",
                "relevant_metrics": [
                    "engagement.average_likes",
                    "content.video_performance.visual_quality_score"
                ],
                "metric_ranges": {
                    "engagement.average_likes": {"min": 0, "max": 2000},
                    "content.video_performance.visual_quality_score": {"min": 0, "max": 10}
                },
                "related_themes": ["visual", "aesthetic", "artistic", "cinematic"],
                "emphasis_implementation": [
                    "Increase investment in visual content production",
                    "Develop more cohesive visual identity across platforms",
                    "Collaborate with visual artists and directors"
                ],
                "de_emphasis_implementation": [
                    "Focus more on audio quality than visual presentation",
                    "Simplify visual approach to reduce production complexity"
                ],
                "introduction_implementation": [
                    "Begin developing a consistent visual aesthetic",
                    "Start incorporating more thoughtful visual elements",
                    "Plan a visual identity evolution over the next quarter"
                ]
            },
            "social_commentator": {
                "description": "Addresses social issues and cultural commentary",
                "relevant_metrics": [
                    "engagement.average_shares",
                    "content.post_performance.social_impact_score"
                ],
                "metric_ranges": {
                    "engagement.average_shares": {"min": 0, "max": 1000},
                    "content.post_performance.social_impact_score": {"min": 0, "max": 10}
                },
                "related_themes": ["political", "social", "commentary", "conscious"],
                "emphasis_implementation": [
                    "Incorporate more social commentary in upcoming content",
                    "Engage more directly with current social issues",
                    "Collaborate with activists and social organizations"
                ],
                "de_emphasis_implementation": [
                    "Focus more on personal themes than social commentary",
                    "Address social issues more subtly and indirectly"
                ],
                "introduction_implementation": [
                    "Begin incorporating thoughtful commentary on select issues",
                    "Start engaging with social causes aligned with artist values",
                    "Develop a voice for addressing important topics authentically"
                ]
            }
        }

    def _load_default_behavior_patterns(self) -> None:
        """Load default behavior patterns."""
        self.behavior_patterns = {
            "authenticity": {
                "description": "Being genuine and true to artistic vision",
                "impact_metrics": [
                    "engagement.engagement_rate",
                    "audience_feedback.sentiment.overall_sentiment"
                ],
                "metric_ranges": {
                    "engagement.engagement_rate": {"min": 0, "max": 0.1},
                    "audience_feedback.sentiment.overall_sentiment": {"min": 0, "max": 1}
                },
                "impact_direction": {
                    "engagement.engagement_rate": 1,  # Positive impact
                    "audience_feedback.sentiment.overall_sentiment": 1  # Positive impact
                },
                "increase_implementation": [
                    "Share more behind-the-scenes content",
                    "Be more transparent about creative process",
                    "Express more personal opinions and perspectives"
                ],
                "decrease_implementation": [
                    "Focus more on polished, curated content",
                    "Maintain more professional distance in communications"
                ]
            },
            "consistency": {
                "description": "Maintaining consistent style, quality, and release schedule",
                "impact_metrics": [
                    "engagement.follower_growth_rate",
                    "content.song_performance.average_retention"
                ],
                "metric_ranges": {
                    "engagement.follower_growth_rate": {"min": 0, "max": 0.2},
                    "content.song_performance.average_retention": {"min": 0, "max": 1}
                },
                "impact_direction": {
                    "engagement.follower_growth_rate": 1,  # Positive impact
                    "content.song_performance.average_retention": 1  # Positive impact
                },
                "increase_implementation": [
                    "Establish more regular release schedule",
                    "Maintain more consistent visual and sonic identity",
                    "Standardize content quality across platforms"
                ],
                "decrease_implementation": [
                    "Allow for more spontaneity and variation",
                    "Experiment more with different styles and approaches"
                ]
            },
            "engagement": {
                "description": "Actively engaging with audience and community",
                "impact_metrics": [
                    "engagement.average_comments",
                    "engagement.engagement_rate"
                ],
                "metric_ranges": {
                    "engagement.average_comments": {"min": 0, "max": 500},
                    "engagement.engagement_rate": {"min": 0, "max": 0.1}
                },
                "impact_direction": {
                    "engagement.average_comments": 1,  # Positive impact
                    "engagement.engagement_rate": 1  # Positive impact
                },
                "increase_implementation": [
                    "Respond to more comments and messages",
                    "Host more interactive sessions with audience",
                    "Create more content that encourages participation"
                ],
                "decrease_implementation": [
                    "Focus more on content creation than audience interaction",
                    "Maintain more mystique and distance"
                ]
            },
            "experimentation": {
                "description": "Willingness to try new approaches and take risks",
                "impact_metrics": [
                    "content.song_performance.innovation_score",
                    "audience_feedback.sentiment.positive_comments_ratio"
                ],
                "metric_ranges": {
                    "content.song_performance.innovation_score": {"min": 0, "max": 10},
                    "audience_feedback.sentiment.positive_comments_ratio": {"min": 0, "max": 1}
                },
                "impact_direction": {
                    "content.song_performance.innovation_score": 1,  # Positive impact
                    "audience_feedback.sentiment.positive_comments_ratio": 0.5  # Mixed impact
                },
                "increase_implementation": [
                    "Try more new production techniques",
                    "Collaborate with artists from different genres",
                    "Incorporate more unexpected elements in content"
                ],
                "decrease_implementation": [
                    "Focus more on refining established style",
                    "Stick closer to proven formulas and approaches"
                ]
            },
            "vulnerability": {
                "description": "Sharing personal experiences and emotions",
                "impact_metrics": [
                    "engagement.average_comments",
                    "audience_feedback.sentiment.overall_sentiment"
                ],
                "metric_ranges": {
                    "engagement.average_comments": {"min": 0, "max": 500},
                    "audience_feedback.sentiment.overall_sentiment": {"min": 0, "max": 1}
                },
                "impact_direction": {
                    "engagement.average_comments": 1,  # Positive impact
                    "audience_feedback.sentiment.overall_sentiment": 0.7  # Mostly positive impact
                },
                "increase_implementation": [
                    "Share more personal stories and experiences",
                    "Express more emotional depth in content",
                    "Be more open about challenges and struggles"
                ],
                "decrease_implementation": [
                    "Focus more on universal themes than personal experiences",
                    "Maintain more emotional distance in content"
                ]
            }
        }
