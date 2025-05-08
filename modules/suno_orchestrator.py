# modules/suno/suno_orchestrator.py

import asyncio
import logging
import json
import os
import sys # Added for path manipulation
from typing import Dict, Any
from datetime import datetime

# Determine project root for absolute imports when run as script
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Use absolute imports now
from modules.suno.suno_state_manager import SunoStateManager, SunoStateManagerError
# Import the REAL BAS Driver (Assuming it's defined elsewhere, e.g., modules/bas/driver.py)
# from modules.bas.driver import BASDriver # Placeholder for actual import path
# Using MockBASDriver temporarily until real driver path is confirmed
from modules.suno.suno_ui_translator import SunoUITranslator, SunoUITranslatorError, MockBASDriver
from modules.suno.suno_feedback_loop import SunoFeedbackLoop, SunoFeedbackLoopError
from modules.suno.suno_logger import SunoLogger

# Import the schema
from schemas.song_metadata import SongMetadata

# Placeholder for actual BAS interaction library
# Replace MockBASDriver with the real driver instance
# Assuming BASDriver takes config, adjust as needed
# bas_driver = BASDriver(config.get("bas_driver_config", {})) # Instantiate the REAL driver
bas_driver = MockBASDriver() # KEEPING MOCK FOR NOW - NEED REAL DRIVER PATH/CLASS

logger = logging.getLogger(__name__)

class SunoOrchestratorError(Exception):
    """Custom exception for Suno Orchestrator errors."""
    pass

