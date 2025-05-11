# modules/suno/suno_orchestrator.py

from schemas.song_metadata import SongMetadata
from modules.suno.suno_logger import SunoLogger
import asyncio
import logging
import os
import sys  # Added for path manipulation
from typing import Dict, Any
from datetime import datetime

# Determine project root for absolute imports when run as script
_project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Use absolute imports now
from modules.suno.suno_state_manager import (  # noqa: E402
    SunoStateManager,
    SunoStateManagerError,
)

# Import the REAL BAS Driver (Assuming it's defined elsewhere, e.g., modules/bas/driver.py)
# from modules.bas.driver import BASDriver # Placeholder for actual import path
# Assuming 'modules.bas.driver' could contain the real one or a dispatcher
from modules.bas.driver import BASDriver
from modules.suno.suno_ui_translator import (  # noqa: E402
    SunoUITranslator,
    SunoUITranslatorError,
    MockBASDriver,  # MockBASDriver is kept for fallback or testing
)
from modules.suno.suno_feedback_loop import (  # noqa: E402
    SunoFeedbackLoop,
    SunoFeedbackLoopError,
)

logger = logging.getLogger(__name__)


class SunoOrchestratorError(Exception):
    """Custom exception for Suno Orchestrator errors."""

    pass


class SunoOrchestrator:
    """Orchestrates the Suno.ai web UI automation process via BAS."""

    def __init__(self, config: Dict[str, Any]):
        """Initializes the Suno Orchestrator.

        Args:
            config: Configuration dictionary containing paths, retry limits,
                    LLM validator config, BAS driver config, etc.
        """
        logger.info("STAGE: Initializing SunoOrchestrator.")
        self.config = config
        self.state_dir = config.get("state_dir", "./suno_run_states")
        self.log_dir = config.get("log_dir", "./suno_run_logs")
        self.screenshot_dir = config.get(
            "screenshot_dir", "./suno_validation_screenshots"
        )

        logger.debug(f"State directory: {self.state_dir}")
        logger.debug(f"Log directory: {self.log_dir}")
        logger.debug(f"Screenshot directory: {self.screenshot_dir}")

        os.makedirs(self.state_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)
        logger.info("Ensured all necessary directories exist.")

        self.state_manager = SunoStateManager(state_dir=self.state_dir)
        logger.debug("SunoStateManager initialized.")

        # --- BAS Driver Instantiation ---
        # TODO: CRITICAL - Replace MockBASDriver logic with the actual BAS driver integration.
        # The real BASDriver class and its import path need to be confirmed and robustly integrated.
        # The current logic attempts to use a real driver if configured, otherwise defaults to Mock.
        bas_driver_config = config.get("bas_driver_config", {})
        use_real_driver = bas_driver_config.get("use_real_bas_driver", False)
        connection_string_valid = (
            bas_driver_config.get("connection_string")
            and bas_driver_config.get("connection_string")
            != "dummy_replace_with_real_connection_string"
        )

        if use_real_driver and connection_string_valid:
            logger.info(
                (
                    "Attempting to initialize REAL BAS Driver. "
                    "Ensure 'BASDriver' from 'modules.bas.driver' is the correct real driver class."
                )
            )
            try:
                # This assumes 'from modules.bas.driver import BASDriver' imports the REAL driver
                self.bas_driver_instance = BASDriver(bas_driver_config)
                logger.info("Successfully initialized REAL BAS Driver.")
            except Exception as e:
                logger.error(
                    f"Failed to initialize REAL BAS Driver: {e}. Falling back to MockBASDriver.",
                    exc_info=True,
                )
                self.bas_driver_instance = MockBASDriver()  # Fallback to mock
        else:
            if not use_real_driver:
                logger.warning(
                    "Configuration 'use_real_bas_driver' is false or not set. Using MockBASDriver."
                )
            elif not connection_string_valid:
                logger.warning(
                    "BAS Driver connection string missing, dummy, or invalid. Using MockBASDriver."
                )
            self.bas_driver_instance = MockBASDriver()
            logger.info("MockBASDriver initialized.")
        # --- End BAS Driver Instantiation ---

        self.ui_translator = SunoUITranslator(
            bas_driver=self.bas_driver_instance
        )
        logger.debug("SunoUITranslator initialized.")
        self.feedback_loop = SunoFeedbackLoop(
            bas_driver=self.bas_driver_instance,
            llm_validator_config=config.get("llm_validator_config", {}),
            screenshot_dir=self.screenshot_dir,
        )
        logger.debug("SunoFeedbackLoop initialized.")
        self.logger = SunoLogger(log_dir=self.log_dir)
        logger.debug("SunoLogger initialized.")
        logger.info("Suno Orchestrator initialized with all components.")

    async def generate_song(
        self, generation_prompt: Dict[str, Any]
    ) -> SongMetadata:
        run_id = generation_prompt.get("run_id")
        if not run_id:
            run_id = f"suno_run_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            generation_prompt["run_id"] = run_id
            logger.warning(
                f"Missing 'run_id' in generation_prompt. Generated: {run_id}"
            )

        self.logger.start_run(run_id, generation_prompt)
        logger.info(f"[{run_id}] STAGE: Starting Suno generation process.")

        try:
            logger.info(f"[{run_id}] STAGE: Loading current state.")
            current_state = self.state_manager.load_state(run_id) or {}
            # Initialize start_step for the very first attempt or resumption
            # This will be updated within the retry loop if specific retry_actions are applied
            # or reset to 0 for a full sequence retry.
            effective_start_step = (
                current_state.get("last_completed_step", -1) + 1
            )
            logger.info(
                f"[{run_id}] Loaded state. Initial effective_start_step: {effective_start_step}. Run data: {current_state}"
            )

            if effective_start_step == 0:
                logger.info(
                    f"[{run_id}] STAGE: Translating prompt to UI actions (first run or full restart)."
                )
                ui_actions = self.ui_translator.translate_prompt_to_actions(
                    generation_prompt
                )
                current_state["planned_actions"] = ui_actions
                self.state_manager.save_state(run_id, current_state)
                logger.debug(f"[{run_id}] Saved initial planned actions.")
            else:
                ui_actions = current_state.get("planned_actions", [])
                if not ui_actions:
                    logger.error(
                        f"[{run_id}] Cannot resume run: Missing 'planned_actions' in state."
                    )
                    raise SunoOrchestratorError(
                        f"[{run_id}] Cannot resume run: Missing 'planned_actions' in state."
                    )
                logger.info(
                    f"[{run_id}] Resuming with existing planned_actions."
                )

            logger.info(
                f"[{run_id}] STAGE: UI Action planning complete. Total actions: {len(ui_actions)}."
            )

            max_retries = self.config.get("max_retries", 3)
            current_retry_attempt_count = current_state.get(
                "current_retry_count", 0
            )
            overall_success = False

            # This variable will hold retry_actions from the feedback loop for the current failed step
            # It's reset at the start of each main retry attempt implicitly by not being carried over unless needed

            while (
                current_retry_attempt_count < max_retries
                and not overall_success
            ):
                logger.info(
                    f"[{run_id}] STAGE: Entering execution attempt {current_retry_attempt_count + 1}/{max_retries}. Current start_step for this attempt: {effective_start_step}"
                )
                action_results = current_state.get("action_results", [])
                current_attempt_step_success = (
                    True  # Tracks success of steps within this current attempt
                )
                llm_suggested_retry_actions_for_failed_step = (
                    None  # Reset for each attempt
                )

                for i in range(effective_start_step, len(ui_actions)):
                    action = ui_actions[i]
                    step_index = i  # Absolute index in the potentially modified ui_actions list
                    logger.info(
                        f"[{run_id}] Attempt {current_retry_attempt_count + 1}, Executing action {step_index + 1}/{len(ui_actions)}: {action.get('action')}"
                    )
                    self.logger.log_event(
                        run_id,
                        "step_start",
                        f"Executing action {step_index+1}/{len(ui_actions)}: {action.get('action')}",
                        {"action": action},
                    )

                    action_result = await self.ui_translator.execute_action(
                        action
                    )
                    validation_result = await self.feedback_loop.validate_step(
                        run_id, step_index, action, action_result
                    )
                    self.logger.log_step(
                        run_id,
                        step_index,
                        action,
                        action_result,
                        validation_result,
                    )

                    if len(action_results) <= step_index:
                        action_results.append(action_result)
                    else:
                        action_results[step_index] = action_result
                    current_state["action_results"] = (
                        action_results  # Persist results immediately
                    )

                    if not validation_result.get("approved"):
                        logger.warning(
                            f"[{run_id}] VALIDATION FAILED for step {step_index}. Feedback: {validation_result.get('feedback')}"
                        )
                        current_attempt_step_success = False
                        llm_suggested_retry_actions_for_failed_step = (
                            await self.feedback_loop.get_retry_actions(
                                validation_result
                            )
                        )

                        if llm_suggested_retry_actions_for_failed_step:
                            logger.info(
                                f"[{run_id}] LLM suggested fix actions for step {step_index}. Applying and restarting inner action loop for this attempt."
                            )
                            # Modify ui_actions: replace current failed action and subsequent ones if needed, or insert before/after.
                            # For simplicity, this example replaces from current step onwards with LLM's plan.
                            # A more sophisticated approach might involve more granular splicing.
                            ui_actions = (
                                ui_actions[:step_index]
                                + llm_suggested_retry_actions_for_failed_step
                            )  # + ui_actions[step_index+1:] if only replacing one step
                            current_state["planned_actions"] = ui_actions
                            logger.info(
                                f"[{run_id}] New action plan has {len(ui_actions)} steps. Restarting action sequence from failed step {step_index} within current attempt."
                            )
                            effective_start_step = step_index  # Set start for the re-evaluation of the inner loop
                        else:
                            logger.error(
                                f"[{run_id}] Validation failed for step {step_index}, and no retry actions suggested by LLM. This attempt will fail."
                            )
                        self.state_manager.save_state(
                            run_id, current_state
                        )  # Save state after failed step and potential action plan update
                        break  # Break from this attempt's action loop (for i in range...)
                    else:
                        logger.info(
                            f"[{run_id}] Step {step_index} validated successfully."
                        )
                        current_state["last_completed_step"] = step_index
                        self.state_manager.save_state(run_id, current_state)
                        logger.debug(
                            f"[{run_id}] Saved state after successful step {step_index}."
                        )
                        effective_start_step = (
                            step_index + 1
                        )  # Next step in this attempt

                # After iterating through actions for the current attempt
                if current_attempt_step_success:
                    overall_success = True
                    logger.info(
                        f"[{run_id}] STAGE: All steps completed and validated successfully in attempt {current_retry_attempt_count + 1}."
                    )
                else:  # Current attempt failed (either a step failed validation, or LLM fix also failed)
                    current_retry_attempt_count += 1
                    current_state["current_retry_count"] = (
                        current_retry_attempt_count
                    )
                    self.state_manager.save_state(run_id, current_state)
                    logger.warning(
                        f"[{run_id}] Execution attempt {current_retry_attempt_count}/{max_retries} (previously {current_retry_attempt_count-1}+1) failed."
                    )

                    if current_retry_attempt_count < max_retries:
                        logger.info(
                            f"[{run_id}] Preparing for main retry attempt {current_retry_attempt_count + 1}. Waiting for {self.config.get('retry_delay', 5)}s..."
                        )
                        await asyncio.sleep(self.config.get("retry_delay", 5))

                        if llm_suggested_retry_actions_for_failed_step:
                            # If LLM actions were applied, the next attempt continues from the modified plan and effective_start_step
                            logger.info(
                                f"[{run_id}] Next attempt will use LLM-modified action plan, starting from step {effective_start_step}."
                            )
                        else:
                            # No LLM fix, or LLM fix also failed to make the step pass. Reset for a full sequence retry.
                            logger.info(
                                f"[{run_id}] No LLM fix was applied or it failed. Resetting to attempt full sequence from beginning (step 0) for next main retry."
                            )
                            effective_start_step = 0
                            current_state["last_completed_step"] = (
                                -1
                            )  # Reset for full retry
                            # Optionally, re-translate prompt to actions if the original plan is suspect
                            # ui_actions = self.ui_translator.translate_prompt_to_actions(generation_prompt)
                            # current_state["planned_actions"] = ui_actions
                            self.state_manager.save_state(
                                run_id, current_state
                            )  # Save reset state
                    else:
                        logger.error(
                            f"[{run_id}] STAGE: All {max_retries} main retry attempts failed."
                        )

            # After the while loop (retries exhausted or overall_success)
            if overall_success:
                logger.info(
                    f"[{run_id}] STAGE: Extracting final output after successful run."
                )
                final_output_data = (
                    await self.ui_translator.extract_final_output(
                        action_results
                    )
                )
                self.state_manager.save_final_state(
                    run_id, final_output_data, status="completed"
                )
                self.logger.end_run(
                    run_id, final_output_data, status="completed"
                )
                logger.info(
                    f"[{run_id}] STAGE: Suno generation process completed successfully."
                )
                song_metadata = SongMetadata(
                    title=generation_prompt.get("title", "Untitled Song"),
                    artist=generation_prompt.get("persona", "AI Artist"),
                    genre=generation_prompt.get("genre"),
                    style_prompt=generation_prompt.get("style"),
                    lyrics=generation_prompt.get("lyrics"),
                    generation_source="suno_bas",
                    suno_song_id=final_output_data.get("suno_song_id"),
                    suno_song_url=final_output_data.get("suno_song_url"),
                )
                return song_metadata
            else:
                error_message = f"[{run_id}] Suno generation failed definitively after {max_retries} retries."
                logger.error(error_message)
                self.state_manager.save_final_state(
                    run_id,
                    {
                        "final_error": error_message,
                        "action_results": action_results,
                    },
                    status="failed",
                    error=error_message,
                )
                self.logger.end_run(
                    run_id,
                    {"final_error": error_message},
                    status="failed",
                    error=error_message,
                )
                logger.error(
                    f"[{run_id}] STAGE: Suno generation process failed after all retries."
                )
                raise SunoOrchestratorError(error_message)

        except (
            SunoStateManagerError,
            SunoUITranslatorError,
            SunoFeedbackLoopError,
        ) as e:
            error_message = f"[{run_id}] STAGE: BAS module error encountered: {type(e).__name__}. Details: {e}"
            logger.error(error_message, exc_info=True)
            self.state_manager.save_final_state(
                run_id,
                {"error_details": str(e)},
                status="failed",
                error=str(e),
            )
            self.logger.end_run(
                run_id,
                {"error_details": str(e)},
                status="failed",
                error=str(e),
            )
            raise SunoOrchestratorError(error_message) from e
        except Exception as e:
            error_message = f"[{run_id}] STAGE: Unexpected critical error: {type(e).__name__}. Details: {e}"
            logger.error(
                error_message, exc_info=True
            )  # Use logger.error for consistency, exc_info for stack trace
            self.state_manager.save_final_state(
                run_id,
                {"error_details": str(e)},
                status="failed",
                error=str(e),
            )
            self.logger.end_run(
                run_id,
                {"error_details": str(e)},
                status="failed",
                error=str(e),
            )
            raise SunoOrchestratorError(error_message) from e


