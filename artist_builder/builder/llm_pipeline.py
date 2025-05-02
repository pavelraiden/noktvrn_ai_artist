"""
LLM Pipeline Module for Artist Profile Builder

This module integrates with the LLM orchestrator to generate complete
artist profiles from initial inputs, including routing and fallback logic.
"""

import logging
import json
import os
import sys
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import asyncio

# Add project root to sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# Import necessary components
from utils.retry_decorator import retry_on_exception

# Assuming a placeholder orchestrator exists or will be created
# Adjust the import path based on the actual location of the orchestrator
try:
    from llm_orchestrator.orchestrator import LLMOrchestrator, LLMOrchestratorError
except ImportError:
    # Fallback if the orchestrator module doesn't exist yet
    logging.warning("LLMOrchestrator not found, using basic placeholder.")

    class LLMOrchestratorError(Exception):
        pass

    class LLMOrchestrator:
        def __init__(
            self, primary_model="mock_primary", fallback_model="mock_fallback"
        ):
            self.primary_model = primary_model
            self.fallback_model = fallback_model
            logging.info(
                f"Initialized Mock LLMOrchestrator (primary: {primary_model}, fallback: {fallback_model})"
            )

        async def generate_profile(
            self, input_data: Dict[str, Any], model: str
        ) -> Dict[str, Any]:
            logging.info(f"Mock LLMOrchestrator received request for model: {model}")
            # Simulate success or failure based on model name for testing
            if "fail" in model:
                logging.warning(f"Simulating failure for model: {model}")
                raise LLMOrchestratorError(f"Simulated failure for model {model}")

            # Simulate a successful generation
            import uuid
            from datetime import datetime

            profile = input_data.copy()
            profile["artist_id"] = profile.get("artist_id", str(uuid.uuid4()))
            stage_name = profile.get(
                "stage_name", "Generated Artist"
            )  # Use .get for safety
            social_media_handle = stage_name.lower().replace(" ", "_")
            profile_dict = {
                "stage_name": stage_name,
                "genre": profile.get("genre", "Electronic"),
                "creation_timestamp": datetime.now().isoformat(),
                "creation_method": f"llm_pipeline (model: {model})",
                "biography": f"Generated biography via {model} for {stage_name}.",
                "influences": ["Mock Influence 1", "Mock Influence 2"],
                "social_media": {"twitter": f"@{social_media_handle}"},
                "discography": [],
                "upcoming_releases": [],
                "visual_identity": {
                    "color_palette": ["#ABCDEF"],
                    "style_keywords": ["mock"],
                },
                "metadata": {
                    "version": "1.1",
                    "generated_by": f"mock_llm_orchestrator ({model})",
                },
            }
            profile.update(profile_dict)
            logging.info(
                f"Mock LLMOrchestrator successfully generated profile using model: {model}"
            )
            return profile


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_builder.llm_pipeline")


class LLMPipelineError(Exception):
    """Exception raised for errors in the LLM pipeline."""

    pass


# Define exceptions to retry on for LLM calls
LLM_RETRY_EXCEPTIONS = (
    LLMOrchestratorError,
    ConnectionError,
    TimeoutError,
    asyncio.TimeoutError,
)


