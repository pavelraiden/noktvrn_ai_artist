# modules/suno/suno_feedback_loop.py

import logging
import json
import os
import asyncio
from typing import Dict, Any, Optional, List

# Import the REAL BAS Driver (Assuming it's defined elsewhere, e.g., modules/bas/driver.py)
# from modules.bas.driver import BASDriver # Placeholder for actual import path
# Using MockBASDriver temporarily until real driver path is confirmed
from .suno_ui_translator import MockBASDriver  # KEEPING MOCK FOR NOW

# Import the REAL LLM Validator Client
# Assuming the client is defined in modules/llm_validator/client.py
# Replace with actual path if different
# from modules.llm_validator.client import LLMValidatorClient # Placeholder


# --- Mock LLM Client (Keep for fallback/testing if needed, but prioritize real one) ---
class MockLLMValidatorClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        logger.info(
            f"MockLLMValidatorClient initialized with config: {config}"
        )

    async def validate_ui_state(
        self, screenshot_path: str, expected_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulates calling an LLM to validate UI state based on a screenshot.

        Enforces strict JSON output format.
        """
        logger.info(
            f"[MockLLMClient] Validating screenshot: {screenshot_path}"
        )
        await asyncio.sleep(1.5)  # Simulate LLM processing time

        # --- Mock LLM Response Logic ---
        approved = True
        feedback = "Validation successful (Mock)."
        suggested_fix = None
        action_performed = expected_state.get("action_performed", {})
        action_type = action_performed.get("action")
        target = action_performed.get("target")

        if (
            action_type == "input"
            and target == "style_input"
            and not expected_state.get("expected_text")
        ):
            approved = False
            feedback = "Validation failed (Mock): The style input field appears empty."
            suggested_fix = [
                {
                    "action": "input",
                    "target": "style_input",
                    "value": "acoustic pop",
                }
            ]
        elif action_type == "click" and target == "create_button":
            if hash(screenshot_path) % 3 == 0:
                approved = False
                feedback = "Validation failed (Mock): 'Create' button click did not proceed."
                suggested_fix = [
                    {"action": "click", "target": "create_button"}
                ]
            else:
                feedback = "Create button clicked (Mock)."

        response = {
            "approved": approved,
            "feedback": feedback,
            "suggested_fix": suggested_fix,
        }
        try:
            json.dumps(response)
            return response
        except TypeError as e:
            logger.error(f"[MockLLMClient] Failed to serialize response: {e}")
            return {
                "approved": False,
                "feedback": f"Internal Mock LLM client error: {e}",
                "suggested_fix": None,
            }


# --- End of Mock LLM Client ---


# --- Placeholder for Real LLM Client (Use this once available) ---
class RealLLMValidatorClient:  # Replace with actual import
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("api_key")
        self.model = config.get("model")
        if not self.api_key or self.api_key == "dummy_key":
            logger.warning(
                "LLM Validator API Key is missing or dummy. Using Mock Client."
            )
            self.client = MockLLMValidatorClient(config)  # Fallback to mock
        else:
            logger.info(
                f"Initializing REAL LLM Validator Client with model: {self.model}"
            )
            # Initialize the actual client library here (e.g., OpenAI, Anthropic, Gemini)
            # self.client = ActualLLMClientLibrary(api_key=self.api_key, model=self.model)
            # Using mock temporarily as placeholder for actual library call
            self.client = MockLLMValidatorClient(
                config
            )  # REPLACE THIS with actual client init

    async def validate_ui_state(
        self, screenshot_path: str, expected_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info(
            f"[RealLLMClient] Requesting validation for: {screenshot_path}"
        )
        # --- Actual LLM Call Logic ---
        # 1. Prepare prompt (text + image)
        # 2. Call LLM API (e.g., self.client.generate_content_async(...))
        # 3. Parse response, enforce JSON structure, handle errors
        # --- Placeholder using Mock ---
        return await self.client.validate_ui_state(
            screenshot_path, expected_state
        )


# --- End of Placeholder Real LLM Client ---


logger = logging.getLogger(__name__)


class SunoFeedbackLoopError(Exception):
    """Custom exception for Feedback Loop errors."""

    pass


class SunoFeedbackLoop:
    """Handles validation of UI actions using screenshots and LLM feedback.
    Enforces strict JSON communication protocol with the LLM validator.
    """

    def __init__(
        self,
        bas_driver: Any,
        llm_validator_config: Dict[str, Any],
        screenshot_dir: str = "./suno_validation_screenshots",
    ):
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

        # Initialize the REAL LLM client (which might fallback to mock if key is missing)
        self.llm_validator = RealLLMValidatorClient(llm_validator_config)
        logger.info("Suno Feedback Loop initialized.")

    async def _take_validation_screenshot(
        self, run_id: str, step_index: int
    ) -> Optional[str]:
        """Takes a screenshot for validation."""
        filename = os.path.join(
            self.screenshot_dir,
            f"run_{run_id}_step_{step_index}_validation.png",
        )
        try:
            result = await self.driver.take_screenshot(filename)
            if result.get("success"):
                logger.info(f"Took validation screenshot: {filename}")
                return filename
            else:
                logger.error(
                    f"Failed to take screenshot: {result.get('error')}"
                )
                return None
        except Exception as e:
            logger.error(f"Exception during screenshot: {e}")
            return None

    async def _ask_llm_for_validation(
        self, screenshot_path: str, expected_state: Dict[str, Any]
    ) -> Dict[str, Any]:
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
        logger.info(
            f"Requesting LLM validation for screenshot: {screenshot_path}"
        )
        try:
            # Use the initialized LLM client instance (RealLLMValidatorClient)
            response = await self.llm_validator.validate_ui_state(
                screenshot_path, expected_state
            )

            # --- Strict JSON Protocol Enforcement ---
            if not isinstance(response, dict):
                raise ValueError(
                    f"LLM response is not a dictionary: {type(response)}"
                )
            if "approved" not in response or not isinstance(
                response["approved"], bool
            ):
                raise ValueError(
                    "LLM response missing or invalid 'approved' key (boolean expected)."
                )
            if "feedback" not in response or not isinstance(
                response["feedback"], str
            ):
                raise ValueError(
                    "LLM response missing or invalid 'feedback' key (string expected)."
                )
            if (
                "suggested_fix" in response
                and response["suggested_fix"] is not None
                and not isinstance(response["suggested_fix"], list)
            ):
                raise ValueError(
                    "LLM response 'suggested_fix' key must be a list or None."
                )
            if isinstance(response.get("suggested_fix"), list):
                for fix_action in response["suggested_fix"]:
                    if (
                        not isinstance(fix_action, dict)
                        or "action" not in fix_action
                    ):
                        raise ValueError(
                            "Invalid structure in 'suggested_fix': Each item must be a dict with an 'action' key."
                        )
            # --- End Strict JSON Protocol Enforcement ---

            logger.info(
                f"LLM Validation result: Approved={response.get('approved')}, Feedback=\"{response.get('feedback')}\""
            )
            return response

        except Exception as e:
            logger.error(
                f"LLM validation request failed or response invalid: {e}"
            )
            raise SunoFeedbackLoopError(f"LLM validation failed: {e}") from e
        finally:
            if os.path.exists(screenshot_path):
                try:
                    # os.remove(screenshot_path)
                    logger.debug(f"Kept screenshot (debug): {screenshot_path}")
                except OSError as e:
                    logger.warning(
                        f"Failed to remove screenshot {screenshot_path}: {e}"
                    )

    async def validate_step(
        self,
        run_id: str,
        step_index: int,
        action: Dict[str, Any],
        action_result: Dict[str, Any],
    ) -> Dict[str, Any]:
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
        if not action_result.get("success"):
            error_msg = action_result.get(
                "error", "Unknown action execution error"
            )
            logger.warning(
                f"Action itself failed, skipping LLM validation. Error: {error_msg}"
            )
            return {
                "approved": False,
                "feedback": f"Action execution failed: {error_msg}",
                "suggested_fix": None,
            }

        screenshot_path = await self._take_validation_screenshot(
            run_id, step_index
        )
        if not screenshot_path:
            logger.error("Failed to take screenshot, cannot validate step.")
            return {
                "approved": False,
                "feedback": "Failed to capture screenshot for validation.",
                "suggested_fix": None,
            }

        expected_state = {
            "action_performed": action,
            "action_result": action_result,
        }
        if action.get("action") == "input":
            expected_state["expected_text"] = action.get("value")
            expected_state["target_element"] = action.get("target")
        elif action.get("action") == "click":
            expected_state["expected_outcome"] = (
                f"Element {action.get('target')} should be clicked, potentially leading to a state change."
            )

        try:
            validation_result = await self._ask_llm_for_validation(
                screenshot_path, expected_state
            )
            return validation_result
        except SunoFeedbackLoopError as e:
            return {
                "approved": False,
                "feedback": f"LLM validation process failed: {e}",
                "suggested_fix": None,
            }

    async def get_retry_actions(
        self, validation_result: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """Extracts validated suggested fix actions from the LLM validation result.

        Args:
            validation_result: The result dictionary from the LLM.

        Returns:
            A list of action dictionaries to retry, or None if no valid fix suggested.
        """
        suggested_fix = validation_result.get("suggested_fix")

        if isinstance(suggested_fix, list) and len(suggested_fix) > 0:
            valid_actions = []
            for i, action in enumerate(suggested_fix):
                if isinstance(action, dict) and "action" in action:
                    valid_actions.append(action)
                else:
                    logger.warning(
                        f"Invalid action structure in suggested_fix at index {i}: {action}. Skipping this action."
                    )

            if valid_actions:
                logger.info(
                    f"Using validated suggested fix actions from LLM: {valid_actions}"
                )
                return valid_actions
            else:
                logger.warning(
                    "LLM suggested fixes, but none had valid structure."
                )
                return None
        else:
            logger.info("No suggested fix actions provided or list is empty.")
            return None


# Example usage (for testing purposes)
async def main():
    # Load .env file if it exists
    try:
        from dotenv import load_dotenv

        dotenv_path = os.path.join(
            os.path.dirname(__file__), "..", "..", ".env"
        )  # Assumes .env is in project root
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)
            logger.info("Loaded environment variables from .env file.")
        else:
            logger.warning(
                ".env file not found, relying on system environment variables."
            )
    except ImportError:
        logger.warning("python-dotenv not installed, cannot load .env file.")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    mock_driver = MockBASDriver()  # Use the mock driver for example
    llm_config = {
        "api_key": os.getenv("LLM_VALIDATOR_API_KEY", "dummy_key"),
        "model": os.getenv("LLM_VALIDATOR_MODEL", "validator-model-v1"),
    }
    feedback_loop = SunoFeedbackLoop(
        mock_driver, llm_config, screenshot_dir="./test_suno_screenshots"
    )

    test_run_id = "feedback_test_003"
    test_step_index = 1

    action_ok = {
        "action": "input",
        "target": "lyrics_input",
        "value": "Hello world",
    }
    result_ok = {"success": True, "selector": "#lyrics", "text": "Hello world"}
    print("--- Testing Successful Validation ---")
    validation_ok = await feedback_loop.validate_step(
        test_run_id, test_step_index, action_ok, result_ok
    )
    print(f"Validation OK Result: {json.dumps(validation_ok, indent=2)}")

    test_step_index = 2
    action_fail = {"action": "input", "target": "style_input", "value": ""}
    result_fail = {"success": True, "selector": "#style", "text": ""}
    print("\n--- Testing Failed Validation with Fix ---")
    validation_fail = await feedback_loop.validate_step(
        test_run_id, test_step_index, action_fail, result_fail
    )
    print(f"Validation Fail Result: {json.dumps(validation_fail, indent=2)}")

    retry_actions = await feedback_loop.get_retry_actions(validation_fail)
    print(f"Retry Actions: {retry_actions}")

    test_step_index = 3
    action_exec_fail = {"action": "click", "target": "nonexistent_button"}
    result_exec_fail = {
        "success": False,
        "error": "Element not found: nonexistent_button",
    }
    print("\n--- Testing Action Execution Failure ---")
    validation_exec_fail = await feedback_loop.validate_step(
        test_run_id, test_step_index, action_exec_fail, result_exec_fail
    )
    print(
        f"Validation Exec Fail Result: {json.dumps(validation_exec_fail, indent=2)}"
    )

    print("\nCleanup complete (manual step for safety).")


if __name__ == "__main__":
    asyncio.run(main())
