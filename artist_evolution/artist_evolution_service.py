import logging
from typing import Dict, Any, List, Tuple, Optional
import random
from datetime import datetime, timedelta
import math # Added for decay

# Adjust imports based on actual project structure
try:
    from ..analytics.performance_db_service import get_performance_metrics_for_release, PerformanceDbError
    from .artist_progression_db_service import add_progression_log_entry, ProgressionDbError, apply_progression_schema
    from .artist_profile_manager import get_artist_profile, update_artist_profile, get_releases_by_artist, ArtistProfileError
except ImportError as e:
    logging.warning(f"Artist Evolution Service: Failed to import dependencies (may be expected if placeholders not yet implemented): {e}")
    # Define dummy functions if imports fail
    class PerformanceDbError(Exception): pass
    class ArtistProfileError(Exception): pass
    class ProgressionDbError(Exception): pass
    def get_performance_metrics_for_release(release_id: int) -> List[Dict[str, Any]]: return []
    def get_artist_profile(artist_id: int) -> Dict[str, Any]: return {"id": artist_id, "name": "Dummy Artist", "genres": ["pop"], "style_keywords": ["upbeat"], "evolution_log": [], "prompt_history": []}
    def update_artist_profile(artist_id: int, profile_data: Dict[str, Any]): pass
    def get_releases_by_artist(artist_id: int) -> List[Dict[str, Any]]: return []
    def add_progression_log_entry(artist_id: int, event_description: str, performance_summary: str = None, profile_snapshot: Dict[str, Any] = None) -> int: return 1
    def apply_progression_schema(): pass

logger = logging.getLogger(__name__)

class ArtistEvolutionError(Exception):
    """Custom exception for artist evolution errors."""
    pass

def score_release_effectiveness(release_id: Any, metrics: List[Dict[str, Any]], decay_factor: float = 0.05) -> Tuple[float, str]:
    """Calculates an effectiveness score for a single release based on its metrics.
    Applies time decay to older metrics.

    Args:
        release_id: The ID of the release being scored.
        metrics: A list of performance metric dictionaries for this release.
        decay_factor: Controls how quickly the score contribution of older metrics decreases (higher value = faster decay).

    Returns:
        A tuple containing: (calculated score, summary string).
    """
    if not metrics:
        return 0.0, f"Release {release_id}: No metrics available."

    total_weighted_score = 0.0
    total_weight = 0.0
    now = datetime.utcnow()
    metric_details = []

    # Sort metrics by timestamp, newest first
    metrics.sort(key=lambda x: x.get("recorded_at", ""), reverse=True)

    for metric in metrics:
        try:
            metric_time = datetime.fromisoformat(metric["recorded_at"].replace("Z", "+00:00")) # Ensure timezone aware
            days_old = (now - metric_time).days
            
            # Apply exponential decay based on age
            weight = math.exp(-decay_factor * days_old)
            
            # Simple scoring: likes + streams/views + saves (adjust weights/metrics as needed)
            # Normalize or scale these values in a real scenario
            raw_score = 0
            if metric.get("metric_type") in ["likes", "saves"]:
                raw_score += metric.get("metric_value", 0) * 0.3 # Weight likes/saves less than streams/views
            elif metric.get("metric_type") in ["views", "streams"]:
                 raw_score += metric.get("metric_value", 0) * 0.7
            else: # Ignore other metric types for now
                continue

            weighted_score = raw_score * weight
            total_weighted_score += weighted_score
            total_weight += weight
            metric_details.append(f"{metric.get(	metric_type	)}={metric.get(	metric_value	)}@{days_old}d(w={weight:.2f})")

        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping metric due to parsing error for release {release_id}: {metric}. Error: {e}")
            continue

    final_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
    summary = f"Release {release_id}: Score={final_score:.2f} (from {len(metric_details)} weighted metrics: {', '.join(metric_details[:3])}{'...' if len(metric_details) > 3 else ''})"
    logger.debug(summary)
    return final_score, summary


