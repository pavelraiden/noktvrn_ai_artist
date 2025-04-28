"""
Orchestrator Module

This module provides the core orchestration functionality for LLM interactions,
managing the flow of prompts, reviews, and refinements between different LLMs.
"""

import asyncio
import uuid
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from datetime import datetime
from enum import Enum

from .llm_interface import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    LLMRequestType,
    LLMProviderFactory,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("orchestrator")


class OrchestrationStatus(Enum):
    """Status of an orchestration process."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class OrchestrationResult:
    """
    Result of an orchestration process.

    Attributes:
        id: Unique identifier for the orchestration
        status: Current status of the orchestration
        content: The final content (if completed)
        iterations: Number of iterations performed
        confidence_score: Final confidence score (if completed)
        history: History of interactions
        error: Error message (if failed)
        created_at: When the orchestration was created
        completed_at: When the orchestration was completed
    """

    def __init__(self, orchestration_id: str):
        """
        Initialize a new orchestration result.

        Args:
            orchestration_id: Unique identifier for the orchestration
        """
        self.id = orchestration_id
        self.status = OrchestrationStatus.PENDING
        self.content: Optional[str] = None
        self.iterations = 0
        self.confidence_score: Optional[float] = None
        self.history: List[Dict[str, Any]] = []
        self.error: Optional[str] = None
        self.created_at = datetime.now().isoformat()
        self.completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary."""
        return {
            "id": self.id,
            "status": self.status.value,
            "content": self.content,
            "iterations": self.iterations,
            "confidence_score": self.confidence_score,
            "history": self.history,
            "error": self.error,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrchestrationResult":
        """Create a result from a dictionary."""
        result = cls(data["id"])
        result.status = OrchestrationStatus(data["status"])
        result.content = data.get("content")
        result.iterations = data.get("iterations", 0)
        result.confidence_score = data.get("confidence_score")
        result.history = data.get("history", [])
        result.error = data.get("error")
        result.created_at = data.get("created_at", datetime.now().isoformat())
        result.completed_at = data.get("completed_at")
        return result

    def add_to_history(self, interaction_type: str, data: Dict[str, Any]) -> None:
        """
        Add an interaction to the history.

        Args:
            interaction_type: Type of interaction (e.g., "generate", "review", "refine")
            data: Data associated with the interaction
        """
        self.history.append(
            {
                "type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "data": data,
            }
        )

    def complete(self, content: str, confidence_score: float) -> None:
        """
        Mark the orchestration as completed.

        Args:
            content: The final content
            confidence_score: The final confidence score
        """
        self.status = OrchestrationStatus.COMPLETED
        self.content = content
        self.confidence_score = confidence_score
        self.completed_at = datetime.now().isoformat()

    def fail(self, error: str) -> None:
        """
        Mark the orchestration as failed.

        Args:
            error: The error message
        """
        self.status = OrchestrationStatus.FAILED
        self.error = error
        self.completed_at = datetime.now().isoformat()

    def timeout(self) -> None:
        """Mark the orchestration as timed out."""
        self.status = OrchestrationStatus.TIMEOUT
        self.error = "Orchestration timed out"
        self.completed_at = datetime.now().isoformat()


class Orchestrator:
    """
    Orchestrates interactions between LLMs for content generation, review, and refinement.

    This class manages the flow of prompts, reviews, and refinements between different LLMs,
    tracking the state of the orchestration and making decisions based on confidence scores.
    """

    def __init__(
        self,
        generator_provider: LLMProvider,
        reviewer_provider: LLMProvider,
        refiner_provider: Optional[LLMProvider] = None,
        confidence_threshold: float = 0.7,
        max_iterations: int = 5,
        session_id: Optional[str] = None,
    ):
        """
        Initialize a new orchestrator.

        Args:
            generator_provider: LLM provider for content generation
            reviewer_provider: LLM provider for content review
            refiner_provider: LLM provider for content refinement (defaults to generator if None)
            confidence_threshold: Minimum confidence score to consider content acceptable
            max_iterations: Maximum number of refinement iterations
            session_id: Unique identifier for the session (generated if None)
        """
        self.generator_provider = generator_provider
        self.reviewer_provider = reviewer_provider
        self.refiner_provider = refiner_provider or generator_provider
        self.confidence_threshold = confidence_threshold
        self.max_iterations = max_iterations
        self.session_id = session_id or str(uuid.uuid4())

        logger.info(f"Initialized orchestrator with session ID: {self.session_id}")

    async def orchestrate_prompt(
        self,
        initial_prompt: str,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> OrchestrationResult:
        """
        Orchestrate the generation, review, and refinement of a prompt.

        Args:
            initial_prompt: The initial prompt to generate content from
            parameters: Additional parameters for the LLM requests
            context: Additional context for the orchestration

        Returns:
            The result of the orchestration
        """
        # Initialize parameters and context
        parameters = parameters or {}
        context = context or {}

        # Add session ID to parameters
        parameters["session_id"] = self.session_id

        # Create a new orchestration result
        orchestration_id = str(uuid.uuid4())
        result = OrchestrationResult(orchestration_id)

        # Update status to in progress
        result.status = OrchestrationStatus.IN_PROGRESS

        try:
            # Generate initial content
            logger.info(
                f"Generating initial content for orchestration {orchestration_id}"
            )
            content = await self._generate_content(initial_prompt, parameters, result)

            # Review and refine loop
            iteration = 0
            confidence_score = 0.0

            while iteration < self.max_iterations:
                # Increment iteration counter
                iteration += 1
                result.iterations = iteration

                # Review the content
                logger.info(
                    f"Reviewing content (iteration {iteration}) for orchestration {orchestration_id}"
                )
                review_response, confidence_score = await self._review_content(
                    content, parameters, result
                )

                # Check if content meets confidence threshold
                if confidence_score >= self.confidence_threshold:
                    logger.info(
                        f"Content meets confidence threshold ({confidence_score:.2f} >= {self.confidence_threshold:.2f})"
                    )
                    break

                # Refine the content based on review
                logger.info(
                    f"Refining content (iteration {iteration}) for orchestration {orchestration_id}"
                )
                content = await self._refine_content(
                    content, review_response, parameters, result
                )

            # Complete the orchestration
            result.complete(content, confidence_score)
            logger.info(
                f"Orchestration {orchestration_id} completed with confidence score {confidence_score:.2f}"
            )

            return result

        except Exception as e:
            # Handle any exceptions
            error_message = f"Orchestration failed: {str(e)}"
            logger.error(error_message)
            result.fail(error_message)
            return result

    async def _generate_content(
        self, prompt: str, parameters: Dict[str, Any], result: OrchestrationResult
    ) -> str:
        """
        Generate content using the generator provider.

        Args:
            prompt: The prompt to generate content from
            parameters: Additional parameters for the LLM request
            result: The orchestration result to update

        Returns:
            The generated content
        """
        # Create a generate request
        request = LLMRequest(
            request_type=LLMRequestType.GENERATE, prompt=prompt, parameters=parameters
        )

        # Send the request to the generator provider
        response = await self.generator_provider.send_request(request)

        # Add to history
        result.add_to_history(
            "generate", {"request": request.to_dict(), "response": response.to_dict()}
        )

        return response.content

    async def _review_content(
        self, content: str, parameters: Dict[str, Any], result: OrchestrationResult
    ) -> Tuple[str, float]:
        """
        Review content using the reviewer provider.

        Args:
            content: The content to review
            parameters: Additional parameters for the LLM request
            result: The orchestration result to update

        Returns:
            A tuple of (review response, confidence score)
        """
        # Create a review prompt
        review_prompt = f"""
        Please review the following content and provide feedback:
        
        {content}
        
        Provide a detailed assessment of the quality, coherence, and effectiveness.
        Suggest specific improvements if needed.
        """

        # Create a review request
        request = LLMRequest(
            request_type=LLMRequestType.REVIEW,
            prompt=review_prompt,
            parameters=parameters,
        )

        # Send the request to the reviewer provider
        response = await self.reviewer_provider.send_request(request)

        # Extract confidence score from metadata
        confidence_score = response.metadata.get("confidence_score", 0.5)

        # Add to history
        result.add_to_history(
            "review",
            {
                "request": request.to_dict(),
                "response": response.to_dict(),
                "confidence_score": confidence_score,
            },
        )

        return response.content, confidence_score

    async def _refine_content(
        self,
        content: str,
        review: str,
        parameters: Dict[str, Any],
        result: OrchestrationResult,
    ) -> str:
        """
        Refine content using the refiner provider.

        Args:
            content: The content to refine
            review: The review feedback
            parameters: Additional parameters for the LLM request
            result: The orchestration result to update

        Returns:
            The refined content
        """
        # Create a refine prompt
        refine_prompt = f"""
        Please refine the following content based on the review feedback:
        
        ORIGINAL CONTENT:
        {content}
        
        REVIEW FEEDBACK:
        {review}
        
        Please provide an improved version that addresses the feedback.
        """

        # Create a refine request
        request = LLMRequest(
            request_type=LLMRequestType.REFINE,
            prompt=refine_prompt,
            parameters=parameters,
        )

        # Send the request to the refiner provider
        response = await self.refiner_provider.send_request(request)

        # Add to history
        result.add_to_history(
            "refine", {"request": request.to_dict(), "response": response.to_dict()}
        )

        return response.content


class OrchestratorFactory:
    """
    Factory for creating orchestrator instances.

    This factory creates orchestrator instances with different configurations.
    """

    @staticmethod
    def create_default_orchestrator(
        session_id: Optional[str] = None,
        confidence_threshold: float = 0.7,
        max_iterations: int = 5,
    ) -> Orchestrator:
        """
        Create a default orchestrator with mock providers.

        Args:
            session_id: Unique identifier for the session (generated if None)
            confidence_threshold: Minimum confidence score to consider content acceptable
            max_iterations: Maximum number of refinement iterations

        Returns:
            A configured orchestrator instance
        """
        # Create mock providers
        generator_provider = LLMProviderFactory.create_provider(
            "smart_mock",
            {"provider_name": "MockGenerator", "model_name": "mock-generator-v1"},
        )

        reviewer_provider = LLMProviderFactory.create_provider(
            "smart_mock",
            {"provider_name": "MockReviewer", "model_name": "mock-reviewer-v1"},
        )

        refiner_provider = LLMProviderFactory.create_provider(
            "smart_mock",
            {"provider_name": "MockRefiner", "model_name": "mock-refiner-v1"},
        )

        # Create and return the orchestrator
        return Orchestrator(
            generator_provider=generator_provider,
            reviewer_provider=reviewer_provider,
            refiner_provider=refiner_provider,
            confidence_threshold=confidence_threshold,
            max_iterations=max_iterations,
            session_id=session_id,
        )

    @staticmethod
    def create_orchestrator_from_config(
        config: Dict[str, Any], session_id: Optional[str] = None
    ) -> Orchestrator:
        """
        Create an orchestrator from a configuration dictionary.

        Args:
            config: Configuration dictionary
            session_id: Unique identifier for the session (generated if None)

        Returns:
            A configured orchestrator instance
        """
        # Extract configuration values
        generator_config = config.get("generator", {})
        reviewer_config = config.get("reviewer", {})
        refiner_config = config.get("refiner", {})

        # Create providers
        generator_provider = LLMProviderFactory.create_provider(
            generator_config.get("provider_type", "smart_mock"),
            generator_config.get("provider_config", {}),
        )

        reviewer_provider = LLMProviderFactory.create_provider(
            reviewer_config.get("provider_type", "smart_mock"),
            reviewer_config.get("provider_config", {}),
        )

        refiner_provider = LLMProviderFactory.create_provider(
            refiner_config.get("provider_type", "smart_mock"),
            refiner_config.get("provider_config", {}),
        )

        # Create and return the orchestrator
        return Orchestrator(
            generator_provider=generator_provider,
            reviewer_provider=reviewer_provider,
            refiner_provider=refiner_provider,
            confidence_threshold=config.get("confidence_threshold", 0.7),
            max_iterations=config.get("max_iterations", 5),
            session_id=session_id,
        )


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_orchestrator():
        # Create a default orchestrator
        orchestrator = OrchestratorFactory.create_default_orchestrator()

        # Define a prompt
        prompt = "Create a dark trap artist with mysterious vibes and urban lifestyle"

        # Orchestrate the prompt
        result = await orchestrator.orchestrate_prompt(prompt)

        # Print the result
        print(f"Orchestration result: {json.dumps(result.to_dict(), indent=2)}")

    # Run the test
    asyncio.run(test_orchestrator())