# --- Real Integration Test Case (example, can be run separately) ---
async def run_real_integration_test():
    # Basic logging setup for test
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    # Get the specific logger for this module if not already configured by main app
    module_logger = logging.getLogger(__name__)
    module_logger.info("--- Starting REAL Suno BAS Integration Test --- ")

    try:
        from dotenv import load_dotenv

        dotenv_path = os.path.join(
            os.path.dirname(__file__), "..", "..", ".env"
        )
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)
            module_logger.info(
                f"Loaded environment variables from: {dotenv_path}"
            )
        else:
            module_logger.warning(
                f".env file not found at {dotenv_path}, relying on system environment variables."
            )
    except ImportError:
        module_logger.warning(
            "python-dotenv not installed, cannot load .env file."
        )
    except Exception as e:
        module_logger.error(f"Error loading .env file: {e}")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    orchestrator_config = {
        "state_dir": os.path.join(base_dir, "test_suno_states"),
        "log_dir": os.path.join(base_dir, "test_suno_logs"),
        "screenshot_dir": os.path.join(base_dir, "test_suno_screenshots"),
        "max_retries": 2,
        "retry_delay": 2,
        "llm_validator_config": {
            "api_key": os.getenv("OPENAI_API_KEY", "dummy_llm_key"),
            "model": "gpt-3.5-turbo",
        },
        "bas_driver_config": {
            "use_real_bas_driver": False,  # Set to True to test with real BAS
            "connection_string": os.getenv(
                "BAS_CONNECTION_STRING",
                "dummy_replace_with_real_connection_string",
            ),
        },
    }
    module_logger.info(f"Test Orchestrator Config: {orchestrator_config}")

    orchestrator = SunoOrchestrator(config=orchestrator_config)

    # Example generation prompt for testing
    test_prompt = {
        "run_id": f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "lyrics": "Verse 1:\nSun shining bright, a beautiful day\nBirds are singing, come out and play",
        "style": "Upbeat pop, happy summer vibe",
        "title": "Summer Fun Test Song",
        "make_instrumental": False,
        "model_version": "v3",  # or chirp-v3, etc.
        "persona": "Test AI Artist",
        "workspace": "test_workspace",
        # Add other fields as per your SunoUITranslator needs
    }
    module_logger.info(f"Test Prompt: {test_prompt}")

    try:
        module_logger.info(
            f"Calling generate_song for run_id: {test_prompt['run_id']}"
        )
        song_metadata = await orchestrator.generate_song(test_prompt)
        module_logger.info(f"--- Test Song Generation Successful ---")
        module_logger.info(
            f"Song Metadata: {song_metadata.dict() if hasattr(song_metadata, 'dict') else song_metadata}"
        )
    except SunoOrchestratorError as e:
        module_logger.error(
            f"--- Test Song Generation Failed ---: {e}", exc_info=True
        )
    except Exception as e:
        module_logger.error(
            f"--- Test Encountered Unexpected Error ---: {e}", exc_info=True
        )

    module_logger.info("--- REAL Suno BAS Integration Test Finished --- ")