def apply_evolution_rules(current_profile: Dict[str, Any], release_scores: List[Tuple[Any, float, str]]) -> Tuple[Dict[str, Any], str]:
    """Applies rules to evolve the artist profile based on release scores.
    
    Args:
        current_profile: The current artist profile dictionary.
        release_scores: List of tuples (release_id, score, summary_string) sorted best to worst.

    Returns:
        A tuple containing: (updated artist profile dictionary, event description string).
    """
    updated_profile = current_profile.copy()
    event_description = "No significant changes applied based on release scores."
    log_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Applying evolution rules to artist ID: {updated_profile.get("id")}")

    # Ensure evolution_log and prompt_history exist
    if "evolution_log" not in updated_profile or not isinstance(updated_profile["evolution_log"], list):
        updated_profile["evolution_log"] = []
    if "prompt_history" not in updated_profile or not isinstance(updated_profile["prompt_history"], list):
        updated_profile["prompt_history"] = [] # Add prompt history tracking

    if not release_scores:
        # Handle case with no scorable releases (similar to previous logic)
        if "experimental" not in updated_profile.get("style_keywords", []):
            updated_profile["style_keywords"] = updated_profile.get("style_keywords", []) + ["experimental"]
            log_message = f"{log_timestamp}: Added keyword 	'experimental'	 due to no scorable releases."
            updated_profile["evolution_log"].append(log_message)
            event_description = "Added keyword 	'experimental'	 due to lack of performance data."
            logger.info(event_description)
        return updated_profile, event_description

    # --- Example Evolution Rules based on Scores --- 
    average_score = sum(score for _, score, _ in release_scores) / len(release_scores)
    best_release_id, best_score, best_summary = release_scores[0]
    worst_release_id, worst_score, worst_summary = release_scores[-1]

    logger.debug(f"Best release: {best_summary}")
    logger.debug(f"Worst release: {worst_summary}")
    logger.debug(f"Average score: {average_score:.2f}")

    # Simple rule: If best score is significantly above average, reinforce; if worst is significantly below, diversify.
    # Thresholds need tuning.
    reinforce_threshold = 1.2 * average_score
    diversify_threshold = 0.8 * average_score

    change_made = False
    if best_score > reinforce_threshold and best_score > 0: # Reinforce based on best
        # In a real system, we'd fetch the prompt/params used for best_release_id
        # For now, let's just add a generic keyword based on the assumed success
        success_keyword = random.choice(["resonant", "engaging", "hit-potential"])
        if success_keyword not in updated_profile.get("style_keywords", []):
            updated_profile["style_keywords"] = updated_profile.get("style_keywords", []) + [success_keyword]
            log_message = f"{log_timestamp}: Added keyword 	'{success_keyword}'	 due to high score ({best_score:.2f}) on release {best_release_id}. Avg score: {average_score:.2f}."
            updated_profile["evolution_log"].append(log_message)
            event_description = f"Reinforced style (added 	'{success_keyword}'	) based on high-performing release {best_release_id}."
            logger.info(event_description)
            change_made = True
            # Store simplified prompt info (placeholder)
            updated_profile["prompt_history"].append({"release_id": best_release_id, "score": best_score, "action": "reinforce", "keywords_added": [success_keyword], "timestamp": log_timestamp})

    if not change_made and worst_score < diversify_threshold and len(release_scores) > 1: # Diversify based on worst (if no reinforcement happened)
        # Remove a keyword or add an experimental one
        current_keywords = updated_profile.get("style_keywords", [])
        if len(current_keywords) > 1:
            keyword_to_remove = random.choice(current_keywords)
            updated_profile["style_keywords"].remove(keyword_to_remove)
            log_message = f"{log_timestamp}: Removed keyword 	'{keyword_to_remove}'	 due to low score ({worst_score:.2f}) on release {worst_release_id}. Avg score: {average_score:.2f}."
            updated_profile["evolution_log"].append(log_message)
            event_description = f"Diversified style (removed 	'{keyword_to_remove}'	) based on low-performing release {worst_release_id}."
            logger.info(event_description)
            change_made = True
            updated_profile["prompt_history"].append({"release_id": worst_release_id, "score": worst_score, "action": "diversify", "keywords_removed": [keyword_to_remove], "timestamp": log_timestamp})
        elif "experimental" not in current_keywords:
             updated_profile["style_keywords"].append("experimental")
             log_message = f"{log_timestamp}: Added keyword 	'experimental'	 due to low score ({worst_score:.2f}) on release {worst_release_id}. Avg score: {average_score:.2f}."
             updated_profile["evolution_log"].append(log_message)
             event_description = f"Added keyword 	'experimental'	 based on low-performing release {worst_release_id}."
             logger.info(event_description)
             change_made = True
             updated_profile["prompt_history"].append({"release_id": worst_release_id, "score": worst_score, "action": "diversify", "keywords_added": ["experimental"], "timestamp": log_timestamp})

    if not change_made:
        log_message = f"{log_timestamp}: Scores analyzed, no significant deviation detected for evolution rules. Best: {best_score:.2f}, Worst: {worst_score:.2f}, Avg: {average_score:.2f}."
        updated_profile["evolution_log"].append(log_message)
        logger.info("Scores analyzed, no significant changes triggered.")

    logger.info(f"Evolution rules applied. Updated profile keywords: {updated_profile.get(	'style_keywords'	)}")
    return updated_profile, event_description

