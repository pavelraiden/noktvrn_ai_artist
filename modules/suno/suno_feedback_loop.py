# modules/suno/suno_feedback_loop.py

import logging
import json
import os
import asyncio
from typing import Dict, Any, Optional, List # Added List

# Placeholder for the actual browser automation driver
from .suno_ui_translator import MockBASDriver # Use the mock driver for now

# Placeholder for LLM interaction client
# This client should be designed to handle retries and enforce JSON output.
class MockLLMValidatorClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        logger.info(f"MockLLMValidatorClient initialized with config: {config}")

    async def validate_ui_state(self, screenshot_path: str, expected_state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates calling an LLM to validate UI state based on a screenshot.

        Enforces strict JSON output format.
        """
        logger.info(f"[MockLLMClient] Validating screenshot: {screenshot_path}")
        await asyncio.sleep(1.5) # Simulate LLM processing time

        # --- Mock LLM Response Logic --- 
        # Simulate different responses based on expected state for testing
        approved = True
        feedback = "Validation successful."
        suggested_fix = None

        action_performed = expected_state.get("action_performed", {})
        action_type = action_performed.get("action")
        target = action_performed.get("target")

        # Example failure scenario: Style input is empty
        if action_type == "input" and target == "style_input" and not expected_state.get("expected_text"): 
            approved = False
            feedback = "Validation failed: The style input field appears empty in the screenshot."
            suggested_fix = [
                {"action": "input", "target": "style_input", "value": "acoustic pop"} # Suggest a default
            ]
        # Example failure scenario: Click failed to navigate (hypothetical)
        elif action_type == "click" and target == "create_button":
             # Let's simulate a case where the LLM thinks the click didn't register
             if hash(screenshot_path) % 3 == 0: # Randomly fail sometimes for testing
                 approved = False
                 feedback = "Validation failed: It seems the \'Create\' button click didn't proceed to the next state."
                 suggested_fix = [
                     {"action": "click", "target": "create_button"} # Suggest clicking again
                 ]
             else:
                 feedback = "Create button clicked, generation likely started."
        
        # --- End Mock LLM Response Logic ---

        response = {
            "approved": approved,
            "feedback": feedback,
            "suggested_fix": suggested_fix
        }

        # Ensure response is valid JSON before returning (as the real client should)
        try:
            json.dumps(response) # Test serialization
            return response
        except TypeError as e:
            logger.error(f"[MockLLMClient] Failed to serialize response: {e}")
            # Fallback response in case of internal error
            return {"approved": False, "feedback": f"Internal LLM client error: {e}", "suggested_fix": None}

# --- End of Mock LLM Client ---

logger = logging.getLogger(__name__)

class SunoFeedbackLoopError(Exception):
    """Custom exception for Feedback Loop errors."""
    pass

class SunoFeedbackLoop:
    """Handles validation of UI actions using screenshots and LLM feedback.
    Enforces strict JSON communication protocol with the LLM validator.
    """

    def __init__(self, bas_driver: Any, llm_validator_config: Dict[str, Any], screenshot_dir: str = "./suno_validation_screenshots"):
        """Initializes the Feedback Loop.

        Args:
            bas_driver: An instance of the browser automation driver.
            llm_validator_config: Configuration for the validator LLM client.
            screenshot_dir: Directory to temporarily store validation screenshots.
        """
        self.driver = bas_driver
        self.llm_config = llm_validator_config
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)
        # Initialize the actual LLM client here
        self.llm_validator = MockLLMValidatorClient(llm_validator_config)
        logger.info("Suno Feedback Loop initialized.")

    async def _take_validation_screenshot(self, run_id: str, step_index: int) -> Optional[str]:
        """Takes a screenshot for validation."""
        filename = os.path.join(self.screenshot_dir, f"run_{run_id}_step_{step_index}_validation.png")
        try:
            # Ensure the driver instance is used correctly
            result = await self.driver.take_screenshot(filename)
            if result.get("success"):
                logger.info(f"Took validation screenshot: {filename}")
                return filename
            else:
                logger.error(f"Failed to take screenshot: {result.get("error")}")
                return None
        except Exception as e:
            logger.error(f"Exception during screenshot: {e}")
            return None

    async def _ask_llm_for_validation(self, screenshot_path: str, expected_state: Dict[str, Any]) -> Dict[str, Any]:
        """Sends screenshot and expected state to LLM for validation, enforcing JSON.

        Args:
            screenshot_path: Path to the validation screenshot.
            expected_state: Dictionary describing what the UI should look like.

        Returns:
            A dictionary containing the LLM's validation result.
            Guaranteed to contain "approved" (bool) and "feedback" (str).
            May contain "suggested_fix" (list or None).

        Raises:
            SunoFeedbackLoopError: If the LLM response is invalid or communication fails.
        """
        logger.info(f"Requesting LLM validation for screenshot: {screenshot_path}")
        try:
            # Use the initialized LLM client instance
            response = await self.llm_validator.validate_ui_state(screenshot_path, expected_state)

            # --- Strict JSON Protocol Enforcement --- 
            if not isinstance(response, dict):
                 raise ValueError(f"LLM response is not a dictionary: {type(response)}")
            if "approved" not in response or not isinstance(response["approved"], bool):
                raise ValueError("LLM response missing or invalid 'approved' key (boolean expected).")
            if "feedback" not in response or not isinstance(response["feedback"], str):
                raise ValueError("LLM response missing or invalid 'feedback' key (string expected).")
            if "suggested_fix" in response and response["suggested_fix"] is not None and not isinstance(response["suggested_fix"], list):
                 raise ValueError("LLM response 'suggested_fix' key must be a list or None.")
            # Optional: Deeper validation of suggested_fix action structure here
            if isinstance(response.get("suggested_fix"), list):
                for fix_action in response["suggested_fix"]:
                    if not isinstance(fix_action, dict) or "action" not in fix_action:
                        raise ValueError("Invalid structure in 'suggested_fix': Each item must be a dict with an 'action' key.")
            # --- End Strict JSON Protocol Enforcement --- 

            logger.info(f"LLM Validation result: Approved={response.get("approved")}, Feedback=\"{response.get("feedback")}\"")
            return response

        except Exception as e:
            logger.error(f"LLM validation request failed or response invalid: {e}")
            # Raise a specific error to be caught by the orchestrator
            raise SunoFeedbackLoopError(f"LLM validation failed: {e}") from e
        finally:
            # Clean up screenshot (optional, based on config)
            # Consider keeping failed screenshots for debugging
            if os.path.exists(screenshot_path):
                 try:
                     # os.remove(screenshot_path)
                     logger.debug(f"Kept screenshot (debug): {screenshot_path}") # Keep for debugging
                 except OSError as e:
                     logger.warning(f"Failed to remove screenshot {screenshot_path}: {e}")

    async def validate_step(self, run_id: str, step_index: int, action: Dict[str, Any], action_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validates a completed UI action step.

        Takes a screenshot, sends it to the LLM validator, and returns the result.

        Args:
            run_id: The unique identifier for the generation run.
            step_index: The index of the step being validated.
            action: The action that was performed.
            action_result: The result returned by the UI translator for the action.

        Returns:
            Validation result dictionary from the LLM, guaranteed to have 'approved' and 'feedback'.
        """
        # If the action itself failed, report failure immediately
        if not action_result.get("success"):
            error_msg = action_result.get("error", "Unknown action execution error")
            logger.warning(f"Action itself failed, skipping LLM validation. Error: {error_msg}")
            return {"approved": False, "feedback": f"Action execution failed: {error_msg}", "suggested_fix": None}

        # Take screenshot
        screenshot_path = await self._take_validation_screenshot(run_id, step_index)
        if not screenshot_path:
            logger.error("Failed to take screenshot, cannot validate step.")
            return {"approved": False, "feedback": "Failed to capture screenshot for validation.", "suggested_fix": None}

        # Define expected state based on the action (can be enhanced)
        expected_state = {
            "action_performed": action,
            "action_result": action_result # Provide action result to LLM context
            }
        if action.get("action") == "input":
            expected_state["expected_text"] = action.get("value")
            expected_state["target_element"] = action.get("target")
        elif action.get("action") == "click":
             expected_state["expected_outcome"] = f"Element {action.get("target")} should be clicked, potentially leading to a state change."
        # Add more context based on action type

        try:
            # Call LLM validator, which enforces JSON structure
            validation_result = await self._ask_llm_for_validation(screenshot_path, expected_state)
            return validation_result
        except SunoFeedbackLoopError as e:
            # Error already logged in _ask_llm_for_validation
            # Return a standard failure format
            return {"approved": False, "feedback": f"LLM validation process failed: {e}", "suggested_fix": None}

    async def get_retry_actions(self, validation_result: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Extracts validated suggested fix actions from the LLM validation result.

        Args:
            validation_result: The result dictionary from the LLM.

        Returns:
            A list of action dictionaries to retry, or None if no valid fix suggested.
        """
        suggested_fix = validation_result.get("suggested_fix")

        # Validate structure (already partially done in _ask_llm_for_validation)
        if isinstance(suggested_fix, list) and len(suggested_fix) > 0:
            valid_actions = []
            for i, action in enumerate(suggested_fix):
                if isinstance(action, dict) and "action" in action:
                    valid_actions.append(action)
                else:
                    logger.warning(f"Invalid action structure in suggested_fix at index {i}: {action}. Skipping this action.")
            
            if valid_actions:
                logger.info(f"Using validated suggested fix actions from LLM: {valid_actions}")
                return valid_actions
            else:
                 logger.warning("LLM suggested fixes, but none had valid structure.")
                 return None
        else:
            logger.info("No suggested fix actions provided or list is empty.")
            return None

# Example usage (for testing purposes)
async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    mock_driver = MockBASDriver() # Use the mock driver
    llm_config = {"api_key": "dummy_key", "model": "validator-model-v1"}
    feedback_loop = SunoFeedbackLoop(mock_driver, llm_config, screenshot_dir="./test_suno_screenshots")

    test_run_id = "feedback_test_002"
    test_step_index = 1

    # Simulate a successful action
    action_ok = {"action": "input", "target": "lyrics_input", "value": "Hello world"}
    result_ok = {"success": True, "selector": "#lyrics", "text": "Hello world"}
    print("--- Testing Successful Validation ---")
    validation_ok = await feedback_loop.validate_step(test_run_id, test_step_index, action_ok, result_ok)
    print(f"Validation OK Result: {json.dumps(validation_ok, indent=2)}")

    # Simulate a failed action (empty style input -> mock LLM suggests fix)
    test_step_index = 2
    action_fail = {"action": "input", "target": "style_input", "value": ""} # Empty style
    result_fail = {"success": True, "selector": "#style", "text": ""}
    print("\n--- Testing Failed Validation with Fix ---")
    validation_fail = await feedback_loop.validate_step(test_run_id, test_step_index, action_fail, result_fail)
    print(f"Validation Fail Result: {json.dumps(validation_fail, indent=2)}")

    # Get retry actions
    retry_actions = await feedback_loop.get_retry_actions(validation_fail)
    print(f"Retry Actions: {retry_actions}")

    # Simulate action execution failure
    test_step_index = 3
    action_exec_fail = {"action": "click", "target": "nonexistent_button"}
    result_exec_fail = {"success": False, "error": "Element not found: nonexistent_button"}
    print("\n--- Testing Action Execution Failure ---")
    validation_exec_fail = await feedback_loop.validate_step(test_run_id, test_step_index, action_exec_fail, result_exec_fail)
    print(f"Validation Exec Fail Result: {json.dumps(validation_exec_fail, indent=2)}")


    # Clean up test directory
    # import shutil
    # if os.path.exists("./test_suno_screenshots"):
    #     shutil.rmtree("./test_suno_screenshots")
    print("\nCleanup complete (manual step for safety).")

if __name__ == "__main__":
    asyncio.run(main())

