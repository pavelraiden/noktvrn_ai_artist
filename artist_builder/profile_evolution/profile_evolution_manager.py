"""
Enhanced Profile Evolution Manager Module

This module is responsible for managing the evolution of AI artist profiles,
including their public-facing descriptions, using LLM capabilities.
Enhanced with real data integration and performance-based context building.
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple

# Assuming LLMOrchestrator is in the llm_orchestrator directory
# Adjust import path based on actual project structure
try:
    from ...llm_orchestrator.orchestrator import LLMOrchestrator
except ImportError:
    # Fallback for different execution contexts or potential restructuring
    try:
        from llm_orchestrator.orchestrator import LLMOrchestrator
    except ImportError as e:
        print(f"Error importing LLMOrchestrator: {e}. Ensure it is correctly placed.")
        LLMOrchestrator = None # Set to None if import fails

# Assuming database connection manager exists
try:
    from ...database.connection_manager import DatabaseConnectionManager
except ImportError:
    try:
        from database.connection_manager import DatabaseConnectionManager
    except ImportError as e:
        print(f"Error importing DatabaseConnectionManager: {e}. Database operations will fail.")
        DatabaseConnectionManager = None

logger = logging.getLogger(__name__)

class ProfileEvolutionManager:
    """
    Manages the evolution of artist profile descriptions using an LLM.
    Handles fetching current descriptions, invoking the LLM for evolution,
    and updating the database with evolved descriptions.
    
    Enhanced with:
    - Performance data integration
    - Country-specific trend awareness
    - Gradual evolution constraints
    - Evolution history tracking
    """

    def __init__(self, db_manager: Optional[DatabaseConnectionManager] = None, llm_config: Optional[Dict[str, Any]] = None):
        """
        Initializes the ProfileEvolutionManager.

        Args:
            db_manager: An instance of DatabaseConnectionManager for database interactions.
            llm_config: Configuration dictionary for the LLMOrchestrator.
        """
        if not LLMOrchestrator:
            raise ImportError("LLMOrchestrator could not be imported. Profile evolution is unavailable.")
        
        self.db_manager = db_manager
        # Initialize LLM Orchestrator (reads API keys/model from env by default)
        self.llm_orchestrator = LLMOrchestrator(config=llm_config)
        logger.info("ProfileEvolutionManager initialized.")

    async def _fetch_artist_profile(self, artist_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches the complete artist profile from the database.
        
        Args:
            artist_id: The unique identifier for the artist.
            
        Returns:
            The complete artist profile as a dictionary, or None if not found.
        """
        if not self.db_manager:
            logger.warning("Database manager not provided. Cannot fetch artist profile.")
            return None
        
        query = "SELECT profile FROM artist_profiles WHERE artist_id = %s;"
        try:
            async with self.db_manager.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, (artist_id,))
                    result = await cur.fetchone()
                    if result and result[0]:
                        logger.info(f"Fetched profile for artist {artist_id}.")
                        return result[0]  # Assuming profile is stored as JSONB
                    else:
                        logger.warning(f"No profile found for artist {artist_id}.")
                        return None
        except Exception as e:
            logger.error(f"Error fetching profile for artist {artist_id}: {e}", exc_info=True)
            return None

    async def _fetch_performance_metrics(self, artist_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches recent performance metrics for the artist.
        
        Args:
            artist_id: The unique identifier for the artist.
            limit: Maximum number of recent metrics to fetch.
            
        Returns:
            List of performance metric dictionaries, or empty list if none found.
        """
        if not self.db_manager:
            logger.warning("Database manager not provided. Cannot fetch performance metrics.")
            return []
        
        query = """
        SELECT metrics_data, timestamp 
        FROM performance_metrics 
        WHERE artist_id = %s 
        ORDER BY timestamp DESC 
        LIMIT %s;
        """
        try:
            metrics = []
            async with self.db_manager.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, (artist_id, limit))
                    rows = await cur.fetchall()
                    for row in rows:
                        metrics_data, timestamp = row
                        metrics.append({
                            "data": metrics_data,  # Assuming metrics_data is JSONB
                            "timestamp": timestamp.isoformat() if hasattr(timestamp, 'isoformat') else timestamp
                        })
            logger.info(f"Fetched {len(metrics)} performance metrics for artist {artist_id}.")
            return metrics
        except Exception as e:
            logger.error(f"Error fetching performance metrics for artist {artist_id}: {e}", exc_info=True)
            return []

    async def _fetch_country_trends(self, country_codes: List[str], limit: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetches recent trend data for specified countries.
        
        Args:
            country_codes: List of country codes to fetch trends for.
            limit: Maximum number of recent trends per country.
            
        Returns:
            Dictionary mapping country codes to lists of trend dictionaries.
        """
        if not self.db_manager:
            logger.warning("Database manager not provided. Cannot fetch country trends.")
            return {}
        
        result = {}
        for country_code in country_codes:
            query = """
            SELECT trend_data 
            FROM country_profiles 
            WHERE country_code = %s 
            ORDER BY timestamp DESC 
            LIMIT %s;
            """
            try:
                trends = []
                async with self.db_manager.get_connection() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(query, (country_code, limit))
                        rows = await cur.fetchall()
                        for row in rows:
                            trends.append(row[0])  # Assuming trend_data is JSONB
                logger.info(f"Fetched {len(trends)} trends for country {country_code}.")
                result[country_code] = trends
            except Exception as e:
                logger.error(f"Error fetching trends for country {country_code}: {e}", exc_info=True)
                result[country_code] = []
        
        return result

    async def _fetch_evolution_history(self, artist_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Fetches recent evolution history for the artist.
        
        Args:
            artist_id: The unique identifier for the artist.
            limit: Maximum number of recent evolution entries to fetch.
            
        Returns:
            List of evolution history dictionaries, or empty list if none found.
        """
        if not self.db_manager:
            logger.warning("Database manager not provided. Cannot fetch evolution history.")
            return []
        
        query = """
        SELECT evolution_data, timestamp 
        FROM evolution_plans 
        WHERE artist_id = %s AND status = 'completed'
        ORDER BY timestamp DESC 
        LIMIT %s;
        """
        try:
            history = []
            async with self.db_manager.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, (artist_id, limit))
                    rows = await cur.fetchall()
                    for row in rows:
                        evolution_data, timestamp = row
                        history.append({
                            "data": evolution_data,  # Assuming evolution_data is JSONB
                            "timestamp": timestamp.isoformat() if hasattr(timestamp, 'isoformat') else timestamp
                        })
            logger.info(f"Fetched {len(history)} evolution history entries for artist {artist_id}.")
            return history
        except Exception as e:
            logger.error(f"Error fetching evolution history for artist {artist_id}: {e}", exc_info=True)
            return []

    async def _update_description_in_db(self, artist_id: str, new_description: str) -> bool:
        """
        Updates the artist description in the database.
        
        Args:
            artist_id: The unique identifier for the artist.
            new_description: The new description to set.
            
        Returns:
            True if update was successful, False otherwise.
        """
        if not self.db_manager:
            logger.warning("Database manager not provided. Cannot update description in DB.")
            return False

        # Update the specific field within the JSONB column
        # Use jsonb_set to update the 'description' key within the 'profile' JSONB object
        query = """
        UPDATE artist_profiles
        SET profile = jsonb_set(profile, 
                                '{description}', 
                                %s::jsonb, 
                                true) -- create_missing = true
        WHERE artist_id = %s;
        """
        try:
            async with self.db_manager.get_connection() as conn:
                async with conn.cursor() as cur:
                    # Ensure the new description is properly formatted as a JSON string literal
                    await cur.execute(query, (json.dumps(new_description), artist_id))
                    # Check if any row was updated
                    if cur.rowcount > 0:
                        logger.info(f"Successfully updated description for artist {artist_id}.")
                        return True
                    else:
                        logger.warning(f"Artist {artist_id} not found or description update failed.")
                        return False
        except Exception as e:
            logger.error(f"Error updating description for artist {artist_id}: {e}", exc_info=True)
            return False

    async def _record_evolution_event(self, artist_id: str, old_description: str, new_description: str, 
                                     evolution_goal: str, context: Dict[str, Any]) -> bool:
        """
        Records an evolution event in the evolution_plans table.
        
        Args:
            artist_id: The unique identifier for the artist.
            old_description: The previous description.
            new_description: The new description.
            evolution_goal: The goal that guided the evolution.
            context: The context used for the evolution.
            
        Returns:
            True if recording was successful, False otherwise.
        """
        if not self.db_manager:
            logger.warning("Database manager not provided. Cannot record evolution event.")
            return False
        
        evolution_data = {
            "old_description": old_description,
            "new_description": new_description,
            "evolution_goal": evolution_goal,
            "context": context or {},
            "evolution_type": "description"
        }
        
        query = """
        INSERT INTO evolution_plans (artist_id, evolution_data, status, timestamp)
        VALUES (%s, %s, 'completed', NOW());
        """
        try:
            async with self.db_manager.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, (artist_id, json.dumps(evolution_data)))
            logger.info(f"Successfully recorded evolution event for artist {artist_id}.")
            return True
        except Exception as e:
            logger.error(f"Error recording evolution event for artist {artist_id}: {e}", exc_info=True)
            return False

    async def _build_enhanced_context(self, artist_id: str, provided_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Builds an enhanced context for evolution by fetching relevant data from the database.
        
        Args:
            artist_id: The unique identifier for the artist.
            provided_context: Optional context provided by the caller.
            
        Returns:
            Enhanced context dictionary combining provided context with database data.
        """
        enhanced_context = provided_context.copy() if provided_context else {}
        
        # Fetch artist profile for genre and other relevant info
        profile = await self._fetch_artist_profile(artist_id)
        if profile:
            enhanced_context["artist_profile"] = {
                "genre": profile.get("genre", "Unknown"),
                "style": profile.get("style", "Unknown"),
                "target_audience": profile.get("target_audience", "General"),
                "creation_date": profile.get("creation_date", "Unknown")
            }
        
        # Fetch performance metrics
        metrics = await self._fetch_performance_metrics(artist_id)
        if metrics:
            # Extract key performance indicators
            performance_summary = {
                "recent_metrics": [],
                "top_countries": set()
            }
            
            for metric in metrics:
                metric_data = metric.get("data", {})
                performance_summary["recent_metrics"].append({
                    "timestamp": metric.get("timestamp"),
                    "streams": metric_data.get("streams", 0),
                    "engagement": metric_data.get("engagement", 0),
                    "sentiment": metric_data.get("sentiment", "neutral")
                })
                
                # Extract top countries from metrics
                countries = metric_data.get("country_breakdown", {})
                if countries:
                    # Add top 3 countries by streams
                    top_countries = sorted(countries.items(), key=lambda x: x[1].get("streams", 0), reverse=True)[:3]
                    for country, _ in top_countries:
                        performance_summary["top_countries"].add(country)
            
            enhanced_context["performance"] = performance_summary
            enhanced_context["top_countries"] = list(performance_summary["top_countries"])
        
        # Fetch country trends for top countries
        if "top_countries" in enhanced_context and enhanced_context["top_countries"]:
            country_trends = await self._fetch_country_trends(enhanced_context["top_countries"])
            if country_trends:
                enhanced_context["country_trends"] = country_trends
        
        # Fetch evolution history
        history = await self._fetch_evolution_history(artist_id)
        if history:
            enhanced_context["evolution_history"] = history
        
        logger.info(f"Built enhanced context for artist {artist_id} with {len(enhanced_context)} components.")
        return enhanced_context

    async def evolve_artist_profile_description(
        self,
        artist_id: str,
        evolution_goal: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 512,
        temperature: float = 0.8,
        enhance_context: bool = True
    ) -> Optional[str]:
        """
        Evolves the description for a specific artist based on a goal and context.
        Fetches the current description, calls the LLM, and updates the database.
        
        Args:
            artist_id: The unique identifier for the artist.
            evolution_goal: The goal for the evolution.
            context: Optional dictionary providing context.
            max_tokens: Maximum tokens for the LLM response.
            temperature: Sampling temperature for the LLM.
            enhance_context: Whether to enhance the provided context with database data.
            
        Returns:
            The evolved description string if successful, otherwise None.
        """
        logger.info(f"Starting description evolution for artist {artist_id} with goal: {evolution_goal[:100]}...")

        # 1. Fetch current profile and extract description
        profile = await self._fetch_artist_profile(artist_id)
        if not profile:
            logger.error(f"Could not fetch profile for artist {artist_id}. Aborting evolution.")
            return None
        
        current_description = profile.get("description")
        if not current_description:
            logger.error(f"No description found in profile for artist {artist_id}. Aborting evolution.")
            return None
        
        # 2. Build enhanced context if requested
        enhanced_context = context
        if enhance_context:
            enhanced_context = await self._build_enhanced_context(artist_id, context)
            logger.info(f"Enhanced context built with {len(enhanced_context)} elements.")
        
        # 3. Call LLM to evolve description
        try:
            evolved_description = await self.llm_orchestrator.evolve_description(
                current_description=current_description,
                evolution_goal=evolution_goal,
                context=enhanced_context,
                max_tokens=max_tokens,
                temperature=temperature
            )
            logger.info(f"Successfully generated evolved description for artist {artist_id}.")
        except Exception as e:
            logger.error(f"LLM call failed during description evolution for artist {artist_id}: {e}", exc_info=True)
            return None

        # 4. Update description in database
        update_success = await self._update_description_in_db(artist_id, evolved_description)
        if not update_success:
            logger.error(f"Failed to update database with evolved description for artist {artist_id}.")
            # Return the description even if DB update failed
            return evolved_description
        
        # 5. Record the evolution event
        record_success = await self._record_evolution_event(
            artist_id=artist_id,
            old_description=current_description,
            new_description=evolved_description,
            evolution_goal=evolution_goal,
            context=enhanced_context or {}
        )
        if not record_success:
            logger.warning(f"Failed to record evolution event for artist {artist_id}.")
        
        return evolved_description

    async def get_evolution_recommendations(self, artist_id: str) -> List[Dict[str, Any]]:
        """
        Analyzes artist data and generates recommendations for evolution.
        
        Args:
            artist_id: The unique identifier for the artist.
            
        Returns:
            List of recommendation dictionaries with goals and rationales.
        """
        # Build enhanced context to get all relevant data
        context = await self._build_enhanced_context(artist_id)
        if not context:
            logger.warning(f"Could not build context for artist {artist_id}. Cannot generate recommendations.")
            return []
        
        # Extract key information for recommendations
        profile = context.get("artist_profile", {})
        genre = profile.get("genre", "Unknown")
        performance = context.get("performance", {})
        country_trends = context.get("country_trends", {})
        
        # Prepare prompt for LLM
        prompt = f"""
        **Task:** Generate evolution recommendations for an AI artist with the following profile and performance data.
        
        **Artist Profile:**
        ```json
        {json.dumps(profile, indent=2)}
        ```
        
        **Performance Data:**
        ```json
        {json.dumps(performance, indent=2)}
        ```
        
        **Country Trends:**
        ```json
        {json.dumps(country_trends, indent=2)}
        ```
        
        **Output Requirements:** 
        Generate 3 specific evolution recommendations in JSON format. Each recommendation should include:
        1. A clear evolution goal
        2. A detailed rationale based on the data
        3. Expected impact on audience engagement
        
        Format as a JSON array of objects with keys: "goal", "rationale", "expected_impact"
        """
        
        try:
            recommendations_json = await self.llm_orchestrator.generate_text(
                prompt=prompt,
                max_tokens=1024,
                temperature=0.7
            )
            
            # Parse the JSON response
            try:
                recommendations = json.loads(recommendations_json)
                if isinstance(recommendations, list) and len(recommendations) > 0:
                    logger.info(f"Generated {len(recommendations)} evolution recommendations for artist {artist_id}.")
                    return recommendations
                else:
                    logger.warning(f"Invalid recommendations format for artist {artist_id}.")
                    return []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse recommendations JSON for artist {artist_id}: {e}")
                return []
                
        except Exception as e:
            logger.error(f"LLM call failed during recommendation generation for artist {artist_id}: {e}", exc_info=True)
            return []

# Example Usage (requires async context)
async def main_example():
    # This is a conceptual example. Actual usage requires setting up DB connection
    # and ensuring environment variables (like OPENAI_API_KEY) are set.
    logging.basicConfig(level=logging.INFO)
    
    # Assume db_manager is initialized elsewhere
    # db_manager = DatabaseConnectionManager(db_config={...})
    db_manager = None # Placeholder
    
    profile_evolver = ProfileEvolutionManager(db_manager=db_manager)
    
    artist_id_to_evolve = "artist_123" # Example artist ID
    goal = "Make the artist sound more mysterious and appealing to a niche electronic music audience."
    perf_context = {"recent_track_performance": "moderate success in Germany", "audience_feedback": "lyrics are too generic"}
    
    print(f"Attempting to evolve description for {artist_id_to_evolve}...")
    new_desc = await profile_evolver.evolve_artist_profile_description(
        artist_id=artist_id_to_evolve,
        evolution_goal=goal,
        context=perf_context
    )
    
    if new_desc:
        print("\n--- Evolved Description ---")
        print(new_desc)
        print("-------------------------")
    else:
        print("\nFailed to evolve description.")
    
    # Get evolution recommendations
    recommendations = await profile_evolver.get_evolution_recommendations(artist_id_to_evolve)
    if recommendations:
        print("\n--- Evolution Recommendations ---")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. Goal: {rec.get('goal')}")
            print(f"   Rationale: {rec.get('rationale')}")
            print(f"   Expected Impact: {rec.get('expected_impact')}")
            print()
    else:
        print("\nNo evolution recommendations available.")

# if __name__ == "__main__":
#     asyncio.run(main_example())
