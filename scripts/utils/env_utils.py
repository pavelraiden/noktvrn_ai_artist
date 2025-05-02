"""
Environment utilities for loading .env files and accessing environment variables.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger("env_utils")


def load_env_file(env_file_path=None):
    """
    Load environment variables from .env file.

    Args:
        env_file_path (str, optional): Path to .env file. Defaults to ".env" in current directory.

    Returns:
        bool: True if successful, False otherwise
    """
    if env_file_path is None:
        env_file_path = Path(".env")
    else:
        env_file_path = Path(env_file_path)

    if not env_file_path.exists():
        logger.error(f".env file not found at {env_file_path}")
        return False

    try:
        with open(env_file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                os.environ[key] = value

        logger.info(f"Successfully loaded environment variables from {env_file_path}")
        return True
    except Exception as e:
        logger.error(f"Error loading .env file: {str(e)}")
        return False