# --- Fallback Resilience Testing Notes ---
# To test fallback mechanisms and retry logic robustly, consider:
# 1. Configuration-driven failure simulation:
#    - Add a 'debug_simulate_failure' section to the orchestrator_config.
#    - Example: "debug_simulate_failure": {"step_index_to_fail": 5, "failure_type": "validation_error", "attempts_to_fail_for": 1}
#    - The orchestrator (specifically ui_translator or feedback_loop) would check this config
#      at specific points and inject failures or return error-indicating results.
# 2. Special generation_prompt flags:
#    - Include a 'test_flags' field in generation_prompt.
#    - Example: "test_flags": {"force_bas_error_on_action_type": "login", "force_validation_fail_count_for_step_5": 2}
#    - Sub-modules would need to be aware of these flags.
# 3. Mocking specific sub-module failures using a testing framework (e.g., pytest with pytest-asyncio):
#    - Mock methods of ui_translator, feedback_loop, or bas_driver_instance to raise exceptions
#      or return specific error-indicating results during test execution.
#    - Example (pytest):
#      async def test_orchestrator_handles_validation_failure(mocker):
#          mock_validate_step = mocker.patch('modules.suno.suno_feedback_loop.SunoFeedbackLoop.validate_step')
#          mock_validate_step.return_value = {"approved": False, "feedback": "Simulated validation error"}
#          # ... setup orchestrator and call generate_song ...
# This allows for controlled testing of how the orchestrator handles various error scenarios
# and utilizes its retry and fallback strategies, ensuring the system is resilient.

if __name__ == "__main__":
    # This allows running the test case directly if the script is executed.
    # Ensure asyncio event loop is handled correctly for top-level await.
    if sys.version_info >= (3, 7):
        asyncio.run(run_real_integration_test())
    else:  # Basic compatibility for older Python 3 versions if needed
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(run_real_integration_test())
        finally:
            loop.close()
