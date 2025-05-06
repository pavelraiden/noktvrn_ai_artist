# modules/suno/suno_orchestrator.py

import asyncio
import logging
import json
import os
from typing import Dict, Any
from datetime import datetime # Added for example usage

# Import the implemented modules
from .suno_state_manager import SunoStateManager, SunoStateManagerError
from .suno_ui_translator import SunoUITranslator, SunoUITranslatorError, MockBASDriver # Using Mock driver for now
from .suno_feedback_loop import SunoFeedbackLoop, SunoFeedbackLoopError
from .suno_logger import SunoLogger

# Import the schema
from schemas.song_metadata import SongMetadata

# Placeholder for actual BAS interaction library
# Replace MockBASDriver with the real driver when available
bas_driver = MockBASDriver() # Instantiate the mock driver

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
                        "llm_validator_config": { "api_key": "dummy", "model": "validator" }
                        # Add BAS driver config here if needed
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
        # Pass the actual BAS driver instance here
        self.ui_translator = SunoUITranslator(bas_driver=bas_driver)
        self.feedback_loop = SunoFeedbackLoop(
            bas_driver=bas_driver,
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
            # Generate a default run_id if not provided, although it should be
            run_id = f"suno_run_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            generation_prompt["run_id"] = run_id
            logger.warning(f"Missing 'run_id' in generation_prompt. Generated: {run_id}")

        self.logger.start_run(run_id, generation_prompt)
        logger.info(f"Starting Suno generation for run_id: {run_id}")

        try:
            # 1. Load state or initialize if new run
            current_state = self.state_manager.load_state(run_id) or {}
            start_step = current_state.get("last_completed_step", -1) + 1
            logger.info(f"[{run_id}] Loaded state. Starting/Resuming from step {start_step}.")

            # 2. Translate prompt to initial UI actions (only if starting fresh)
            if start_step == 0:
                ui_actions = self.ui_translator.translate_prompt_to_actions(generation_prompt)
                current_state["planned_actions"] = ui_actions
                self.state_manager.save_state(run_id, current_state)
            else:
                ui_actions = current_state.get("planned_actions", [])
                if not ui_actions:
                     raise SunoOrchestratorError(f"[{run_id}] Cannot resume run: Missing 'planned_actions' in state.")

            logger.info(f"[{run_id}] Total planned actions: {len(ui_actions)}.")

            # 3. Execute actions with feedback loop
            max_retries = self.config.get("max_retries", 3)
            current_retry = current_state.get("current_retry_count", 0)
            overall_success = False
            retry_actions = None # Initialize retry_actions

            while current_retry < max_retries and not overall_success:
                logger.info(f"[{run_id}] Starting execution sequence (Attempt {current_retry + 1}/{max_retries})")
                action_results = current_state.get("action_results", [])
                step_success = True

                for i in range(start_step, len(ui_actions)):
                    action = ui_actions[i]
                    step_index = i # Use 0-based index consistent with list
                    self.logger.log_event(run_id, "step_start", f"Executing action {step_index+1}/{len(ui_actions)}: {action.get('action')}", {"action": action})

                    action_result = await self.ui_translator.execute_action(action)

                    # Validate the step using the feedback loop
                    validation_result = await self.feedback_loop.validate_step(run_id, step_index, action, action_result)

                    # Log the step outcome
                    self.logger.log_step(run_id, step_index, action, action_result, validation_result)

                    # Store result
                    if len(action_results) <= step_index:
                        action_results.append(action_result)
                    else:
                        action_results[step_index] = action_result # Overwrite on retry
                    current_state["action_results"] = action_results

                    if not validation_result.get("approved"):
                        logger.warning(f"[{run_id}] Step {step_index} failed validation: {validation_result.get('feedback')}")
                        step_success = False
                        # Attempt to get retry actions from LLM
                        retry_actions = await self.feedback_loop.get_retry_actions(validation_result)
                        if retry_actions:
                            logger.info(f"[{run_id}] Applying suggested fix actions from LLM.")
                            # Modify the plan: replace current/future actions or insert fix actions
                            # Simple strategy: Replace the rest of the plan with the fix
                            ui_actions = ui_actions[:step_index] + retry_actions
                            current_state["planned_actions"] = ui_actions # Update plan in state
                            logger.info(f"[{run_id}] New action plan: {len(ui_actions)} steps. Restarting sequence.")
                            start_step = step_index # Restart from the failed step with new actions
                        else:
                            logger.error(f"[{run_id}] Validation failed, but no retry actions suggested. Aborting attempt.")
                        break # Break inner loop (steps) to retry the sequence or fail
                    else:
                        logger.info(f"[{run_id}] Step {step_index} validated successfully.")
                        current_state["last_completed_step"] = step_index
                        # Save state after each successful step
                        self.state_manager.save_state(run_id, current_state)

                # --- End of steps loop ---

                if step_success:
                    overall_success = True
                    logger.info(f"[{run_id}] All steps completed and validated successfully in attempt {current_retry + 1}.")
                else:
                    current_retry += 1
                    current_state["current_retry_count"] = current_retry
                    self.state_manager.save_state(run_id, current_state) # Save retry count
                    if current_retry < max_retries:
                        logger.info(f"[{run_id}] Retrying sequence (attempt {current_retry + 1}). Waiting {self.config.get('retry_delay', 5)}s...")
                        await asyncio.sleep(self.config.get("retry_delay", 5)) # Wait before retrying
                        # Reset start_step for the next attempt if not using targeted retry actions
                        if not retry_actions: # If no specific fix, restart from beginning of sequence
                             start_step = 0
                             logger.info(f"[{run_id}] Restarting action sequence from beginning for retry.")
                    else:
                        logger.error(f"[{run_id}] Sequence failed after {max_retries} attempts.")

            # --- End of retry loop ---

            # 4. Handle final state (success or failure)
            if overall_success:
                # Extract final output (e.g., song URL, metadata)
                # Assuming extract_final_output returns a dict like {'suno_song_id': '...', 'suno_song_url': '...'}
                final_output_data = await self.ui_translator.extract_final_output(action_results)
                self.state_manager.save_final_state(run_id, final_output_data, status="completed")
                self.logger.end_run(run_id, final_output_data, status="completed")
                logger.info(f"[{run_id}] Suno generation completed successfully.")

                # Create SongMetadata object
                song_metadata = SongMetadata(
                    title=generation_prompt.get("title", "Untitled Song"),
                    artist=generation_prompt.get("persona", "AI Artist"),
                    genre=generation_prompt.get("genre"), # Assuming genre might be in prompt
                    style_prompt=generation_prompt.get("style"),
                    lyrics=generation_prompt.get("lyrics"),
                    generation_source="suno_bas",
                    suno_song_id=final_output_data.get("suno_song_id"),
                    suno_song_url=final_output_data.get("suno_song_url")
                    # Add other fields if available from prompt or final_output_data
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
            logger.exception(error_message) # Log full traceback
            self.state_manager.save_final_state(run_id, None, status="failed", error=str(e))
            self.logger.end_run(run_id, None, status="failed", error=str(e))
            raise SunoOrchestratorError(error_message) from e

# Example usage (for testing purposes)
async def main():
    # Setup basic logging for the example
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    # Define directories relative to the script or use absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    orchestrator_config = {
        "state_dir": os.path.join(base_dir, "test_suno_run_states"),
        "log_dir": os.path.join(base_dir, "test_suno_run_logs"),
        "screenshot_dir": os.path.join(base_dir, "test_suno_screenshots"),
        "max_retries": 2,
        "retry_delay": 3,
        "llm_validator_config": { "api_key": "dummy_key", "model": "validator-model-v1" }
        # Add BAS driver config here if needed
    }
    orchestrator = SunoOrchestrator(orchestrator_config)

    test_prompt = {
        "run_id": f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "title": "Cosmic Drift",
        "lyrics": "Verse 1\nFloating through the void\nStars like diamond dust\nChorus\nCosmic drift, endless night",
        "style": "Ambient space music, ethereal pads, slow tempo",
        "model": "v4.5",
        "persona": "Stellar Voyager",
        "workspace": "Deep Space Sonnets",
        "genre": "Ambient"
    }

    logger.info("--- Starting Test Run --- ")
    try:
        # Ensure the example usage reflects the new return type
        song_metadata_result: SongMetadata = await orchestrator.generate_song(test_prompt)
        print(f"\n--- Generation Result --- \n{song_metadata_result.model_dump_json(indent=2)}")
    except SunoOrchestratorError as e:
        print(f"\n--- Generation Failed --- \n{e}")
    logger.info("--- Test Run Finished --- ")

if __name__ == "__main__":
    asyncio.run(main())