class SunoOrchestrator:
    """Orchestrates the Suno.ai web UI automation process via BAS."""

    def __init__(self, config: Dict[str, Any]):
        """Initializes the Suno Orchestrator.

        Args:
            config: Configuration dictionary containing paths, retry limits, LLM validator config, etc.
                    Example: {
                        "state_dir": "./suno_run_states",
                        "log_dir": "./suno_run_logs",
                        "screenshot_dir": "./suno_validation_screenshots",
                        "max_retries": 3,
                        "retry_delay": 5,
                        "llm_validator_config": { "api_key": "...", "model": "..." },
                        "bas_driver_config": { "connection_string": "..." } # Config for the real BAS driver
                    }
        """
        self.config = config
        self.state_dir = config.get("state_dir", "./suno_run_states")
        self.log_dir = config.get("log_dir", "./suno_run_logs")
        self.screenshot_dir = config.get("screenshot_dir", "./suno_validation_screenshots")

        # Ensure directories exist
        os.makedirs(self.state_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)

        # Initialize components
        self.state_manager = SunoStateManager(state_dir=self.state_dir)

        # Instantiate the REAL BAS driver here when path/class is known
        # self.bas_driver_instance = BASDriver(config.get("bas_driver_config", {}))
        # TODO: Replace MockBASDriver with the actual BAS driver import and instantiation
        bas_driver_config = config.get("bas_driver_config", {})
        if bas_driver_config.get("connection_string") and bas_driver_config.get("connection_string") != "dummy_replace_with_real_connection_string":
            logger.info("Attempting to initialize REAL BAS Driver (assuming class BASDriver exists).")
            # from modules.bas.driver import BASDriver # Assumed path
            # self.bas_driver_instance = BASDriver(bas_driver_config)
            self.bas_driver_instance = MockBASDriver() # Replace with real one when available
            logger.warning("Using MockBASDriver as placeholder for real BAS driver.") # Remove when real driver is used
        else:
            logger.warning("BAS Driver connection string missing or dummy. Using MockBASDriver.")
            self.bas_driver_instance = MockBASDriver()

        # Pass the actual BAS driver instance here
        self.ui_translator = SunoUITranslator(bas_driver=self.bas_driver_instance)
        self.feedback_loop = SunoFeedbackLoop(
            bas_driver=self.bas_driver_instance, # Use the instantiated driver
            llm_validator_config=config.get("llm_validator_config", {}),
            screenshot_dir=self.screenshot_dir
        )
        self.logger = SunoLogger(log_dir=self.log_dir)
        logger.info("Suno Orchestrator initialized with all components.")

    async def generate_song(self, generation_prompt: Dict[str, Any]) -> SongMetadata:
        """Handles the end-to-end process of generating a song on Suno.ai via BAS.

        Args:
            generation_prompt: A structured dictionary containing all necessary
                               details for song generation (lyrics, style, model,
                               persona, workspace, title etc.). Must include a unique `run_id`.

        Returns:
            A SongMetadata object containing details of the generated song.

        Raises:
            SunoOrchestratorError: If the generation process fails after retries or encounters errors.
        """
        run_id = generation_prompt.get("run_id")
        if not run_id:
            run_id = f"suno_run_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            generation_prompt["run_id"] = run_id
            logger.warning(f"Missing 'run_id' in generation_prompt. Generated: {run_id}")

        self.logger.start_run(run_id, generation_prompt)
        logger.info(f"Starting Suno generation for run_id: {run_id}")

        try:
            current_state = self.state_manager.load_state(run_id) or {}
            start_step = current_state.get("last_completed_step", -1) + 1
            logger.info(f"[{run_id}] Loaded state. Starting/Resuming from step {start_step}.")

            if start_step == 0:
                ui_actions = self.ui_translator.translate_prompt_to_actions(generation_prompt)
                current_state["planned_actions"] = ui_actions
                self.state_manager.save_state(run_id, current_state)
            else:
                ui_actions = current_state.get("planned_actions", [])
                if not ui_actions:
                     raise SunoOrchestratorError(f"[{run_id}] Cannot resume run: Missing 'planned_actions' in state.")

            logger.info(f"[{run_id}] Total planned actions: {len(ui_actions)}.")

            max_retries = self.config.get("max_retries", 3)
            current_retry = current_state.get("current_retry_count", 0)
            overall_success = False
            retry_actions = None

            while current_retry < max_retries and not overall_success:
                logger.info(f"[{run_id}] Starting execution sequence (Attempt {current_retry + 1}/{max_retries})")
                action_results = current_state.get("action_results", [])
                step_success = True

                for i in range(start_step, len(ui_actions)):
                    action = ui_actions[i]
                    step_index = i
                    self.logger.log_event(run_id, "step_start", f"Executing action {step_index+1}/{len(ui_actions)}: {action.get('action')}", {"action": action})

                    action_result = await self.ui_translator.execute_action(action)
                    validation_result = await self.feedback_loop.validate_step(run_id, step_index, action, action_result)
                    self.logger.log_step(run_id, step_index, action, action_result, validation_result)

                    if len(action_results) <= step_index:
                        action_results.append(action_result)
                    else:
                        action_results[step_index] = action_result
                    current_state["action_results"] = action_results

                    if not validation_result.get("approved"):
                        logger.warning(f"[{run_id}] Step {step_index} failed validation: {validation_result.get('feedback')}")
                        step_success = False
                        retry_actions = await self.feedback_loop.get_retry_actions(validation_result)
                        if retry_actions:
                            logger.info(f"[{run_id}] Applying suggested fix actions from LLM.")
                            ui_actions = ui_actions[:step_index] + retry_actions
                            current_state["planned_actions"] = ui_actions
                            logger.info(f"[{run_id}] New action plan: {len(ui_actions)} steps. Restarting sequence.")
                            start_step = step_index
                        else:
                            logger.error(f"[{run_id}] Validation failed, but no retry actions suggested. Aborting attempt.")
                        break
                    else:
                        logger.info(f"[{run_id}] Step {step_index} validated successfully.")
                        current_state["last_completed_step"] = step_index
                        self.state_manager.save_state(run_id, current_state)

                if step_success:
                    overall_success = True
                    logger.info(f"[{run_id}] All steps completed and validated successfully in attempt {current_retry + 1}.")
                else:
                    current_retry += 1
                    current_state["current_retry_count"] = current_retry
                    self.state_manager.save_state(run_id, current_state)
                    if current_retry < max_retries:
                        logger.info(f"[{run_id}] Retrying sequence (attempt {current_retry + 1}). Waiting {self.config.get('retry_delay', 5)}s...")
                        await asyncio.sleep(self.config.get("retry_delay", 5))
                        if not retry_actions:
                             start_step = 0
                             logger.info(f"[{run_id}] Restarting action sequence from beginning for retry.")
                    else:
                        logger.error(f"[{run_id}] Sequence failed after {max_retries} attempts.")

            if overall_success:
                final_output_data = await self.ui_translator.extract_final_output(action_results)
                self.state_manager.save_final_state(run_id, final_output_data, status="completed")
                self.logger.end_run(run_id, final_output_data, status="completed")
                logger.info(f"[{run_id}] Suno generation completed successfully.")

                song_metadata = SongMetadata(
                    title=generation_prompt.get("title", "Untitled Song"),
                    artist=generation_prompt.get("persona", "AI Artist"),
                    genre=generation_prompt.get("genre"),
                    style_prompt=generation_prompt.get("style"),
                    lyrics=generation_prompt.get("lyrics"),
                    generation_source="suno_bas",
                    suno_song_id=final_output_data.get("suno_song_id"),
                    suno_song_url=final_output_data.get("suno_song_url")
                )
                return song_metadata
            else:
                error_message = f"[{run_id}] Suno generation failed after {max_retries} retries."
                logger.error(error_message)
                self.state_manager.save_final_state(run_id, None, status="failed", error=error_message)
                self.logger.end_run(run_id, None, status="failed", error=error_message)
                raise SunoOrchestratorError(error_message)

        except (SunoStateManagerError, SunoUITranslatorError, SunoFeedbackLoopError) as e:
            error_message = f"[{run_id}] BAS module error during Suno generation: {e}"
            logger.error(error_message)
            self.state_manager.save_final_state(run_id, None, status="failed", error=str(e))
            self.logger.end_run(run_id, None, status="failed", error=str(e))
            raise SunoOrchestratorError(error_message) from e
        except Exception as e:
            error_message = f"[{run_id}] Unexpected error during Suno generation: {e}"
            logger.exception(error_message)
            self.state_manager.save_final_state(run_id, None, status="failed", error=str(e))
            self.logger.end_run(run_id, None, status="failed", error=str(e))
            raise SunoOrchestratorError(error_message) from e

