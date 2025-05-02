"""
Input Handler Module for Artist Profile Builder

This module handles the collection and validation of initial user inputs
for artist profile creation through various interfaces (CLI, API, GUI).
"""

import logging
import json
import argparse
import sys
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.input_handler")

# Required fields for minimal artist profile creation
REQUIRED_FIELDS = [
    "stage_name",
    "genre",
    "subgenres",
    "style_description",
    "voice_type",
    "personality_traits",
    "target_audience",
    "visual_identity_prompt",
]

# Optional fields that can be provided but will be generated if missing
OPTIONAL_FIELDS = [
    "real_name",
    "backstory",
    "influences",
    "notes",
    "song_prompt_generator",
    "video_prompt_generator",
]

# Fields that should be lists
LIST_FIELDS = ["subgenres", "personality_traits", "influences"]


class InputValidationError(Exception):
    """Exception raised for errors in the input validation."""

    pass


def validate_initial_input(input_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate that the initial input contains all required fields.

    Args:
        input_data: Dictionary containing the input data

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check for required fields
    for field in REQUIRED_FIELDS:
        if field not in input_data or not input_data[field]:
            errors.append(f"Missing required field: {field}")

    # Check that list fields are actually lists
    for field in LIST_FIELDS:
        if field in input_data and not isinstance(input_data[field], list):
            # Try to convert string to list if it's comma-separated
            if isinstance(input_data[field], str):
                try:
                    input_data[field] = [
                        item.strip() for item in input_data[field].split(",")
                    ]
                except Exception:
                    errors.append(
                        f"Field {field} must be a list or comma-separated string"
                    )
            else:
                errors.append(f"Field {field} must be a list")

    return len(errors) == 0, errors


def normalize_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize input data to ensure consistent format.

    Args:
        input_data: Dictionary containing the input data

    Returns:
        Normalized input data
    """
    normalized = input_data.copy()

    # Ensure list fields are lists
    for field in LIST_FIELDS:
        if field in normalized and not isinstance(normalized[field], list):
            if isinstance(normalized[field], str):
                normalized[field] = [
                    item.strip() for item in normalized[field].split(",")
                ]

    # Strip whitespace from string fields
    for key, value in normalized.items():
        if isinstance(value, str):
            normalized[key] = value.strip()

    # Ensure subgenres is a list even if only one item
    if "subgenres" in normalized and isinstance(normalized["subgenres"], str):
        normalized["subgenres"] = [normalized["subgenres"]]

    # Ensure personality_traits is a list even if only one item
    if "personality_traits" in normalized and isinstance(
        normalized["personality_traits"], str
    ):
        normalized["personality_traits"] = [normalized["personality_traits"]]

    return normalized


def collect_cli_input() -> Dict[str, Any]:
    """
    Collect artist profile inputs from command line arguments.

    Returns:
        Dictionary containing the input data
    """
    parser = argparse.ArgumentParser(description="Create an artist profile")

    # Add arguments for required fields
    parser.add_argument("--stage-name", required=True, help="Artist's stage name")
    parser.add_argument("--genre", required=True, help="Primary music genre")
    parser.add_argument(
        "--subgenres", required=True, help="Comma-separated list of subgenres"
    )
    parser.add_argument(
        "--style-description", required=True, help="Description of the artist's style"
    )
    parser.add_argument(
        "--voice-type", required=True, help="Description of the artist's voice"
    )
    parser.add_argument(
        "--personality-traits",
        required=True,
        help="Comma-separated list of personality traits",
    )
    parser.add_argument(
        "--target-audience", required=True, help="Description of the target audience"
    )
    parser.add_argument(
        "--visual-identity-prompt",
        required=True,
        help="Prompt for generating visual identity",
    )

    # Add arguments for optional fields
    parser.add_argument(
        "--real-name", help="Artist's real name (if different from stage name)"
    )
    parser.add_argument("--backstory", help="Artist's fictional backstory")
    parser.add_argument(
        "--influences", help="Comma-separated list of musical influences"
    )
    parser.add_argument("--notes", help="Additional notes about the artist")
    parser.add_argument(
        "--song-prompt-generator", help="Template to use for song prompt generation"
    )
    parser.add_argument(
        "--video-prompt-generator", help="Template to use for video prompt generation"
    )

    # Add argument for input from file
    parser.add_argument("--input-file", help="JSON file containing artist profile data")

    args = parser.parse_args()

    # If input file is provided, read from file
    if args.input_file:
        try:
            with open(args.input_file, "r") as f:
                input_data = json.load(f)
            logger.info(f"Loaded input data from {args.input_file}")
            return input_data
        except Exception as e:
            logger.error(f"Error loading input file: {e}")
            sys.exit(1)

    # Convert args to dictionary
    input_data = vars(args)

    # Remove input_file from dictionary
    input_data.pop("input_file", None)

    # Convert kebab-case args to snake_case
    converted_data = {}
    for key, value in input_data.items():
        converted_key = key.replace("-", "_")
        converted_data[converted_key] = value

    return converted_data


def collect_api_input(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process artist profile inputs from API request.

    Args:
        request_data: Dictionary containing the request data

    Returns:
        Dictionary containing the input data
    """
    # API input is already a dictionary, just validate and normalize
    return request_data


def collect_gui_input(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process artist profile inputs from GUI form.

    Args:
        form_data: Dictionary containing the form data

    Returns:
        Dictionary containing the input data
    """
    # GUI input is already a dictionary, just validate and normalize
    return form_data


def load_input_from_file(file_path: str) -> Dict[str, Any]:
    """
    Load artist profile inputs from a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary containing the input data
    """
    try:
        with open(file_path, "r") as f:
            input_data = json.load(f)
        logger.info(f"Loaded input data from {file_path}")
        return input_data
    except Exception as e:
        logger.error(f"Error loading input file: {e}")
        raise InputValidationError(f"Error loading input file: {e}")


def save_input_to_file(input_data: Dict[str, Any], file_path: str) -> None:
    """
    Save artist profile inputs to a JSON file.

    Args:
        input_data: Dictionary containing the input data
        file_path: Path to save the JSON file
    """
    try:
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(input_data, f, indent=2)
        logger.info(f"Saved input data to {file_path}")
    except Exception as e:
        logger.error(f"Error saving input file: {e}")
        raise InputValidationError(f"Error saving input file: {e}")


def process_input(
    input_data: Dict[str, Any], input_source: str = "unknown"
) -> Dict[str, Any]:
    """
    Process and validate input data from any source.

    Args:
        input_data: Dictionary containing the input data
        input_source: Source of the input (cli, api, gui, file)

    Returns:
        Normalized and validated input data
    """
    logger.info(f"Processing input from {input_source}")

    # Normalize input
    normalized_data = normalize_input(input_data)

    # Validate input
    is_valid, errors = validate_initial_input(normalized_data)
    if not is_valid:
        error_msg = f"Input validation failed: {', '.join(errors)}"
        logger.error(error_msg)
        raise InputValidationError(error_msg)

    logger.info("Input validation successful")
    return normalized_data


def get_minimal_input_template() -> Dict[str, Any]:
    """
    Get a template with the minimal required fields for artist profile creation.

    Returns:
        Dictionary containing the template
    """
    template = {}
    for field in REQUIRED_FIELDS:
        if field in LIST_FIELDS:
            template[field] = []
        else:
            template[field] = ""

    return template


def get_full_input_template() -> Dict[str, Any]:
    """
    Get a template with all possible input fields for artist profile creation.

    Returns:
        Dictionary containing the template
    """
    template = get_minimal_input_template()

    for field in OPTIONAL_FIELDS:
        if field in LIST_FIELDS:
            template[field] = []
        else:
            template[field] = ""

    return template


def main():
    """Main function for CLI usage."""
    try:
        # Collect input from command line
        input_data = collect_cli_input()

        # Process and validate input
        processed_data = process_input(input_data, "cli")

        # Print the processed data
        print(json.dumps(processed_data, indent=2))

        return processed_data
    except InputValidationError as e:
        logger.error(f"Validation error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
