"""
Prompt Validator Module

This module provides functionality for validating artist prompts based on quality criteria.
It assesses style, coherence, and completeness, and provides feedback for improvement.
"""

import re
import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("prompt_validator")


class ValidationResult(Enum):
    """Result of a prompt validation."""

    VALID = "valid"
    NEEDS_IMPROVEMENT = "needs_improvement"
    INVALID = "invalid"


class PromptValidator:
    """
    Validates artist prompts based on quality criteria.

    This class assesses prompts for style, coherence, and completeness,
    and provides feedback for improvement.
    """

    def __init__(
        self,
        min_length: int = 100,
        max_length: int = 1000,
        required_elements: Optional[List[str]] = None,
        confidence_threshold: float = 0.7,
        style_keywords: Optional[List[str]] = None,
    ):
        """
        Initialize a new prompt validator.

        Args:
            min_length: Minimum acceptable prompt length
            max_length: Maximum acceptable prompt length
            required_elements: List of elements that must be present in the prompt
            confidence_threshold: Minimum confidence score for a valid prompt
            style_keywords: List of keywords that indicate good style
        """
        self.min_length = min_length
        self.max_length = max_length
        self.required_elements = required_elements or [
            "genre",
            "style",
            "vibe",
            "artist",
        ]
        self.confidence_threshold = confidence_threshold
        self.style_keywords = style_keywords or [
            "unique",
            "creative",
            "authentic",
            "distinctive",
            "original",
            "innovative",
            "fresh",
            "compelling",
            "engaging",
            "captivating",
        ]

        logger.info("Initialized prompt validator")

    def validate_prompt(
        self, prompt: str
    ) -> Tuple[ValidationResult, float, Dict[str, Any]]:
        """
        Validate an artist prompt based on quality criteria.

        Args:
            prompt: The artist prompt to validate

        Returns:
            A tuple of (validation result, confidence score, detailed feedback)
        """
        # Initialize feedback dictionary
        feedback = {
            "length": {"status": "pass", "message": ""},
            "required_elements": {"status": "pass", "message": "", "missing": []},
            "style": {"status": "pass", "message": "", "keywords_found": []},
            "coherence": {"status": "pass", "message": ""},
            "improvement_suggestions": [],
        }

        # Check length
        length_score, length_feedback = self._check_length(prompt)
        feedback["length"] = length_feedback

        # Check required elements
        elements_score, elements_feedback = self._check_required_elements(prompt)
        feedback["required_elements"] = elements_feedback

        # Check style
        style_score, style_feedback = self._check_style(prompt)
        feedback["style"] = style_feedback

        # Check coherence
        coherence_score, coherence_feedback = self._check_coherence(prompt)
        feedback["coherence"] = coherence_feedback

        # Calculate overall confidence score
        confidence_score = self.calculate_confidence_score(
            length_score, elements_score, style_score, coherence_score
        )

        # Generate improvement suggestions
        feedback["improvement_suggestions"] = self.generate_feedback(feedback)

        # Determine validation result
        if confidence_score >= self.confidence_threshold:
            result = ValidationResult.VALID
        elif confidence_score >= self.confidence_threshold * 0.7:
            result = ValidationResult.NEEDS_IMPROVEMENT
        else:
            result = ValidationResult.INVALID

        logger.info(
            f"Validated prompt with score {confidence_score:.2f}, result: {result.value}"
        )
        return result, confidence_score, feedback

    def calculate_confidence_score(
        self,
        length_score: float,
        elements_score: float,
        style_score: float,
        coherence_score: float,
    ) -> float:
        """
        Calculate an overall confidence score based on individual criteria scores.

        Args:
            length_score: Score for prompt length (0.0-1.0)
            elements_score: Score for required elements (0.0-1.0)
            style_score: Score for style quality (0.0-1.0)
            coherence_score: Score for coherence (0.0-1.0)

        Returns:
            An overall confidence score between 0.0 and 1.0
        """
        # Weights for different criteria
        weights = {"length": 0.1, "elements": 0.3, "style": 0.3, "coherence": 0.3}

        # Calculate weighted score
        weighted_score = (
            length_score * weights["length"]
            + elements_score * weights["elements"]
            + style_score * weights["style"]
            + coherence_score * weights["coherence"]
        )

        # Add a small random variation to simulate real-world scoring
        variation = random.uniform(-0.05, 0.05)
        final_score = max(0.0, min(1.0, weighted_score + variation))

        return final_score

    def generate_feedback(self, feedback_dict: Dict[str, Any]) -> List[str]:
        """
        Generate improvement suggestions based on validation feedback.

        Args:
            feedback_dict: Detailed feedback from validation

        Returns:
            A list of improvement suggestions
        """
        suggestions = []

        # Add length suggestions
        if feedback_dict["length"]["status"] == "fail":
            suggestions.append(feedback_dict["length"]["message"])

        # Add required elements suggestions
        if feedback_dict["required_elements"]["status"] == "fail":
            missing = feedback_dict["required_elements"]["missing"]
            if missing:
                elements_str = ", ".join(missing)
                suggestions.append(
                    f"Include information about the following elements: {elements_str}"
                )

        # Add style suggestions
        if feedback_dict["style"]["status"] == "fail":
            suggestions.append(
                "Enhance the creative language and use more descriptive terms"
            )
            suggestions.append(
                "Consider adding more unique and distinctive characteristics"
            )

        # Add coherence suggestions
        if feedback_dict["coherence"]["status"] == "fail":
            suggestions.append("Improve the flow and logical connection between ideas")
            suggestions.append("Ensure the description has a consistent tone and theme")

        # If no specific suggestions, add a general one
        if not suggestions:
            suggestions.append(
                "The prompt is acceptable but could be enhanced with more vivid descriptions"
            )

        return suggestions

    def _check_length(self, prompt: str) -> Tuple[float, Dict[str, Any]]:
        """
        Check if the prompt length is within acceptable range.

        Args:
            prompt: The prompt to check

        Returns:
            A tuple of (score, feedback)
        """
        length = len(prompt)
        feedback = {
            "status": "pass",
            "message": f"Length is acceptable ({length} characters)",
            "actual_length": length,
        }

        if length < self.min_length:
            feedback["status"] = "fail"
            feedback["message"] = (
                f"Prompt is too short ({length} characters). Minimum required is {self.min_length}."
            )
            return max(0.0, length / self.min_length), feedback

        if length > self.max_length:
            feedback["status"] = "fail"
            feedback["message"] = (
                f"Prompt is too long ({length} characters). Maximum allowed is {self.max_length}."
            )
            return (
                max(0.0, 1.0 - (length - self.max_length) / self.max_length),
                feedback,
            )

        # Calculate score based on optimal length (somewhere in the middle)
        optimal_length = (self.min_length + self.max_length) / 2
        distance_from_optimal = abs(length - optimal_length) / optimal_length
        score = max(0.0, 1.0 - distance_from_optimal)

        return score, feedback

    def _check_required_elements(self, prompt: str) -> Tuple[float, Dict[str, Any]]:
        """
        Check if the prompt contains all required elements.

        Args:
            prompt: The prompt to check

        Returns:
            A tuple of (score, feedback)
        """
        prompt_lower = prompt.lower()
        missing_elements = []
        found_elements = []

        for element in self.required_elements:
            if element.lower() not in prompt_lower:
                missing_elements.append(element)
            else:
                found_elements.append(element)

        feedback = {
            "status": "pass",
            "message": "All required elements are present",
            "missing": missing_elements,
            "found": found_elements,
        }

        if missing_elements:
            feedback["status"] = "fail"
            elements_str = ", ".join(missing_elements)
            feedback["message"] = f"Missing required elements: {elements_str}"

        # Calculate score based on percentage of elements found
        score = len(found_elements) / len(self.required_elements)

        return score, feedback

    def _check_style(self, prompt: str) -> Tuple[float, Dict[str, Any]]:
        """
        Check if the prompt has good style based on keywords.

        Args:
            prompt: The prompt to check

        Returns:
            A tuple of (score, feedback)
        """
        prompt_lower = prompt.lower()
        keywords_found = []

        for keyword in self.style_keywords:
            if keyword.lower() in prompt_lower:
                keywords_found.append(keyword)

        feedback = {
            "status": "pass",
            "message": "Style is creative and engaging",
            "keywords_found": keywords_found,
        }

        # Require at least 2 style keywords for a pass
        if len(keywords_found) < 2:
            feedback["status"] = "fail"
            feedback["message"] = (
                "Style lacks creativity and distinctive characteristics"
            )

        # Calculate score based on percentage of keywords found (with diminishing returns)
        max_expected = min(len(self.style_keywords), 5)  # Don't expect all keywords
        score = min(1.0, len(keywords_found) / max_expected)

        return score, feedback

    def _check_coherence(self, prompt: str) -> Tuple[float, Dict[str, Any]]:
        """
        Check if the prompt is coherent and well-structured.

        Args:
            prompt: The prompt to check

        Returns:
            A tuple of (score, feedback)
        """
        # This is a simplified mock implementation
        # In a real system, this would use more sophisticated NLP techniques

        # Check for sentence structure (simple heuristic)
        sentences = re.split(r"[.!?]+", prompt)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Check for very short sentences (potential fragments)
        short_sentences = [s for s in sentences if len(s.split()) < 3]

        # Check for very long sentences (potential run-ons)
        long_sentences = [s for s in sentences if len(s.split()) > 25]

        feedback = {
            "status": "pass",
            "message": "Prompt is coherent and well-structured",
            "sentence_count": len(sentences),
            "short_sentences": len(short_sentences),
            "long_sentences": len(long_sentences),
        }

        # Simple heuristic: too many short or long sentences indicates poor coherence
        if (
            len(short_sentences) > len(sentences) * 0.3
            or len(long_sentences) > len(sentences) * 0.3
        ):
            feedback["status"] = "fail"
            feedback["message"] = "Prompt has issues with sentence structure and flow"

        # Calculate score based on sentence structure
        short_penalty = (
            min(1.0, len(short_sentences) / len(sentences) * 3) if sentences else 0
        )
        long_penalty = (
            min(1.0, len(long_sentences) / len(sentences) * 3) if sentences else 0
        )
        score = max(0.0, 1.0 - (short_penalty + long_penalty) / 2)

        # Add a random component to simulate more complex coherence analysis
        score = max(0.0, min(1.0, score + random.uniform(-0.1, 0.1)))

        return score, feedback


# Example usage
if __name__ == "__main__":
    # Create a validator
    validator = PromptValidator()

    # Example prompt
    example_prompt = """
    A mysterious dark trap artist who thrives in the urban night scene. 
    Their music combines haunting melodies with heavy bass, creating a unique atmospheric sound.
    Always seen wearing a black hood and mask, their identity remains hidden, adding to their enigmatic presence.
    Their deep, raspy voice delivers lyrics about city life and personal struggles, resonating with listeners
    who connect with the authentic emotion in their music.
    """

    # Validate the prompt
    result, score, feedback = validator.validate_prompt(example_prompt)

    # Print the results
    print(f"Validation Result: {result.value}")
    print(f"Confidence Score: {score:.2f}")
    print("\nDetailed Feedback:")
    for category, details in feedback.items():
        if isinstance(details, dict) and "status" in details:
            print(f"- {category}: {details['status']} - {details['message']}")

    print("\nImprovement Suggestions:")
    for suggestion in feedback["improvement_suggestions"]:
        print(f"- {suggestion}")
