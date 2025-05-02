"""
Logging and Error Handling Module for Artist Profile Builder

This module provides consistent logging and comprehensive error handling
for the Artist Profile Builder, ensuring robust operation and clear error messages.
"""

import logging
import os
import sys
import traceback
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from pathlib import Path
from datetime import datetime
import json
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.error_handler")


class ArtistBuilderError(Exception):
    """Base exception class for all Artist Profile Builder errors."""

    pass


class InputError(ArtistBuilderError):
    """Exception raised for errors in the input data."""

    pass


class LLMPipelineError(ArtistBuilderError):
    """Exception raised for errors in the LLM pipeline."""

    pass


class ValidationError(ArtistBuilderError):
    """Exception raised for errors in profile validation."""

    pass


class StorageError(ArtistBuilderError):
    """Exception raised for errors in profile storage operations."""

    pass


class IntegrationError(ArtistBuilderError):
    """Exception raised for errors in integration with other modules."""

    pass


class ErrorHandler:
    """
    Handles errors and logging for the Artist Profile Builder.
    """

    def __init__(
        self, log_dir: Optional[str] = None, error_log_file: Optional[str] = None
    ):
        """
        Initialize the error handler.

        Args:
            log_dir: Optional path to the log directory. If not provided,
                    defaults to /logs in the project root.
            error_log_file: Optional name of the error log file. If not provided,
                           defaults to artist_builder_errors.log.
        """
        # Set default log directory if not provided
        if log_dir is None:
            # Get the project root directory (two levels up from this file)
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            log_dir = os.path.join(project_root, "logs")

        self.log_dir = log_dir
        self.error_log_file = error_log_file or "artist_builder_errors.log"
        self.error_log_path = os.path.join(self.log_dir, self.error_log_file)

        # Ensure log directory exists
        self._ensure_log_directory()

        # Configure file handler for error logging
        self._setup_file_logging()

        logger.info(f"Initialized ErrorHandler with error log at {self.error_log_path}")

    def _ensure_log_directory(self) -> None:
        """Ensure the log directory exists, creating it if necessary."""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            logger.info(f"Ensured log directory exists: {self.log_dir}")
        except Exception as e:
            logger.error(f"Error creating log directory: {e}")
            # Continue without file logging if directory creation fails

    def _setup_file_logging(self) -> None:
        """Set up file logging for errors."""
        try:
            # Create file handler for error logging
            file_handler = logging.FileHandler(self.error_log_path)
            file_handler.setLevel(logging.ERROR)

            # Create formatter
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)

            # Add file handler to logger
            logger.addHandler(file_handler)

            logger.info(f"Set up file logging to {self.error_log_path}")
        except Exception as e:
            logger.error(f"Error setting up file logging: {e}")
            # Continue without file logging if setup fails

    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """
        Log an error with context information.

        Args:
            error: The exception to log
            context: Optional dictionary containing context information

        Returns:
            String containing the error ID for reference
        """
        # Generate error ID
        error_id = str(uuid.uuid4())

        # Create error entry
        error_entry = {
            "error_id": error_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
        }

        # Log the error
        logger.error(f"Error {error_id}: {type(error).__name__}: {str(error)}")
        if context:
            logger.error(f"Error context: {json.dumps(context)}")

        # Save to error log file
        self._save_error_to_file(error_entry)

        return error_id

    def _save_error_to_file(self, error_entry: Dict[str, Any]) -> None:
        """
        Save an error entry to the error log file.

        Args:
            error_entry: Dictionary containing the error information
        """
        try:
            # Read existing errors
            errors = []
            if os.path.exists(self.error_log_path):
                try:
                    with open(self.error_log_path, "r") as f:
                        errors = json.load(f)
                except json.JSONDecodeError:
                    # If file is corrupted, start with empty list
                    errors = []

            # Add new error
            errors.append(error_entry)

            # Write back to file
            with open(self.error_log_path, "w") as f:
                json.dump(errors, f, indent=2)
        except Exception as e:
            # Log to console if file saving fails
            logger.error(f"Error saving to error log file: {e}")

    def handle_error(
        self, error: Exception, context: Dict[str, Any] = None, raise_error: bool = True
    ) -> Optional[str]:
        """
        Handle an error by logging it and optionally re-raising.

        Args:
            error: The exception to handle
            context: Optional dictionary containing context information
            raise_error: Whether to re-raise the error after handling

        Returns:
            String containing the error ID if not raising, None otherwise
        """
        # Log the error
        error_id = self.log_error(error, context)

        # Convert to appropriate error type if needed
        if not isinstance(error, ArtistBuilderError):
            if context and "error_type" in context:
                error_type = context["error_type"]
                if error_type == "input":
                    converted_error = InputError(str(error))
                elif error_type == "llm_pipeline":
                    converted_error = LLMPipelineError(str(error))
                elif error_type == "validation":
                    converted_error = ValidationError(str(error))
                elif error_type == "storage":
                    converted_error = StorageError(str(error))
                elif error_type == "integration":
                    converted_error = IntegrationError(str(error))
                else:
                    converted_error = ArtistBuilderError(str(error))
            else:
                converted_error = ArtistBuilderError(str(error))
        else:
            converted_error = error

        # Re-raise if requested
        if raise_error:
            raise converted_error

        return error_id

    def get_error_by_id(self, error_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an error entry by its ID.

        Args:
            error_id: ID of the error to retrieve

        Returns:
            Dictionary containing the error information, or None if not found
        """
        try:
            # Check if error log file exists
            if not os.path.exists(self.error_log_path):
                logger.warning(f"Error log file not found: {self.error_log_path}")
                return None

            # Read errors from file
            with open(self.error_log_path, "r") as f:
                errors = json.load(f)

            # Find error by ID
            for error in errors:
                if error.get("error_id") == error_id:
                    return error

            logger.warning(f"Error with ID {error_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving error by ID: {e}")
            return None

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve the most recent errors.

        Args:
            limit: Maximum number of errors to retrieve

        Returns:
            List of dictionaries containing error information
        """
        try:
            # Check if error log file exists
            if not os.path.exists(self.error_log_path):
                logger.warning(f"Error log file not found: {self.error_log_path}")
                return []

            # Read errors from file
            with open(self.error_log_path, "r") as f:
                errors = json.load(f)

            # Sort by timestamp (newest first) and limit
            sorted_errors = sorted(
                errors, key=lambda x: x.get("timestamp", ""), reverse=True
            )
            return sorted_errors[:limit]
        except Exception as e:
            logger.error(f"Error retrieving recent errors: {e}")
            return []

    def clear_error_log(self) -> bool:
        """
        Clear the error log file.

        Returns:
            Boolean indicating success
        """
        try:
            # Check if error log file exists
            if not os.path.exists(self.error_log_path):
                logger.warning(f"Error log file not found: {self.error_log_path}")
                return True

            # Create backup before clearing
            backup_path = (
                f"{self.error_log_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            )
            import shutil

            shutil.copy2(self.error_log_path, backup_path)

            # Clear the file
            with open(self.error_log_path, "w") as f:
                f.write("[]")

            logger.info(f"Cleared error log (backup at {backup_path})")
            return True
        except Exception as e:
            logger.error(f"Error clearing error log: {e}")
            return False


class LoggingManager:
    """
    Manages logging for the Artist Profile Builder.
    """

    def __init__(self, log_dir: Optional[str] = None, log_level: int = logging.INFO):
        """
        Initialize the logging manager.

        Args:
            log_dir: Optional path to the log directory. If not provided,
                    defaults to /logs in the project root.
            log_level: Logging level to use (default: INFO)
        """
        # Set default log directory if not provided
        if log_dir is None:
            # Get the project root directory (two levels up from this file)
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            log_dir = os.path.join(project_root, "logs")

        self.log_dir = log_dir
        self.log_level = log_level

        # Ensure log directory exists
        self._ensure_log_directory()

        # Dictionary to store module loggers
        self.loggers = {}

        logger.info(f"Initialized LoggingManager with log directory: {self.log_dir}")

    def _ensure_log_directory(self) -> None:
        """Ensure the log directory exists, creating it if necessary."""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            logger.info(f"Ensured log directory exists: {self.log_dir}")
        except Exception as e:
            logger.error(f"Error creating log directory: {e}")
            # Continue without file logging if directory creation fails

    def get_logger(self, module_name: str) -> logging.Logger:
        """
        Get a logger for a specific module.

        Args:
            module_name: Name of the module

        Returns:
            Logger instance for the module
        """
        # Check if logger already exists
        if module_name in self.loggers:
            return self.loggers[module_name]

        # Create new logger
        module_logger = logging.getLogger(f"artist_builder.{module_name}")
        module_logger.setLevel(self.log_level)

        # Create file handler
        log_file = os.path.join(self.log_dir, f"{module_name}.log")
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(self.log_level)

            # Create formatter
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)

            # Add file handler to logger
            module_logger.addHandler(file_handler)

            logger.info(
                f"Set up logger for module {module_name} with log file {log_file}"
            )
        except Exception as e:
            logger.error(f"Error setting up file logging for module {module_name}: {e}")
            # Continue without file logging if setup fails

        # Store logger
        self.loggers[module_name] = module_logger

        return module_logger

    def set_log_level(self, level: int) -> None:
        """
        Set the log level for all loggers.

        Args:
            level: Logging level to set
        """
        self.log_level = level

        # Update root logger
        logging.getLogger().setLevel(level)

        # Update all module loggers
        for module_logger in self.loggers.values():
            module_logger.setLevel(level)
            for handler in module_logger.handlers:
                handler.setLevel(level)

        logger.info(f"Set log level to {level}")

    def enable_console_logging(self, enable: bool = True) -> None:
        """
        Enable or disable console logging.

        Args:
            enable: Whether to enable console logging
        """
        root_logger = logging.getLogger()

        # Find existing console handlers
        console_handlers = [
            h
            for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler) and h.stream == sys.stdout
        ]

        if enable and not console_handlers:
            # Create new console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)

            # Create formatter
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)

            # Add console handler to root logger
            root_logger.addHandler(console_handler)

            logger.info("Enabled console logging")
        elif not enable and console_handlers:
            # Remove console handlers
            for handler in console_handlers:
                root_logger.removeHandler(handler)

            logger.info("Disabled console logging")

    def log_performance(
        self, module_name: str, operation: str, duration_ms: float
    ) -> None:
        """
        Log performance metrics for an operation.

        Args:
            module_name: Name of the module
            operation: Name of the operation
            duration_ms: Duration of the operation in milliseconds
        """
        # Get performance logger
        perf_logger = self.get_logger("performance")

        # Log performance metric
        perf_logger.info(f"Performance: {module_name}.{operation}: {duration_ms:.2f}ms")

    def log_api_call(
        self, api_name: str, params: Dict[str, Any], success: bool, duration_ms: float
    ) -> None:
        """
        Log an API call.

        Args:
            api_name: Name of the API
            params: Parameters passed to the API
            success: Whether the call was successful
            duration_ms: Duration of the call in milliseconds
        """
        # Get API logger
        api_logger = self.get_logger("api")

        # Log API call
        status = "SUCCESS" if success else "FAILURE"
        api_logger.info(
            f"API Call: {api_name} - {status} - {duration_ms:.2f}ms - Params: {json.dumps(params)}"
        )

    def log_profile_operation(
        self, operation: str, profile_id: str, details: str = ""
    ) -> None:
        """
        Log an operation on an artist profile.

        Args:
            operation: Type of operation (create, update, delete, etc.)
            profile_id: ID of the profile
            details: Optional details about the operation
        """
        # Get profile logger
        profile_logger = self.get_logger("profile_operations")

        # Log profile operation
        profile_logger.info(
            f"Profile Operation: {operation} - Profile ID: {profile_id} - {details}"
        )


