# modules/llm_validator_interface.py

import abc
from typing import Dict, Any


class LLMValidatorInterface(abc.ABC):
    """Abstract Base Class defining the interface for an LLM-based UI validation agent.

    This interface standardizes how the feedback loop interacts with an LLM
    to validate UI states based on screenshots and expected outcomes.
    """

    @abc.abstractmethod
    async def validate_step(
        self,
        screenshot_path: str,
        expected_state: Dict[str, Any],
        previous_action: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validate the current UI state based on a screenshot and expectations.

        Args:
            screenshot_path: Absolute path to the screenshot image file.
            expected_state: A dictionary describing the expected UI state after the action.
                            (e.g., {"element_visible": "#song-title", "text_contains": "Generated Song"})
            previous_action: The action dictionary that led to this state.

        Returns:
            A dictionary containing the validation result and suggested fix actions if validation failed.
            The structure must adhere to the strict JSON protocol defined in the master prompt.
            Example (Success):
            {
                "validation_status": "approved",
                "reasoning": "UI matches expected state after clicking create button.",
                "suggested_fix_actions": []
            }
            Example (Failure):
            {
                "validation_status": "rejected",
                "reasoning": "Expected element #song-title not visible in screenshot.",
                "suggested_fix_actions": [
                    {"action": "wait", "duration": 5},
                    {"action": "screenshot", "filename": "retry_screenshot.png"}
                ]
            }
        """
        pass
