# boot_test.py
import sys
import os
import logging

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BootTest")

logger.info("Starting boot test...")

success = True

try:
    logger.info("Importing artist_db_service...")
    from services.artist_db_service import initialize_database, get_all_artists

    logger.info("Initializing artist DB...")
    initialize_database()
    logger.info("Fetching artists...")
    get_all_artists()
    logger.info("Artist DB Service OK.")
except Exception as e:
    logger.error(f"Error testing artist_db_service: {e}", exc_info=True)
    success = False

try:
    logger.info("Importing LLMOrchestrator...")
    from llm_orchestrator.orchestrator import LLMOrchestrator

    logger.info("Initializing LLMOrchestrator...")
    LLMOrchestrator(primary_model="deepseek:deepseek-chat")  # Provide a default model
    logger.info("LLMOrchestrator OK.")
except Exception as e:
    logger.error(f"Error testing LLMOrchestrator: {e}", exc_info=True)
    success = False

try:
    logger.info("Importing release_chain...")
    from release_chain.release_chain import (
        process_approved_run,
    )  # Just importing main function

    logger.info("Release Chain import OK.")
except Exception as e:
    logger.error(f"Error testing release_chain import: {e}", exc_info=True)
    success = False

try:
    logger.info("Importing artist_batch_runner...")
    # Importing the whole module might execute top-level code, be careful
    # Let's try importing a specific function/class if possible, or just the module
    import batch_runner.artist_batch_runner

    logger.info("Artist Batch Runner import OK.")
except Exception as e:
    logger.error(f"Error testing artist_batch_runner import: {e}", exc_info=True)
    success = False

if success:
    logger.info("Boot test simulation completed successfully.")
    sys.exit(0)
else:
    logger.error("Boot test simulation encountered errors.")
    sys.exit(1)