def setup_logging_and_error_handling() -> Tuple[LoggingManager, ErrorHandler]:
    """
    Set up logging and error handling for the Artist Profile Builder.

    Returns:
        Tuple of (LoggingManager, ErrorHandler)
    """
    # Get the project root directory
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    log_dir = os.path.join(project_root, "logs")

    # Create logging manager
    logging_manager = LoggingManager(log_dir=log_dir)

    # Create error handler
    error_handler = ErrorHandler(log_dir=log_dir)

    return logging_manager, error_handler


def main():
    """Main function for testing logging and error handling."""
    try:
        # Set up logging and error handling
        logging_manager, error_handler = setup_logging_and_error_handling()

        # Get a logger for a module
        input_logger = logging_manager.get_logger("input_handler")
        input_logger.info("This is a test log message from the input handler")

        # Log performance
        logging_manager.log_performance("llm_pipeline", "generate_profile", 1250.5)

        # Log API call
        logging_manager.log_api_call(
            "llm_orchestrator.generate_text",
            {"prompt": "Generate artist profile", "max_tokens": 1024},
            True,
            850.3,
        )

        # Log profile operation
        logging_manager.log_profile_operation(
            "create",
            "12345678-1234-5678-1234-567812345678",
            "Created new electronic artist profile",
        )

        # Test error handling
        try:
            # Simulate an error
            raise ValueError("This is a test error")
        except Exception as e:
            # Handle the error
            error_id = error_handler.handle_error(
                e,
                context={"module": "test", "operation": "main", "error_type": "input"},
                raise_error=False,
            )
            print(f"Error handled with ID: {error_id}")

            # Retrieve the error
            error_entry = error_handler.get_error_by_id(error_id)
            print(f"Retrieved error: {json.dumps(error_entry, indent=2)}")

        # Get recent errors
        recent_errors = error_handler.get_recent_errors(limit=5)
        print(f"Recent errors: {len(recent_errors)}")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
