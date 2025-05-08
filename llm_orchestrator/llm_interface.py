"""
LLM Interface Module

This module provides abstract interfaces and mock implementations for LLM
    interactions.
It defines standardized request/response formats and provider-agnostic interfaces.
"""

import abc
import uuid
import time
import random
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime


class LLMRequestType(Enum):
    """Types of LLM requests."""

    GENERATE = "generate"  # Generate new content
    REVIEW = "review"  # Review existing content
    REFINE = "refine"  # Refine content based on feedback


class LLMRequest:
    """
    Represents a request to an LLM.

    Attributes:
        id: Unique identifier for the request
        type: Type of request (generate, review, refine)
        prompt: The prompt sent to the LLM
        parameters: Configuration parameters for the request
        timestamp: When the request was sent
    """

    def __init__(
        self,
        request_type: LLMRequestType,
        prompt: str,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new LLM request.

        Args:
            request_type: Type of request (generate, review, refine)
            prompt: The prompt sent to the LLM
            parameters: Configuration parameters for the request
        """
        self.id = str(uuid.uuid4())
        self.type = request_type
        self.prompt = prompt
        self.parameters = parameters or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the request to a dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "prompt": self.prompt,
            "parameters": self.parameters,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMRequest":
        """Create a request from a dictionary."""
        request = cls(
            request_type=LLMRequestType(data["type"]),
            prompt=data["prompt"],
            parameters=data.get("parameters", {}),
        )
        request.id = data["id"]
        request.timestamp = data["timestamp"]
        return request


class LLMResponse:
    """
    Represents a response from an LLM.

    Attributes:
        request_id: Reference to the request
        content: The response content
        metadata: Additional information from the LLM
        latency: Response time in seconds
        timestamp: When the response was received
    """

    def __init__(
        self,
        request_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        latency: Optional[float] = None,
    ):
        """
        Initialize a new LLM response.

        Args:
            request_id: Reference to the request
            content: The response content
            metadata: Additional information from the LLM
            latency: Response time in seconds
        """
        self.request_id = request_id
        self.content = content
        self.metadata = metadata or {}
        self.latency = latency or 0.0
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the response to a dictionary."""
        return {
            "request_id": self.request_id,
            "content": self.content,
            "metadata": self.metadata,
            "latency": self.latency,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMResponse":
        """Create a response from a dictionary."""
        response = cls(
            request_id=data["request_id"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            latency=data.get("latency", 0.0),
        )
        response.timestamp = data["timestamp"]
        return response


class LLMProvider(abc.ABC):
    """
    Abstract base class for LLM providers.

    This class defines the interface that all LLM providers must implement.
    """

    @abc.abstractmethod
    async def send_request(self, request: LLMRequest) -> LLMResponse:
        """
        Send a request to the LLM and get a response.

        Args:
            request: The request to send

        Returns:
            The response from the LLM
        """
        pass

    @abc.abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the LLM provider.

        Returns:
            The provider name
        """
        pass

    @abc.abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the LLM model.

        Returns:
            The model name
        """
        pass


class MockLLMProvider(LLMProvider):
    """
    Mock implementation of an LLM provider for testing.

    This provider simulates LLM responses with configurable behavior.
    """

    def __init__(
        self,
        provider_name: str = "MockProvider",
        model_name: str = "mock-model-v1",
        latency_range: tuple = (0.5, 2.0),
        error_rate: float = 0.0,
    ):
        """
        Initialize a new mock LLM provider.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            latency_range: Range of simulated latency in seconds (min, max)
            error_rate: Probability of simulating an error (0.0 to 1.0)
        """
        self.provider_name = provider_name
        self.model_name = model_name
        self.latency_range = latency_range
        self.error_rate = error_rate

        # Templates for different request types
        self.templates = {
            LLMRequestType.GENERATE: [
                "Here is a generated response based on your prompt: "
                " {prompt_summary}",
                "I've created the following content: {prompt_summary}",
                "Based on your requirements, I've generated: {prompt_summary}",
            ],
            LLMRequestType.REVIEW: [
                "I've reviewed the content and found it to be {quality}. "
                "{feedback}",
                "Upon review, the content is {quality}. {feedback}",
                "My assessment of the content: {quality}. " "{feedback}",
            ],
            LLMRequestType.REFINE: [
                "I've refined the content to address the feedback: "
                "{prompt_summary}",
                "Here's an improved version that addresses the issues:                     {prompt_summary}",
                "I've made the following improvements: {prompt_summary}",
            ],
        }

        # Quality assessments for reviews
        self.quality_assessments = [
            "excellent",
            "good",
            "satisfactory",
            "needs improvement",
            "poor",
        ]

        # Feedback templates for reviews
        self.feedback_templates = {
            "excellent": [
                "The content is well-structured and engaging.",
                "No improvements needed, this is ready to use.",
                "This exceeds expectations in clarity and creativity.",
            ],
            "good": [
                "The content is solid with minor room for improvement.",
                "Consider adding more specific details, but otherwise good.",
                "Well done, with just a few tweaks this would be excellent.",
            ],
            "satisfactory": [
                "The content meets basic requirements but could be enhanced.",
                "Consider revising for more impact and engagement.",
                "This works but lacks some creativity and uniqueness.",
            ],
            "needs improvement": [
                "The content has potential but needs significant " "revision.",
                "Consider restructuring and adding more depth.",
                "The main ideas are there but execution needs work.",
            ],
            "poor": [
                "The content doesn't meet the requirements and needs a complete                     rewrite.",
                "Major issues with clarity, structure, and relevance.",
                "This misses the mark on the core objectives.",
            ],
        }

    async def send_request(self, request: LLMRequest) -> LLMResponse:
        """
        Send a request to the mock LLM and get a simulated response.

        Args:
            request: The request to send

        Returns:
            A simulated response
        """
        # Simulate processing time
        latency = random.uniform(self.latency_range[0], self.latency_range[1])
        time.sleep(latency)

        # Simulate random errors
        if random.random() < self.error_rate:
            raise Exception("Simulated LLM provider error")

        # Generate response based on request type
        content = self._generate_mock_response(request)

        # Create metadata
        metadata = {
            "provider": self.provider_name,
            "model": self.model_name,
            "token_count": len(content) // 4,  # Rough approximation
            "finish_reason": "stop",
        }

        # For review requests, add confidence score
        if request.type == LLMRequestType.REVIEW:
            quality = self._extract_quality_from_content(content)
            confidence_score = self._quality_to_confidence_score(quality)
            metadata["confidence_score"] = confidence_score

        return LLMResponse(
            request_id=request.id,
            content=content,
            metadata=metadata,
            latency=latency,
        )

    def get_provider_name(self) -> str:
        """Get the name of the mock LLM provider."""
        return self.provider_name

    def get_model_name(self) -> str:
        """Get the name of the mock LLM model."""
        return self.model_name

    def _generate_mock_response(self, request: LLMRequest) -> str:
        """
        Generate a mock response based on the request type.

        Args:
            request: The request to respond to

        Returns:
            A simulated response string
        """
        # Get templates for this request type
        templates = self.templates.get(
            request.type, self.templates[LLMRequestType.GENERATE]
        )

        # Select a random template
        template = random.choice(templates)

        if request.type == LLMRequestType.REVIEW:
            # For reviews, generate a quality assessment and feedback
            quality = random.choice(self.quality_assessments)
            feedback = random.choice(self.feedback_templates[quality])
            return template.format(quality=quality, feedback=feedback)
        else:
            # For other types, summarize the prompt
            prompt_summary = self._summarize_prompt(request.prompt)
            return template.format(prompt_summary=prompt_summary)

    def _summarize_prompt(self, prompt: str) -> str:
        """
        Create a summary of the prompt for mock responses.

        Args:
            prompt: The prompt to summarize

        Returns:
            A summary of the prompt
        """
        # Simple summarization: take first 50 chars and last 50 chars
        if len(prompt) <= 100:
            return prompt

        return prompt[:50] + "..." + prompt[-50:]

    def _extract_quality_from_content(self, content: str) -> str:
        """
        Extract the quality assessment from review content.

        Args:
            content: The review content

        Returns:
            The quality assessment string
        """
        for quality in self.quality_assessments:
            if quality in content.lower():
                return quality

        # Default if no quality found
        return "satisfactory"

    def _quality_to_confidence_score(self, quality: str) -> float:
        """
        Convert a quality assessment to a confidence score.

        Args:
            quality: The quality assessment string

        Returns:
            A confidence score between 0.0 and 1.0
        """
        quality_scores = {
            "excellent": 0.9,
            "good": 0.75,
            "satisfactory": 0.6,
            "needs improvement": 0.4,
            "poor": 0.2,
        }

        # Add some randomness to the score
        base_score = quality_scores.get(quality, 0.5)
        variation = random.uniform(-0.1, 0.1)

        # Ensure score is between 0.0 and 1.0
        return max(0.0, min(1.0, base_score + variation))


class SmartMockLLMProvider(MockLLMProvider):
    """
    Enhanced mock LLM provider that can improve content over iterations.

    This provider simulates the behavior of a real LLM that learns
    from feedback.
    """

    def __init__(
        self,
        provider_name: str = "SmartMockProvider",
        model_name: str = "smart-mock-model-v1",
        latency_range: tuple = (1.0, 3.0),
        error_rate: float = 0.0,
        improvement_rate: float = 0.2,
    ):
        """
        Initialize a new smart mock LLM provider.

        Args:
            provider_name: Name of the provider
            model_name: Name of the model
            latency_range: Range of simulated latency in seconds (min, max)
            error_rate: Probability of simulating an error (0.0 to 1.0)
            improvement_rate: How much to improve content on each iteration
                (0.0 to 1.0)
        """
        super().__init__(provider_name, model_name, latency_range, error_rate)
        self.improvement_rate = improvement_rate
        self.iteration_memory = {}  # Track iterations for each session

    async def send_request(self, request: LLMRequest) -> LLMResponse:
        """
        Send a request to the smart mock LLM and get a simulated response.

        This implementation tracks sessions and improves responses over
            iterations.

        Args:
            request: The request to send

        Returns:
            A simulated response that improves with iterations
        """
        # Extract session ID from parameters if available
        session_id = request.parameters.get("session_id", "default_session")

        # Increment iteration count for this session
        if session_id not in self.iteration_memory:
            self.iteration_memory[session_id] = {
                "iteration": 0,
                "last_quality": None,
            }

        self.iteration_memory[session_id]["iteration"] += 1
        iteration = self.iteration_memory[session_id]["iteration"]

        # Simulate processing time
        latency = random.uniform(self.latency_range[0], self.latency_range[1])
        time.sleep(latency)

        # Simulate random errors
        if random.random() < self.error_rate:
            raise Exception("Simulated LLM provider error")

        # Generate response based on request type and iteration
        content = self._generate_smart_response(
            request, session_id, iteration
        )  # Create metadata
        metadata = {
            "provider": self.provider_name,
            "model": self.model_name,
            "token_count": len(content) // 4,  # Rough approximation
            "finish_reason": "stop",
            "iteration": iteration,
        }

        # For review requests, add confidence score that improves with iterations
        if request.type == LLMRequestType.REVIEW:
            quality = self._extract_quality_from_content(content)
            if session_id in self.iteration_memory:  # Ensure session exists
                self.iteration_memory[session_id]["last_quality"] = quality
            confidence_score = self._quality_to_confidence_score(
                quality, iteration
            )
            metadata["confidence_score"] = confidence_score

        return LLMResponse(
            request_id=request.id,
            content=content,
            metadata=metadata,
            latency=latency,
        )

    def _generate_smart_response(
        self, request: LLMRequest, session_id: str, iteration: int
    ) -> str:
        """
        Generate a smart mock response that improves with iterations.

        Args:
            request: The request to respond to
            session_id: The session identifier
            iteration: The iteration number for this session

        Returns:
            A simulated response string that improves with iterations
        """
        # Get templates for this request type
        templates = self.templates.get(
            request.type, self.templates[LLMRequestType.GENERATE]
        )

        # Select a random template
        template = random.choice(templates)

        if request.type == LLMRequestType.REVIEW:
            # For reviews, quality improves with iterations
            quality_index = min(
                len(self.quality_assessments) - 1,
                max(
                    0,
                    len(self.quality_assessments)
                    - 1
                    - int(iteration * self.improvement_rate * 2),
                ),
            )
            quality = self.quality_assessments[quality_index]

            # Add more positive feedback with higher iterations
            feedback = random.choice(self.feedback_templates[quality])

            if iteration > 2:
                feedback += (
                    " The improvements from previous versions are noticeable."
                )

            return template.format(quality=quality, feedback=feedback)

        elif request.type == LLMRequestType.REFINE:
            # For refinements, mention specific improvements
            prompt_summary = self._summarize_prompt(request.prompt)

            improvements = [
                "I've enhanced the clarity and flow.",
                "The language is now more engaging and precise.",
                "I've added more specific details as suggested.",
                "The structure has been improved for better readability.",
                "I've addressed the feedback about tone and style.",
            ]

            # Add more improvements with higher iterations
            num_improvements = min(iteration, len(improvements))
            selected_improvements = random.sample(
                improvements, num_improvements
            )

            base_text = template.format(prompt_summary=prompt_summary)
            improvements_text = " ".join(selected_improvements)
            return f"{base_text}\n                {improvements_text}"
        else:
            # For other types, summarize the prompt
            prompt_summary = self._summarize_prompt(request.prompt)
            return template.format(prompt_summary=prompt_summary)

    def _quality_to_confidence_score(
        self, quality: str, iteration: int
    ) -> float:
        """
        Convert quality assessment to confidence score, considering iteration.

        Args:
            quality: The quality assessment string
            iteration: The iteration number

        Returns:
            A confidence score between 0.0 and 1.0 that improves with                 iterations
        """
        quality_scores = {
            "excellent": 0.9,
            "good": 0.75,
            "satisfactory": 0.6,
            "needs improvement": 0.4,
            "poor": 0.2,
        }

        # Base score from quality
        base_score = quality_scores.get(quality, 0.5)

        # Improve score with iterations, but with diminishing returns
        iteration_bonus = min(0.3, self.improvement_rate * iteration)

        # Add some randomness
        variation = random.uniform(-0.05, 0.05)

        # Ensure score is between 0.0 and 1.0
        return max(0.0, min(1.0, base_score + iteration_bonus + variation))


class LLMProviderFactory:
    """
    Factory for creating LLM providers.

    This factory creates provider instances based on configuration.
    """

    @staticmethod
    def create_provider(
        provider_type: str, config: Optional[Dict[str, Any]] = None
    ) -> LLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider_type: Type of provider to create
            config: Configuration parameters for the provider

        Returns:
            An LLM provider instance

        Raises:
            ValueError: If the provider type is not supported
        """
        config = config or {}

        if provider_type.lower() == "mock":
            return MockLLMProvider(
                provider_name=config.get("provider_name", "MockProvider"),
                model_name=config.get("model_name", "mock-model-v1"),
                latency_range=config.get("latency_range", (0.5, 2.0)),
                error_rate=config.get("error_rate", 0.0),
            )

        elif provider_type.lower() == "smart_mock":
            return SmartMockLLMProvider(
                provider_name=config.get("provider_name", "SmartMockProvider"),
                model_name=config.get("model_name", "smart-mock-model-v1"),
                latency_range=config.get("latency_range", (1.0, 3.0)),
                error_rate=config.get("error_rate", 0.0),
                improvement_rate=config.get("improvement_rate", 0.2),
            )

        # Add more provider types here as they are implemented
        # elif provider_type.lower() == "openai":
        #     return OpenAIProvider(...)

        else:
            raise ValueError(f"Unsupported LLM provider type: {provider_type}")


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_mock_provider():
        # Create a mock provider
        provider = LLMProviderFactory.create_provider("mock")

        # Create a request
        request = LLMRequest(
            request_type=LLMRequestType.GENERATE,
            prompt="Create a dark trap artist with mysterious vibes",
            parameters={"temperature": 0.7},
        )

        # Send the request
        response = await provider.send_request(request)

        # Print the response
        print(f"Request: {request.to_dict()}")
        print(f"Response: {response.to_dict()}")

    # Run the test
    asyncio.run(test_mock_provider())
