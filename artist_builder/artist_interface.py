"""
Artist Creation Interface Module

This module provides a high-level interface for creating and evolving AI artists
with integrated trend analysis, role optimization, and LLM collaboration.
"""

import logging
import json
import os
import time
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from datetime import datetime
import uuid
from pathlib import Path

from ..trend_analyzer import TrendAnalyzer
from ..role_optimizer import RoleDynamicOptimizer
from ..llm_metrics import LLMMetrics
from ..llm_collaboration import LLMCollaboration
from ..schema import ArtistProfileSchema
from ..builder import ProfileBuilder, ProfileValidator, StorageManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.artist_interface")


class ArtistCreationError(Exception):
    """Exception raised for errors in the artist creation process."""
    pass


class ArtistCreationInterface:
    """
    High-level interface for creating and evolving AI artists.
    Integrates trend analysis, role optimization, and LLM collaboration.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the artist creation interface.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Initialize components
        self.trend_analyzer = TrendAnalyzer(self.config.get("trend_analyzer_config"))
        self.role_optimizer = RoleDynamicOptimizer(self.config.get("role_optimizer_config"))
        self.llm_metrics = LLMMetrics(self.config.get("llm_metrics_config"))
        self.llm_collaboration = LLMCollaboration(self.config.get("llm_collaboration_config"))
        self.profile_builder = ProfileBuilder(self.config.get("profile_builder_config"))
        self.profile_validator = ProfileValidator()
        self.storage_manager = StorageManager(self.config.get("storage_config"))
        
        # Set up base directories
        self.artists_dir = self.config.get("artists_dir", "artists")
        os.makedirs(self.artists_dir, exist_ok=True)
        
        logger.info("Initialized artist creation interface")

    def create_artist(
        self,
        artist_name: str,
        main_genre: str,
        subgenres: List[str],
        style_tags: List[str],
        vibe_description: str,
        target_audience: str,
        trend_sensitivity: float = 0.5,
        additional_params: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Create a new AI artist with trend analysis and role optimization.
        
        Args:
            artist_name: Name of the artist
            main_genre: Primary genre of the artist
            subgenres: List of subgenres
            style_tags: List of style tags
            vibe_description: Description of the artist's vibe
            target_audience: Description of the target audience
            trend_sensitivity: How much to incorporate current trends (0.0-1.0)
            additional_params: Optional additional parameters
            callback: Optional callback function for progress updates
            
        Returns:
            Dictionary containing the created artist profile
        """
        try:
            # Start tracking LLM metrics
            tracking_id = self.llm_metrics.start_tracking(
                module="artist_interface",
                operation="create_artist",
                metadata={
                    "artist_name": artist_name,
                    "main_genre": main_genre,
                    "trend_sensitivity": trend_sensitivity
                }
            )
            
            # Notify callback if provided
            if callback:
                callback({
                    "status": "started",
                    "message": f"Starting creation of artist: {artist_name}",
                    "progress": 0.0
                })
            
            # Analyze current trends
            logger.info(f"Analyzing trends for new artist: {artist_name}")
            trend_data = self.trend_analyzer.analyze_trends(
                main_genre=main_genre,
                subgenres=subgenres,
                style_tags=style_tags
            )
            
            # Notify callback
            if callback:
                callback({
                    "status": "in_progress",
                    "message": "Analyzed current trends",
                    "progress": 0.2,
                    "trend_data": trend_data
                })
            
            # Optimize roles based on trends and artist parameters
            logger.info(f"Optimizing roles for new artist: {artist_name}")
            role_config = self.role_optimizer.optimize_roles(
                artist_name=artist_name,
                main_genre=main_genre,
                subgenres=subgenres,
                style_tags=style_tags,
                vibe_description=vibe_description,
                target_audience=target_audience,
                trend_data=trend_data,
                trend_sensitivity=trend_sensitivity
            )
            
            # Notify callback
            if callback:
                callback({
                    "status": "in_progress",
                    "message": "Optimized artist roles",
                    "progress": 0.4,
                    "role_config": role_config
                })
            
            # Prepare parameters for profile builder
            builder_params = {
                "artist_name": artist_name,
                "main_genre": main_genre,
                "subgenres": subgenres,
                "style_tags": style_tags,
                "vibe_description": vibe_description,
                "target_audience": target_audience,
                "trend_data": trend_data,
                "role_config": role_config
            }
            
            # Add additional parameters if provided
            if additional_params:
                builder_params.update(additional_params)
            
            # Create collaboration session for artist creation
            collab_session_id = self.llm_collaboration.create_collaboration_session(
                session_name=f"Creation of artist: {artist_name}",
                roles=["creator", "critic", "refiner", "audience", "technical"],
                context=builder_params
            )
            
            # Run initial collaboration round to generate artist profile
            logger.info(f"Generating initial profile for artist: {artist_name}")
            collab_result = self.llm_collaboration.run_collaboration_round(
                session_id=collab_session_id,
                prompt=self._generate_artist_creation_prompt(builder_params),
                round_type="sequential",
                max_iterations=2
            )
            
            # Extract artist profile from collaboration result
            initial_profile_text = collab_result["final_result"]["result"]
            
            # Notify callback
            if callback:
                callback({
                    "status": "in_progress",
                    "message": "Generated initial artist profile",
                    "progress": 0.6,
                    "initial_profile": initial_profile_text
                })
            
            # Parse and validate the profile
            try:
                # Convert text to structured profile
                initial_profile = self.profile_builder.build_profile_from_text(initial_profile_text)
                
                # Validate the profile
                validation_result = self.profile_validator.validate(initial_profile)
                
                if not validation_result["valid"]:
                    logger.warning(f"Initial profile validation failed: {validation_result['errors']}")
                    
                    # Try to fix the profile
                    fixed_profile = self.profile_builder.fix_profile(
                        initial_profile, validation_result["errors"]
                    )
                    
                    # Validate again
                    validation_result = self.profile_validator.validate(fixed_profile)
                    
                    if not validation_result["valid"]:
                        raise ArtistCreationError(f"Failed to create valid artist profile: {validation_result['errors']}")
                    
                    initial_profile = fixed_profile
            
            except Exception as e:
                logger.error(f"Error parsing or validating profile: {str(e)}")
                
                # Fall back to using the profile builder directly
                logger.info("Falling back to direct profile builder")
                initial_profile = self.profile_builder.build_profile(builder_params)
            
            # Notify callback
            if callback:
                callback({
                    "status": "in_progress",
                    "message": "Validated artist profile",
                    "progress": 0.7,
                    "validation_result": validation_result
                })
            
            # Create review session for the profile
            review_session_id = self.llm_collaboration.create_review_session(
                content=json.dumps(initial_profile, indent=2),
                content_type="artist_profile",
                reviewer_roles=["critic", "audience", "technical"]
            )
            
            # Run peer review
            logger.info(f"Running peer review for artist: {artist_name}")
            review_result = self.llm_collaboration.run_peer_review(
                review_session_id=review_session_id
            )
            
            # Notify callback
            if callback:
                callback({
                    "status": "in_progress",
                    "message": "Completed peer review",
                    "progress": 0.8,
                    "review_result": review_result
                })
            
            # Apply review feedback to improve the profile
            improved_profile = self._apply_review_feedback(
                initial_profile, review_result["consensus"]["review"]
            )
            
            # Generate artist slug
            artist_slug = self._generate_artist_slug(artist_name)
            
            # Add metadata to the profile
            improved_profile["metadata"] = improved_profile.get("metadata", {})
            improved_profile["metadata"].update({
                "created_at": datetime.now().isoformat(),
                "trend_sensitivity": trend_sensitivity,
                "trend_data": trend_data,
                "role_config": role_config,
                "review_session_id": review_session_id,
                "artist_slug": artist_slug
            })
            
            # Save the artist profile
            logger.info(f"Saving profile for artist: {artist_name}")
            save_result = self.storage_manager.save_artist_profile(
                artist_slug=artist_slug,
                profile=improved_profile
            )
            
            # Create artist directory structure
            self._create_artist_directory_structure(artist_slug)
            
            # End tracking LLM metrics
            self.llm_metrics.end_tracking(
                tracking_id=tracking_id,
                model="multiple",
                prompt_tokens=collab_result["final_result"]["total_tokens"],
                completion_tokens=0,
                success=True,
                additional_metadata={
                    "artist_slug": artist_slug,
                    "review_session_id": review_session_id
                }
            )
            
            # Prepare result
            result = {
                "artist_name": artist_name,
                "artist_slug": artist_slug,
                "profile": improved_profile,
                "save_path": save_result["save_path"],
                "trend_data": trend_data,
                "role_config": role_config,
                "review_result": review_result,
                "created_at": datetime.now().isoformat()
            }
            
            # Notify callback
            if callback:
                callback({
                    "status": "completed",
                    "message": f"Successfully created artist: {artist_name}",
                    "progress": 1.0,
                    "result": result
                })
            
            logger.info(f"Successfully created artist: {artist_name} ({artist_slug})")
            return result
            
        except Exception as e:
            logger.error(f"Error creating artist {artist_name}: {str(e)}")
            
            # End tracking with error
            if 'tracking_id' in locals():
                self.llm_metrics.end_tracking(
                    tracking_id=tracking_id,
                    model="multiple",
                    prompt_tokens=0,
                    completion_tokens=0,
                    success=False,
                    additional_metadata={"error": str(e)}
                )
            
            # Notify callback
            if callback:
                callback({
                    "status": "error",
                    "message": f"Error creating artist: {str(e)}",
                    "error": str(e)
                })
            
            raise ArtistCreationError(f"Failed to create artist {artist_name}: {str(e)}")

    def evolve_artist(
        self,
        artist_slug: str,
        evolution_strength: float = 0.3,
        trend_sensitivity: float = 0.5,
        target_aspects: Optional[List[str]] = None,
        additional_params: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Evolve an existing AI artist based on trends and feedback.
        
        Args:
            artist_slug: Slug of the artist to evolve
            evolution_strength: How strongly to evolve the artist (0.0-1.0)
            trend_sensitivity: How much to incorporate current trends (0.0-1.0)
            target_aspects: Optional list of specific aspects to evolve
            additional_params: Optional additional parameters
            callback: Optional callback function for progress updates
            
        Returns:
            Dictionary containing the evolved artist profile
        """
        try:
            # Start tracking LLM metrics
            tracking_id = self.llm_metrics.start_tracking(
                module="artist_interface",
                operation="evolve_artist",
                artist_id=artist_slug,
                metadata={
                    "artist_slug": artist_slug,
                    "evolution_strength": evolution_strength,
                    "trend_sensitivity": trend_sensitivity
                }
            )
            
            # Notify callback if provided
            if callback:
                callback({
                    "status": "started",
                    "message": f"Starting evolution of artist: {artist_slug}",
                    "progress": 0.0
                })
            
            # Load the current artist profile
            logger.info(f"Loading profile for artist: {artist_slug}")
            current_profile = self.storage_manager.load_artist_profile(artist_slug)
            
            if not current_profile:
                raise ArtistCreationError(f"Artist not found: {artist_slug}")
            
            # Extract basic information
            artist_name = current_profile.get("name", artist_slug)
            main_genre = current_profile.get("genre", {}).get("main", "")
            subgenres = current_profile.get("genre", {}).get("subgenres", [])
            style_tags = current_profile.get("style_tags", [])
            
            # Notify callback
            if callback:
                callback({
                    "status": "in_progress",
                    "message": f"Loaded profile for artist: {artist_name}",
                    "progress": 0.1,
                    "current_profile": current_profile
                })
            
            # Analyze current trends
            logger.info(f"Analyzing trends for artist evolution: {artist_name}")
            trend_data = self.trend_analyzer.analyze_trends(
                main_genre=main_genre,
                subgenres=subgenres,
                style_tags=style_tags
            )
            
            # Analyze trend compatibility with the artist
            compatibility = self.trend_analyzer.analyze_artist_compatibility(
                artist_profile=current_profile,
                trend_data=trend_data
            )
            
            # Notify callback
            if callback:
                callback({
                    "status": "in_progress",
                    "message": "Analyzed current trends and compatibility",
                    "progress": 0.3,
                    "trend_data": trend_data,
                    "compatibility": compatibility
                })
            
            # Determine which aspects to evolve
            if not target_aspects:
                # Automatically determine based on compatibility
                target_aspects = self._determine_evolution_targets(
                    compatibility, evolution_strength
                )
            
            # Optimize roles based on trends and evolution targets
            logger.info(f"Optimizing roles for artist evolution: {artist_name}")
            role_config = self.role_optimizer.optimize_roles(
                artist_name=artist_name,
                main_genre=main_genre,
                subgenres=subgenres,
                style_tags=style_tags,
                vibe_description=current_profile.get("vibe", ""),
                target_audience=current_profile.get("target_audience", ""),
                trend_data=trend_data,
                trend_sensitivity=trend_sensitivity,
                current_profile=current_profile,
                evolution_targets=target_aspects
            )
            
            # Notify callback
            if callback:
                callback({
                    "status": "in_progress",
                    "message": "Optimized artist roles for evolution",
                    "progress": 0.4,
                    "role_config": role_config,
                    "target_aspects": target_aspects
                })
            
            # Prepare parameters for evolution
            evolution_params = {
                "artist_name": artist_name,
                "artist_slug": artist_slug,
                "current_profile": current_profile,
                "trend_data": trend_data,
                "compatibility": compatibility,
                "target_aspects": target_aspects,
                "evolution_strength": evolution_strength,
                "trend_sensitivity": trend_sensitivity,
                "role_config": role_config
            }
            
            # Add additional parameters if provided
            if additional_params:
                evolution_params.update(additional_params)
            
            # Create collaboration session for artist evolution
            collab_session_id = self.llm_collaboration.create_collaboration_session(
                session_name=f"Evolution of artist: {artist_name}",
                roles=["creator", "critic", "refiner", "audience", "technical"],
                context=evolution_params
            )
            
            # Run collaboration round to generate evolved profile
            logger.info(f"Generating evolved profile for artist: {artist_name}")
            collab_result = self.llm_collaboration.run_collaboration_round(
                session_id=collab_session_id,
                prompt=self._generate_artist_evolution_prompt(evolution_params),
                round_type="debate",
                max_iterations=2
            )
            
            # Extract evolved profile from collaboration result
            evolved_profile_text = collab_result["final_result"]["result"]
            
            # Notify callback
            if callback:
                callback({
                    "status": "in_progress",
                    "message": "Generated evolved artist profile",
                    "progress": 0.6,
                    "evolved_profile_text": evolved_profile_text
                })
            
            # Parse and validate the evolved profile
            try:
                # Convert text to structured profile
                evolved_profile = self.profile_builder.build_profile_from_text(evolved_profile_text)
                
                # Validate the profile
                validation_result = self.profile_validator.validate(evolved_profile)
                
                if not validation_result["valid"]:
                    logger.warning(f"Evolved profile validation failed: {validation_result['errors']}")
                    
                    # Try to fix the profile
                    fixed_profile = self.profile_builder.fix_profile(
                        evolved_profile, validation_result["errors"]
                    )
                    
                    # Validate again
                    validation_result = self.profile_validator.validate(fixed_profile)
                    
                    if not validation_result["valid"]:
                        raise ArtistCreationError(f"Failed to create valid evolved profile: {validation_result['errors']}")
                    
                    evolved_profile = fixed_profile
            
            except Exception as e:
                logger.error(f"Error parsing or validating evolved profile: {str(e)}")
                
                # Fall back to modifying the current profile directly
                logger.info("Falling back to direct profile modification")
                evolved_profile = self._evolve_profile_directly(
                    current_profile, trend_data, target_aspects, evolution_strength
                )
            
            # Notify callback
            if callback:
                callback({
                    "status": "in_progress",
                    "message": "Validated evolved artist profile",
                    "progress": 0.7,
                    "validation_result": validation_result
                })
            
            # Create review session for the evolved profile
            review_session_id = self.llm_collaboration.create_review_session(
                content=json.dumps(evolved_profile, indent=2),
                content_type="artist_profile",
                artist_id=artist_slug,
                reviewer_roles=["critic", "audience", "technical"]
            )
            
            # Run peer review
            logger.info(f"Running peer review for evolved artist: {artist_name}")
            review_result = self.llm_collaboration.run_peer_review(
                review_session_id=review_session_id
            )
            
            # Notify callback
            if callback:
                callback({
                    "status": "in_progress",
                    "message": "Completed peer review of evolved profile",
                    "progress": 0.8,
                    "review_result": review_result
                })
            
            # Apply review feedback to improve the profile
            final_profile = self._apply_review_feedback(
                evolved_profile, review_result["consensus"]["review"]
            )
            
            # Add evolution metadata to the profile
            final_profile["metadata"] = final_profile.get("metadata", {})
            final_profile["metadata"].update({
                "evolved_at": datetime.now().isoformat(),
                "evolution_strength": evolution_strength,
                "trend_sensitivity": trend_sensitivity,
                "target_aspects": target_aspects,
                "trend_data": trend_data,
                "compatibility": compatibility,
                "role_config": role_config,
                "review_session_id": review_session_id,
                "previous_version": current_profile.get("metadata", {}).get("version", 0) + 1
            })
            
            # Save the evolved artist profile
            logger.info(f"Saving evolved profile for artist: {artist_name}")
            save_result = self.storage_manager.save_artist_profile(
                artist_slug=artist_slug,
                profile=final_profile,
                create_version=True
            )
            
            # End tracking LLM metrics
            self.llm_metrics.end_tracking(
                tracking_id=tracking_id,
                model="multiple",
                prompt_tokens=collab_result["final_result"]["total_tokens"],
                completion_tokens=0,
                success=True,
                additional_metadata={
                    "artist_slug": artist_slug,
                    "review_session_id": review_session_id,
                    "target_aspects": target_aspects
                }
            )
            
            # Prepare result
            result = {
                "artist_name": artist_name,
                "artist_slug": artist_slug,
                "original_profile": current_profile,
                "evolved_profile": final_profile,
                "save_path": save_result["save_path"],
                "trend_data": trend_data,
                "compatibility": compatibility,
                "target_aspects": target_aspects,
                "role_config": role_config,
                "review_result": review_result,
                "evolved_at": datetime.now().isoformat()
            }
            
            # Notify callback
            if callback:
                callback({
                    "status": "completed",
                    "message": f"Successfully evolved artist: {artist_name}",
                    "progress": 1.0,
                    "result": result
                })
            
            logger.info(f"Successfully evolved artist: {artist_name} ({artist_slug})")
            return result
            
        except Exception as e:
            logger.error(f"Error evolving artist {artist_slug}: {str(e)}")
            
            # End tracking with error
            if 'tracking_id' in locals():
                self.llm_metrics.end_tracking(
                    tracking_id=tracking_id,
                    model="multiple",
                    prompt_tokens=0,
                    completion_tokens=0,
                    success=False,
                    additional_metadata={"error": str(e)}
                )
            
            # Notify callback
            if callback:
                callback({
                    "status": "error",
                    "message": f"Error evolving artist: {str(e)}",
                    "error": str(e)
                })
            
            raise ArtistCreationError(f"Failed to evolve artist {artist_slug}: {str(e)}")

    def get_artist_analytics(
        self,
        artist_slug: str,
        include_llm_metrics: bool = True,
        include_trend_data: bool = True,
        include_review_history: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics for an artist.
        
        Args:
            artist_slug: Slug of the artist
            include_llm_metrics: Whether to include LLM metrics
            include_trend_data: Whether to include trend data
            include_review_history: Whether to include review history
            
        Returns:
            Dictionary containing artist analytics
        """
        try:
            # Load the artist profile
            profile = self.storage_manager.load_artist_profile(artist_slug)
            
            if not profile:
                raise ArtistCreationError(f"Artist not found: {artist_slug}")
            
            # Initialize analytics result
            analytics = {
                "artist_slug": artist_slug,
                "artist_name": profile.get("name", artist_slug),
                "profile": profile,
                "creation_date": profile.get("metadata", {}).get("created_at"),
                "last_evolution": profile.get("metadata", {}).get("evolved_at"),
                "version": profile.get("metadata", {}).get("version", 1)
            }
            
            # Get version history
            analytics["version_history"] = self.storage_manager.get_artist_version_history(artist_slug)
            
            # Include LLM metrics if requested
            if include_llm_metrics:
                analytics["llm_metrics"] = self.llm_metrics.get_artist_efficiency_metrics(artist_slug)
            
            # Include trend data if requested
            if include_trend_data:
                # Get current trend data
                main_genre = profile.get("genre", {}).get("main", "")
                subgenres = profile.get("genre", {}).get("subgenres", [])
                style_tags = profile.get("style_tags", [])
                
                current_trends = self.trend_analyzer.analyze_trends(
                    main_genre=main_genre,
                    subgenres=subgenres,
                    style_tags=style_tags
                )
                
                # Get compatibility with current trends
                compatibility = self.trend_analyzer.analyze_artist_compatibility(
                    artist_profile=profile,
                    trend_data=current_trends
                )
                
                analytics["trend_data"] = {
                    "current_trends": current_trends,
                    "compatibility": compatibility,
                    "historical_trends": profile.get("metadata", {}).get("trend_data", {})
                }
            
            # Include review history if requested
            if include_review_history:
                review_sessions = self.llm_collaboration.get_review_sessions_for_artist(artist_slug)
                analytics["review_history"] = review_sessions
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics for artist {artist_slug}: {str(e)}")
            raise ArtistCreationError(f"Failed to get analytics for artist {artist_slug}: {str(e)}")

    def _generate_artist_creation_prompt(self, params: Dict[str, Any]) -> str:
        """
        Generate a prompt for artist creation.
        
        Args:
            params: Parameters for the prompt
            
        Returns:
            Formatted prompt string
        """
        return f"""
        Create a detailed AI artist profile with the following characteristics:
        
        Name: {params['artist_name']}
        Main Genre: {params['main_genre']}
        Subgenres: {', '.join(params['subgenres'])}
        Style Tags: {', '.join(params['style_tags'])}
        Vibe Description: {params['vibe_description']}
        Target Audience: {params['target_audience']}
        
        Current Trends to Consider:
        {json.dumps(params['trend_data'], indent=2)}
        
        Role Configuration:
        {json.dumps(params['role_config'], indent=2)}
        
        Create a comprehensive artist profile that includes:
        1. Detailed background story and persona
        2. Musical style and influences
        3. Visual aesthetic and branding
        4. Lyrical themes and content approach
        5. Performance style and audience interaction
        6. Production techniques and sonic characteristics
        7. Marketing approach and platform strategy
        
        The profile should be coherent, distinctive, and marketable while incorporating
        relevant current trends. Make sure the artist has a unique identity that stands
        out in the current music landscape.
        
        Format the response as a structured profile that can be parsed into JSON.
        """

    def _generate_artist_evolution_prompt(self, params: Dict[str, Any]) -> str:
        """
        Generate a prompt for artist evolution.
        
        Args:
            params: Parameters for the prompt
            
        Returns:
            Formatted prompt string
        """
        # Format target aspects as a readable list
        target_aspects_text = "\n".join([f"- {aspect}" for aspect in params['target_aspects']])
        
        return f"""
        Evolve the existing AI artist profile with the following parameters:
        
        Artist Name: {params['artist_name']}
        Evolution Strength: {params['evolution_strength']} (0.0-1.0)
        Trend Sensitivity: {params['trend_sensitivity']} (0.0-1.0)
        
        Current Profile:
        {json.dumps(params['current_profile'], indent=2)}
        
        Current Trends:
        {json.dumps(params['trend_data'], indent=2)}
        
        Trend Compatibility Analysis:
        {json.dumps(params['compatibility'], indent=2)}
        
        Target Aspects to Evolve:
        {target_aspects_text}
        
        Role Configuration:
        {json.dumps(params['role_config'], indent=2)}
        
        Create an evolved version of this artist profile that:
        1. Maintains the core identity and recognizability of the artist
        2. Evolves the specified target aspects to better align with current trends
        3. Ensures the evolution feels organic and authentic to the artist's established persona
        4. Balances commercial appeal with artistic integrity
        5. Considers the artist's existing audience while potentially expanding appeal
        
        The evolution should respect the specified evolution strength (how dramatic the changes should be)
        and trend sensitivity (how much to incorporate current trends).
        
        Format the response as a structured profile that can be parsed into JSON.
        """

    def _apply_review_feedback(
        self,
        profile: Dict[str, Any],
        review: str
    ) -> Dict[str, Any]:
        """
        Apply review feedback to improve an artist profile.
        
        Args:
            profile: The artist profile to improve
            review: The review feedback
            
        Returns:
            Improved artist profile
        """
        # This is a placeholder implementation
        # In a real implementation, this would parse the review and apply specific changes
        
        # For now, just add the review to the profile metadata
        improved_profile = profile.copy()
        improved_profile["metadata"] = improved_profile.get("metadata", {})
        improved_profile["metadata"]["review_feedback"] = review
        
        return improved_profile

    def _determine_evolution_targets(
        self,
        compatibility: Dict[str, Any],
        evolution_strength: float
    ) -> List[str]:
        """
        Determine which aspects of an artist profile to evolve based on trend compatibility.
        
        Args:
            compatibility: Trend compatibility analysis
            evolution_strength: How strongly to evolve the artist (0.0-1.0)
            
        Returns:
            List of aspects to target for evolution
        """
        # Extract compatibility scores for different aspects
        aspect_scores = compatibility.get("aspect_scores", {})
        
        # Sort aspects by compatibility score (ascending, so least compatible first)
        sorted_aspects = sorted(
            aspect_scores.items(),
            key=lambda x: x[1]
        )
        
        # Determine how many aspects to evolve based on evolution strength
        # Stronger evolution means more aspects will be targeted
        num_aspects = max(1, int(len(sorted_aspects) * evolution_strength))
        
        # Select the least compatible aspects
        target_aspects = [aspect for aspect, score in sorted_aspects[:num_aspects]]
        
        return target_aspects

    def _evolve_profile_directly(
        self,
        profile: Dict[str, Any],
        trend_data: Dict[str, Any],
        target_aspects: List[str],
        evolution_strength: float
    ) -> Dict[str, Any]:
        """
        Directly evolve an artist profile without using LLM collaboration.
        
        Args:
            profile: The current artist profile
            trend_data: Current trend data
            target_aspects: Aspects to evolve
            evolution_strength: How strongly to evolve the artist (0.0-1.0)
            
        Returns:
            Evolved artist profile
        """
        # This is a fallback implementation for when the LLM-based evolution fails
        # It makes simple, direct modifications to the profile based on trends
        
        evolved_profile = profile.copy()
        
        # Apply simple evolutions based on target aspects
        for aspect in target_aspects:
            if aspect == "genre":
                # Incorporate trending subgenres
                if "trending_genres" in trend_data:
                    current_subgenres = set(evolved_profile.get("genre", {}).get("subgenres", []))
                    trending_subgenres = set(trend_data["trending_genres"][:3])
                    
                    # Add some trending subgenres based on evolution strength
                    num_to_add = max(1, int(len(trending_subgenres) * evolution_strength))
                    subgenres_to_add = list(trending_subgenres)[:num_to_add]
                    
                    # Update subgenres
                    new_subgenres = list(current_subgenres.union(subgenres_to_add))
                    evolved_profile.setdefault("genre", {})["subgenres"] = new_subgenres
            
            elif aspect == "style":
                # Incorporate trending style tags
                if "trending_styles" in trend_data:
                    current_tags = set(evolved_profile.get("style_tags", []))
                    trending_tags = set(trend_data["trending_styles"][:5])
                    
                    # Add some trending tags based on evolution strength
                    num_to_add = max(1, int(len(trending_tags) * evolution_strength))
                    tags_to_add = list(trending_tags)[:num_to_add]
                    
                    # Update style tags
                    new_tags = list(current_tags.union(tags_to_add))
                    evolved_profile["style_tags"] = new_tags
            
            elif aspect == "production":
                # Update production techniques
                evolved_profile.setdefault("production", {})["techniques"] = [
                    "Updated production techniques based on current trends"
                ]
            
            elif aspect == "visual":
                # Update visual aesthetic
                evolved_profile.setdefault("visual", {})["aesthetic"] = [
                    "Updated visual aesthetic based on current trends"
                ]
        
        # Add evolution metadata
        evolved_profile["metadata"] = evolved_profile.get("metadata", {})
        evolved_profile["metadata"].update({
            "evolved_directly": True,
            "evolution_strength": evolution_strength,
            "target_aspects": target_aspects
        })
        
        return evolved_profile

    def _generate_artist_slug(self, artist_name: str) -> str:
        """
        Generate a URL-friendly slug from an artist name.
        
        Args:
            artist_name: Name of the artist
            
        Returns:
            URL-friendly slug
        """
        # Convert to lowercase
        slug = artist_name.lower()
        
        # Replace spaces with underscores
        slug = slug.replace(" ", "_")
        
        # Remove special characters
        slug = "".join(c for c in slug if c.isalnum() or c == "_")
        
        # Add timestamp to ensure uniqueness
        timestamp = int(time.time())
        slug = f"{slug}_{timestamp}"
        
        return slug

    def _create_artist_directory_structure(self, artist_slug: str) -> None:
        """
        Create the directory structure for an artist.
        
        Args:
            artist_slug: Slug of the artist
        """
        # Create base artist directory
        artist_dir = os.path.join(self.artists_dir, artist_slug)
        os.makedirs(artist_dir, exist_ok=True)
        
        # Create subdirectories
        subdirs = [
            "prompts",
            "lyrics",
            "assets",
            "assets/images",
            "assets/audio",
            "assets/video",
            "metadata",
            "versions"
        ]
        
        for subdir in subdirs:
            os.makedirs(os.path.join(artist_dir, subdir), exist_ok=True)
        
        logger.info(f"Created directory structure for artist: {artist_slug}")


class ArtistCreationCLI:
    """
    Command-line interface for the artist creation system.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the artist creation CLI.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.interface = ArtistCreationInterface(self.config)
        
        logger.info("Initialized artist creation CLI")

    def create_artist_interactive(self) -> Dict[str, Any]:
        """
        Create a new artist through interactive prompts.
        
        Returns:
            Dictionary containing the created artist profile
        """
        print("\n=== Create New AI Artist ===\n")
        
        # Collect basic information
        artist_name = input("Artist Name: ")
        main_genre = input("Main Genre: ")
        
        subgenres_input = input("Subgenres (comma-separated): ")
        subgenres = [s.strip() for s in subgenres_input.split(",") if s.strip()]
        
        style_tags_input = input("Style Tags (comma-separated): ")
        style_tags = [s.strip() for s in style_tags_input.split(",") if s.strip()]
        
        vibe_description = input("Vibe Description: ")
        target_audience = input("Target Audience: ")
        
        trend_sensitivity = float(input("Trend Sensitivity (0.0-1.0): ") or "0.5")
        
        # Define callback for progress updates
        def progress_callback(update):
            status = update.get("status", "")
            message = update.get("message", "")
            progress = update.get("progress", 0.0)
            
            # Print progress bar
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            
            print(f"\r[{bar}] {progress:.1%} - {status}: {message}", end="")
            
            if status in ["completed", "error"]:
                print()  # Add newline for completion or error
        
        print("\nCreating artist profile... This may take a few minutes.\n")
        
        # Create the artist
        result = self.interface.create_artist(
            artist_name=artist_name,
            main_genre=main_genre,
            subgenres=subgenres,
            style_tags=style_tags,
            vibe_description=vibe_description,
            target_audience=target_audience,
            trend_sensitivity=trend_sensitivity,
            callback=progress_callback
        )
        
        print(f"\n\nArtist created successfully!")
        print(f"Artist Slug: {result['artist_slug']}")
        print(f"Profile saved to: {result['save_path']}")
        
        return result

    def evolve_artist_interactive(self) -> Dict[str, Any]:
        """
        Evolve an existing artist through interactive prompts.
        
        Returns:
            Dictionary containing the evolved artist profile
        """
        print("\n=== Evolve Existing AI Artist ===\n")
        
        # Get list of available artists
        artists_dir = self.config.get("artists_dir", "artists")
        available_artists = []
        
        if os.path.exists(artists_dir):
            available_artists = [
                d for d in os.listdir(artists_dir)
                if os.path.isdir(os.path.join(artists_dir, d))
            ]
        
        if not available_artists:
            print("No artists found. Please create an artist first.")
            return {}
        
        # Display available artists
        print("Available Artists:")
        for i, artist in enumerate(available_artists):
            print(f"{i+1}. {artist}")
        
        # Select artist
        selection = int(input("\nSelect artist number: "))
        if selection < 1 or selection > len(available_artists):
            print("Invalid selection.")
            return {}
        
        artist_slug = available_artists[selection - 1]
        
        # Get evolution parameters
        evolution_strength = float(input("Evolution Strength (0.0-1.0): ") or "0.3")
        trend_sensitivity = float(input("Trend Sensitivity (0.0-1.0): ") or "0.5")
        
        target_aspects_input = input("Target Aspects (comma-separated, leave empty for automatic): ")
        target_aspects = None
        if target_aspects_input.strip():
            target_aspects = [s.strip() for s in target_aspects_input.split(",") if s.strip()]
        
        # Define callback for progress updates
        def progress_callback(update):
            status = update.get("status", "")
            message = update.get("message", "")
            progress = update.get("progress", 0.0)
            
            # Print progress bar
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            
            print(f"\r[{bar}] {progress:.1%} - {status}: {message}", end="")
            
            if status in ["completed", "error"]:
                print()  # Add newline for completion or error
        
        print(f"\nEvolving artist {artist_slug}... This may take a few minutes.\n")
        
        # Evolve the artist
        result = self.interface.evolve_artist(
            artist_slug=artist_slug,
            evolution_strength=evolution_strength,
            trend_sensitivity=trend_sensitivity,
            target_aspects=target_aspects,
            callback=progress_callback
        )
        
        print(f"\n\nArtist evolved successfully!")
        print(f"Profile saved to: {result['save_path']}")
        
        return result

    def view_artist_analytics(self) -> Dict[str, Any]:
        """
        View analytics for an existing artist.
        
        Returns:
            Dictionary containing the artist analytics
        """
        print("\n=== View Artist Analytics ===\n")
        
        # Get list of available artists
        artists_dir = self.config.get("artists_dir", "artists")
        available_artists = []
        
        if os.path.exists(artists_dir):
            available_artists = [
                d for d in os.listdir(artists_dir)
                if os.path.isdir(os.path.join(artists_dir, d))
            ]
        
        if not available_artists:
            print("No artists found. Please create an artist first.")
            return {}
        
        # Display available artists
        print("Available Artists:")
        for i, artist in enumerate(available_artists):
            print(f"{i+1}. {artist}")
        
        # Select artist
        selection = int(input("\nSelect artist number: "))
        if selection < 1 or selection > len(available_artists):
            print("Invalid selection.")
            return {}
        
        artist_slug = available_artists[selection - 1]
        
        print(f"\nFetching analytics for {artist_slug}...\n")
        
        # Get analytics
        analytics = self.interface.get_artist_analytics(artist_slug)
        
        # Display basic information
        print(f"Artist: {analytics['artist_name']}")
        print(f"Created: {analytics['creation_date']}")
        print(f"Last Evolution: {analytics.get('last_evolution', 'Never')}")
        print(f"Current Version: {analytics['version']}")
        
        # Display version history
        print("\nVersion History:")
        for version in analytics.get("version_history", []):
            print(f"- Version {version['version']}: {version['date']}")
        
        # Display trend compatibility if available
        if "trend_data" in analytics and "compatibility" in analytics["trend_data"]:
            compatibility = analytics["trend_data"]["compatibility"]
            print("\nTrend Compatibility:")
            print(f"Overall Score: {compatibility.get('overall_score', 0):.2f}")
            
            if "aspect_scores" in compatibility:
                print("\nAspect Scores:")
                for aspect, score in compatibility["aspect_scores"].items():
                    print(f"- {aspect}: {score:.2f}")
        
        return analytics

    def run(self) -> None:
        """Run the CLI interface."""
        while True:
            print("\n=== AI Artist Creation and Evolution System ===")
            print("1. Create New Artist")
            print("2. Evolve Existing Artist")
            print("3. View Artist Analytics")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ")
            
            try:
                if choice == "1":
                    self.create_artist_interactive()
                elif choice == "2":
                    self.evolve_artist_interactive()
                elif choice == "3":
                    self.view_artist_analytics()
                elif choice == "4":
                    print("Exiting...")
                    break
                else:
                    print("Invalid choice. Please try again.")
            
            except Exception as e:
                print(f"Error: {str(e)}")
                logger.error(f"CLI error: {str(e)}")