class ArtistProfileLLMPipeline:
    """
    Integrates with LLM orchestrator to generate complete artist profiles,
    including routing to primary/fallback models and retries.
    """

    def __init__(
        self, primary_model: str = "gpt-4-turbo", fallback_model: str = "gpt-3.5-turbo"
    ):
        """Initialize the LLM pipeline with primary and fallback model preferences."""
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        # Instantiate the orchestrator (real or mock)
        self.orchestrator = LLMOrchestrator(
            primary_model=self.primary_model, fallback_model=self.fallback_model
        )
        logger.info(
            f"Initialized ArtistProfileLLMPipeline (Primary: {self.primary_model}, Fallback: {self.fallback_model})"
        )

    # Apply retry logic to the core generation attempt
    @retry_on_exception(retries=2, delay=5, backoff=2, exceptions=LLM_RETRY_EXCEPTIONS)
    async def _attempt_generation(
        self, input_data: Dict[str, Any], model: str
    ) -> Dict[str, Any]:
        """Internal method to attempt profile generation with a specific model, with retries."""
        logger.info(f"Attempting profile generation using model: {model}")
        try:
            # Use asyncio.wait_for for timeout if the orchestrator call is async
            # Adjust timeout value as needed
            profile = await asyncio.wait_for(
                self.orchestrator.generate_profile(input_data, model), timeout=120.0
            )
            logger.info(f"Successfully generated profile using model: {model}")
            return profile
        except asyncio.TimeoutError:
            logger.error(f"LLM generation timed out for model: {model}")
            raise LLMOrchestratorError(f"LLM generation timed out for model: {model}")
        except LLMOrchestratorError as e:
            logger.error(f"LLM Orchestrator error using model {model}: {e}")
            raise  # Re-raise to be caught by retry decorator or fallback logic
        except Exception as e:
            logger.error(
                f"Unexpected error during generation with model {model}: {e}",
                exc_info=True,
            )
            # Wrap unexpected errors
            raise LLMPipelineError(f"Unexpected error with model {model}: {e}") from e

    async def generate_complete_profile(
        self, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a complete artist profile from initial inputs, using primary model
        with fallback to a secondary model on failure.

        Args:
            input_data: Dictionary containing the initial user inputs

        Returns:
            Dictionary containing the complete artist profile

        Raises:
            LLMPipelineError: If generation fails with both primary and fallback models after retries.
        """
        logger.info(
            f"Starting profile generation for input: {json.dumps(input_data)[:100]}..."
        )

        # --- Try Primary Model --- #
        try:
            logger.info(
                f"Attempting generation with primary model: {self.primary_model}"
            )
            # Use await here as _attempt_generation is now async
            generated_profile = await self._attempt_generation(
                input_data, self.primary_model
            )
            logger.info("Successfully generated profile using primary model.")
            return generated_profile
        except Exception as primary_error:
            logger.warning(
                f"Primary model ({self.primary_model}) failed after retries: {primary_error}. Attempting fallback..."
            )

            # --- Try Fallback Model --- #
            try:
                logger.info(
                    f"Attempting generation with fallback model: {self.fallback_model}"
                )
                # Use await here as _attempt_generation is now async
                generated_profile = await self._attempt_generation(
                    input_data, self.fallback_model
                )
                logger.info("Successfully generated profile using fallback model.")
                # Add metadata indicating fallback was used
                if "metadata" not in generated_profile:
                    generated_profile["metadata"] = {}
                generated_profile["metadata"]["fallback_used"] = True
                generated_profile["metadata"]["primary_model_error"] = str(
                    primary_error
                )
                return generated_profile
            except Exception as fallback_error:
                logger.error(
                    f"Fallback model ({self.fallback_model}) also failed after retries: {fallback_error}"
                )
                # Raise the final error if both primary and fallback fail
                raise LLMPipelineError(
                    f"LLM generation failed with both primary ({self.primary_model}: {primary_error}) "
                    f"and fallback ({self.fallback_model}: {fallback_error}) models after retries."
                ) from fallback_error


# Example Usage (for testing purposes)
async def main():
    logging.basicConfig(level=logging.DEBUG)  # Use DEBUG for more detail during testing
    logger.info("--- Testing LLM Pipeline --- ")

    pipeline = ArtistProfileLLMPipeline(
        primary_model="mock_primary", fallback_model="mock_fallback"
    )
    # Test case 1: Primary model succeeds
    test_input_1 = {"genre": "Synthwave", "mood": "Nostalgic"}
    print("\n--- Test Case 1: Primary Success ---")
    try:
        profile_1 = await pipeline.generate_complete_profile(test_input_1)
        print("Generated Profile (Primary Success):")
        print(json.dumps(profile_1, indent=2))
    except LLMPipelineError as e:
        print(f"Error in Test Case 1: {e}")

    # Test case 2: Primary fails, Fallback succeeds
    pipeline_fail_primary = ArtistProfileLLMPipeline(
        primary_model="mock_primary_fail", fallback_model="mock_fallback_ok"
    )
    test_input_2 = {"genre": "Ambient", "theme": "Space"}
    print("\n--- Test Case 2: Primary Fail, Fallback Success ---")
    try:
        profile_2 = await pipeline_fail_primary.generate_complete_profile(test_input_2)
        print("Generated Profile (Fallback Success):")
        print(json.dumps(profile_2, indent=2))
        assert profile_2.get("metadata", {}).get("fallback_used") is True
    except LLMPipelineError as e:
        print(f"Error in Test Case 2: {e}")

    # Test case 3: Both Primary and Fallback fail
    pipeline_fail_all = ArtistProfileLLMPipeline(
        primary_model="mock_primary_fail", fallback_model="mock_fallback_fail"
    )
    test_input_3 = {"genre": "Lo-fi", "vibe": "Rainy day"}
    print("\n--- Test Case 3: Both Fail ---")
    try:
        profile_3 = await pipeline_fail_all.generate_complete_profile(test_input_3)
        print("Generated Profile (Both Fail - Should not print):")
        print(json.dumps(profile_3, indent=2))
    except LLMPipelineError as e:
        print(f"Successfully caught expected error in Test Case 3: {e}")
    except Exception as e:
        print(f"Caught unexpected error in Test Case 3: {e}")


if __name__ == "__main__":
    asyncio.run(main())