def evolve_artist(artist_id: int) -> Dict[str, Any]:
    """Evolves an artist's profile based on performance scores of releases, logs the change.
    """
    logger.info(f"Starting evolution process for artist ID: {artist_id}")
    release_scores = []
    event_description = "Initialization."
    performance_summary = "No releases or metrics found."
    updated_profile = None

    try:
        # Ensure progression schema is applied (idempotent)
        apply_progression_schema()

        current_profile = get_artist_profile(artist_id)
        if not current_profile:
            raise ArtistEvolutionError(f"Artist profile not found for ID: {artist_id}")
        logger.debug(f"Retrieved current profile for artist {artist_id}")

        releases = get_releases_by_artist(artist_id)
        if not releases:
            logger.warning(f"No releases found for artist {artist_id}. Cannot perform evolution based on performance.")
        else:
            logger.debug(f"Found {len(releases)} releases for artist {artist_id}")
            release_score_summaries = []
            for release in releases:
                release_id = release.get("id")
                if release_id:
                    try:
                        metrics = get_performance_metrics_for_release(release_id)
                        logger.debug(f"Retrieved {len(metrics)} metrics for release {release_id}")
                        if metrics:
                            score, summary = score_release_effectiveness(release_id, metrics)
                            if score > 0: # Only consider releases with a valid score
                                release_scores.append((release_id, score, summary))
                            release_score_summaries.append(summary)
                        else:
                             release_score_summaries.append(f"Release {release_id}: No metrics found.")
                    except PerformanceDbError as e:
                        logger.warning(f"Could not retrieve/score performance data for release {release_id}: {e}")
                        release_score_summaries.append(f"Release {release_id}: Error fetching metrics.")
            
            performance_summary = " | ".join(release_score_summaries)
            # Sort releases by score, highest first
            release_scores.sort(key=lambda x: x[1], reverse=True)

        # Apply rules based on sorted scores and get description
        updated_profile, event_description = apply_evolution_rules(current_profile, release_scores)

        # Update profile in storage
        update_artist_profile(artist_id, updated_profile)
        logger.info(f"Successfully updated profile for artist ID: {artist_id}")

        # Add log entry to progression DB
        try:
            add_progression_log_entry(
                artist_id=artist_id,
                event_description=event_description,
                performance_summary=performance_summary, # Log the summary of scores
                profile_snapshot=updated_profile # Log the state *after* the change
            )
            logger.info(f"Successfully logged progression for artist ID: {artist_id}")
        except ProgressionDbError as log_e:
            logger.error(f"Failed to log progression for artist {artist_id}: {log_e}", exc_info=True)

        return updated_profile

    except (ArtistProfileError, PerformanceDbError) as e:
        logger.error(f"Database/Profile error during evolution for artist {artist_id}: {e}", exc_info=True)
        raise ArtistEvolutionError(f"Data retrieval/update failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during evolution for artist {artist_id}: {e}", exc_info=True)
        raise ArtistEvolutionError(f"An unexpected error occurred: {e}")

