# boot_test.py
import logging
import os
import sys

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# Configure basic logging for the test
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BootTestError(Exception):
    """Custom exception for boot test failures."""

    pass


def run_boot_tests():
    """Runs basic import and configuration checks."""
    logger.info("--- Starting Boot Tests ---")
    errors_found = False

    # Test 1: Core module imports
    logger.info("Test 1: Checking core module imports...")
    try:
        from llm_orchestrator.orchestrator import LLMOrchestrator
        from services.artist_db_service import get_all_artists

        # Try using one function from each to be more thorough
        _ = (
            LLMOrchestrator()
        )  # Instantiate orchestrator         _ = get_all_artists()  # Call DB service function
        # _ = select_next_artist() # This might require more setup, skip for
        # basic boot test
        logger.info("Test 1 PASSED: Core modules imported successfully.")
    except ImportError as e:
        logger.error(f"Test 1 FAILED: Failed to import core modules: {e}")
        errors_found = True
    except Exception as e:
        logger.error(
            f"Test 1 FAILED: Error during core module initialization/use: {e}"
        )
        errors_found = True

    # Test 2: Check essential environment variables (example)
    logger.info("Test 2: Checking essential environment variables...")
    # Add more critical variables as needed
    required_vars = ["DEEPSEEK_API_KEY"]  # Example
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if not missing_vars:
        logger.info(
            "Test 2 PASSED: Essential environment variables seem present."
        )
    else:
        logger.error(
            "Test 2 FAILED: Missing essential environment variables: "
            f"{missing_vars}"
        )
        errors_found = True

    # Test 3: Check directory structure (example)
    logger.info("Test 3: Checking essential directories...")
    required_dirs = [
        os.path.join(PROJECT_ROOT, "logs"),
        os.path.join(PROJECT_ROOT, "output"),
        os.path.join(PROJECT_ROOT, "data"),
    ]
    missing_dirs = [d for d in required_dirs if not os.path.isdir(d)]
    if not missing_dirs:
        logger.info("Test 3 PASSED: Essential directories exist.")
    else:
        logger.error(
            f"Test 3 FAILED: Missing essential directories: {missing_dirs}"
        )
        # Attempt to create them?
        try:
            for d in missing_dirs:
                os.makedirs(d, exist_ok=True)
                logger.info(f"Created missing directory: {d}")
            # Recheck after creation attempt
            missing_dirs_after_create = [
                d for d in required_dirs if not os.path.isdir(d)
            ]
            if missing_dirs_after_create:
                logger.error(
                    f"Test 3 FAILED:                         Still missing directories after creation attempt:                         {missing_dirs_after_create}"
                )
                errors_found = True
            else:
                logger.info(
                    "Test 3 PASSED: Missing directories created successfully."
                )
        except OSError as e:
            logger.error(
                f"Test 3 FAILED: Error creating missing directories: {e}"
            )
            errors_found = True

    logger.info("--- Boot Tests Finished ---")
    if errors_found:
        logger.error("One or more boot tests failed.")
        # Instead of sys.exit(1), raise a specific exception
        raise BootTestError("One or more boot tests failed.")
    else:
        logger.info("All boot tests passed successfully.")
        return True  # Indicate success


if __name__ == "__main__":
    try:
        run_boot_tests()
        sys.exit(0)  # Explicitly exit with 0 on success
    except BootTestError as e:
        print(f"Boot Test Error: {e}", file=sys.stderr)
        sys.exit(
            1
        )  # Exit with 1 specifically on BootTestError     except Exception as e:
        print(f"Unexpected error during boot tests: {e}", file=sys.stderr)
        sys.exit(2)  # Exit with a different code for other errors