# --- Real Integration Test Case --- 
async def run_real_integration_test():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    logger.info("--- Starting REAL Suno BAS Integration Test --- ")

    # Load .env file
    try:
        from dotenv import load_dotenv
        # Assumes .env is in the project root, 2 levels up from modules/suno/
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env') 
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)
            logger.info(f"Loaded environment variables from: {dotenv_path}")
        else:
             logger.warning(f".env file not found at {dotenv_path}, relying on system environment variables.")
    except ImportError:
        logger.warning("python-dotenv not installed, cannot load .env file.")
    except Exception as e:
        logger.error(f"Error loading .env file: {e}")

    # Define configuration using environment variables
    base_dir = os.path.dirname(os.path.abspath(__file__))
    orchestrator_config = {
        "state_dir": os.path.join(base_dir, "real_test_suno_run_states"),
        "log_dir": os.path.join(base_dir, "real_test_suno_run_logs"),
        "screenshot_dir": os.path.join(base_dir, "real_test_suno_screenshots"),
        "max_retries": 2, # Keep retries low for initial testing
        "retry_delay": 10, # Increase delay slightly for real UI
        "llm_validator_config": {
            "api_key": os.getenv("LLM_VALIDATOR_API_KEY"),
            "model": os.getenv("LLM_VALIDATOR_MODEL")
        },
        "bas_driver_config": {
            "connection_string": os.getenv("BAS_CONNECTION_STRING")
            # Add other BAS driver specific configs if needed
        }
    }
    logger.info(f"Orchestrator Config (API keys masked): { {k: (v if k != 'llm_validator_config' else {vk: ('***' if vk == 'api_key' else vv) for vk, vv in v.items()}) for k, v in orchestrator_config.items()} }")

    # Instantiate the orchestrator
    orchestrator = SunoOrchestrator(orchestrator_config)

    # Define the test prompt for the real run
    real_test_prompt = {
        "run_id": f"real_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}", # Simplified run_id for testing
        "title": "Cyberpunk Lullaby",
        "lyrics": "[Verse 1]\nRain streaks down the chrome\nNeon signs hum low\nA lonely android weeps\nAs the city sleeps\n\n[Chorus]\nBinary dreams in the code\nA lullaby for the lost road\nElectric sheep in the night\nFlickering, fading light",
        "style": "Slow tempo, melancholic synthwave, female vocal, reverb, atmospheric pads",
        "model": "v4.5", # Use a model likely supported by UI
        "persona": "Data Ghost",
        "workspace": "Integration Tests",
        "genre": "Synthwave"
    }
    logger.info(f"Using generation prompt: {real_test_prompt}")

    try:
        song_metadata_result: SongMetadata = await orchestrator.generate_song(real_test_prompt)
        print(f"\n--- REAL Generation Result --- \n{song_metadata_result.model_dump_json(indent=2)}")
    except SunoOrchestratorError as e:
        print(f"\n--- REAL Generation Failed --- \n{e}")
    except Exception as e:
        logger.exception("Unhandled exception during real integration test.")
        print(f"\n--- REAL Generation Failed (Unexpected Error) --- \n{e}")

    logger.info("--- REAL Suno BAS Integration Test Finished --- ")

if __name__ == "__main__":
    # Add project root to path to allow absolute imports when run as script
    # This is handled by the sys.path manipulation at the top of the file now
    
    # Run the real integration test function
    asyncio.run(run_real_integration_test())