# Example Usage (for testing purposes)
if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.DEBUG, format=	'%(asctime)s - %(name)s - %(levelname)s - %(message)s	)

    # --- Mocking Dependencies --- 
    mock_profiles = {
        1: {"id": 1, "name": "Synthwave Dreamer", "genres": ["synthwave", "electronic"], "style_keywords": ["80s", "retro", "neon"], "evolution_log": [], "prompt_history": []}
    }
    mock_releases = {
        1: [
            {"id": 101, "artist_id": 1, "title": "Neon Nights"},
            {"id": 102, "artist_id": 1, "title": "Digital Sunset"},
            {"id": 103, "artist_id": 1, "title": "Future Drive"} # Add a third release
        ]
    }
    # Simulate metrics with different timestamps and values
    now = datetime.utcnow()
    mock_performance = {
        101: [ # Low performing
            {"id": 1, "release_id": 101, "platform": "YouTube", "metric_type": "views", "metric_value": 1000, "recorded_at": (now - timedelta(days=10)).isoformat() + "Z"},
            {"id": 2, "release_id": 101, "platform": "YouTube", "metric_type": "likes", "metric_value": 50, "recorded_at": (now - timedelta(days=10)).isoformat() + "Z"}
        ],
        102: [ # High performing
            {"id": 3, "release_id": 102, "platform": "Spotify", "metric_type": "streams", "metric_value": 50000, "recorded_at": (now - timedelta(days=5)).isoformat() + "Z"},
            {"id": 4, "release_id": 102, "platform": "Spotify", "metric_type": "saves", "metric_value": 1000, "recorded_at": (now - timedelta(days=5)).isoformat() + "Z"}
        ],
        103: [ # Medium performing, older
            {"id": 5, "release_id": 103, "platform": "Spotify", "metric_type": "streams", "metric_value": 20000, "recorded_at": (now - timedelta(days=40)).isoformat() + "Z"},
        ]
    }
    mock_progression_log = []

    def mock_get_artist_profile(artist_id: int) -> Dict[str, Any]:
        logger.debug(f"[Mock] Getting profile for artist {artist_id}")
        profile = mock_profiles.get(artist_id)
        if not profile: raise ArtistProfileError("Mock profile not found")
        return profile.copy()

    def mock_update_artist_profile(artist_id: int, profile_data: Dict[str, Any]):
        logger.debug(f"[Mock] Updating profile for artist {artist_id}")
        if artist_id not in mock_profiles: raise ArtistProfileError("Mock profile not found for update")
        mock_profiles[artist_id] = profile_data
        logger.debug(f"[Mock] Updated profile: {profile_data}")

    def mock_get_releases_by_artist(artist_id: int) -> List[Dict[str, Any]]:
        logger.debug(f"[Mock] Getting releases for artist {artist_id}")
        return mock_releases.get(artist_id, [])

    def mock_get_performance_metrics_for_release(release_id: int) -> List[Dict[str, Any]]:
        logger.debug(f"[Mock] Getting performance for release {release_id}")
        return mock_performance.get(release_id, [])

    def mock_add_progression_log_entry(artist_id: int, event_description: str, performance_summary: str = None, profile_snapshot: Dict[str, Any] = None) -> int:
        log_entry = {
            "id": len(mock_progression_log) + 1,
            "artist_id": artist_id,
            "event_timestamp": datetime.now().isoformat(),
            "event_description": event_description,
            "performance_summary": performance_summary,
            "profile_snapshot": profile_snapshot
        }
        mock_progression_log.append(log_entry)
        logger.debug(f"[Mock] Added progression log entry: {log_entry['id']}")
        return log_entry['id']
    
    def mock_apply_progression_schema():
        logger.debug("[Mock] Applying progression schema (no-op)")
        pass

    # Replace real functions with mocks
    get_artist_profile = mock_get_artist_profile
    update_artist_profile = mock_update_artist_profile
    get_releases_by_artist = mock_get_releases_by_artist
    get_performance_metrics_for_release = mock_get_performance_metrics_for_release
    add_progression_log_entry = mock_add_progression_log_entry
    apply_progression_schema = mock_apply_progression_schema
    ArtistProfileError = Exception
    PerformanceDbError = Exception
    ProgressionDbError = Exception
    # --- End Mocking --- 

    TEST_ARTIST_ID = 1
    print(f"\n--- Evolving Artist ID: {TEST_ARTIST_ID} ---")
    try:
        print(f"Initial Profile: {json.dumps(mock_profiles[TEST_ARTIST_ID], indent=2)}")
        updated = evolve_artist(TEST_ARTIST_ID)
        print(f"\nEvolved Profile: {json.dumps(updated, indent=2)}")
        print(f"\nMock Progression Log: {json.dumps(mock_progression_log, indent=2)}")
    except ArtistEvolutionError as e:
        print(f"Evolution Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")


