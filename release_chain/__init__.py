# This file makes the release_chain directory a Python package.

# Import key functions and classes to be available directly from the package namespace.
from .release_chain import (
    generate_artist_slug,
    create_release_directory,
    download_asset,
    generate_cover_art,
    analyze_track_structure,
    get_prompts_from_run_data,
    save_json_file,
    save_metadata_file,
    save_prompts_file,
    create_feedback_placeholder,
    log_release_to_markdown,
    add_release_to_queue,
    log_learning_entry,
    process_approved_run,
    OUTPUT_BASE_DIR,  # Added
    RELEASES_DIR,  # Added
    RUN_STATUS_DIR,  # Added
    RELEASE_LOG_FILE,  # Added
    RELEASE_QUEUE_FILE,  # Added
    EVOLUTION_LOG_FILE,  # Added
)

# Re-export Path from pathlib as it seems to be expected by tests
from pathlib import Path

# Schemas might also be expected here if tests import them via release_chain
# For now, focusing on functions and Path based on AttributeErrors
# from .schemas import ReleaseMetadata, PromptsUsed # This was in release_chain.py, might be needed here too

__all__ = [
    "generate_artist_slug",
    "create_release_directory",
    "download_asset",
    "generate_cover_art",
    "analyze_track_structure",
    "get_prompts_from_run_data",
    "save_json_file",
    "save_metadata_file",
    "save_prompts_file",
    "create_feedback_placeholder",
    "log_release_to_markdown",
    "add_release_to_queue",
    "log_learning_entry",
    "process_approved_run",
    "Path",
    "OUTPUT_BASE_DIR",  # Added
    "RELEASES_DIR",  # Added
    "RUN_STATUS_DIR",  # Added
    "RELEASE_LOG_FILE",  # Added
    "RELEASE_QUEUE_FILE",  # Added
    "EVOLUTION_LOG_FILE",  # Added
    # "ReleaseMetadata", # Add if needed
    # "PromptsUsed"      # Add if needed
]
