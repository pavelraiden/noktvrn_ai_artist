"""
Integration module for connecting the Artist Prompt Designer with the LLM Orchestrator.

This module provides the necessary functionality to integrate the artist_prompt_designer
with the orchestrator for generating, reviewing, and refining artist identity prompts.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Tuple

from artist_builder.prompts.artist_prompt_designer import ArtistPromptDesigner
from llm_orchestrator.orchestrator import (
    Orchestrator,
    OrchestratorFactory,
    OrchestrationResult,
    OrchestrationStatus,
)
from llm_orchestrator.session_manager import SessionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("artist_orchestrator_integration")


class ArtistPromptOrchestrator:
    """
    Orchestrates the generation, review, and refinement of artist identity prompts.

    This class integrates the ArtistPromptDesigner with the LLM Orchestrator to
    create high-quality artist identity prompts through an iterative review process.
    """

    def __init__(
        self,
        orchestrator: Optional[Orchestrator] = None,
        session_manager: Optional[SessionManager] = None,
        confidence_threshold: float = 0.8,
        max_iterations: int = 3,
    ):
        """
        Initialize a new artist prompt orchestrator.

        Args:
            orchestrator: The LLM orchestrator to use (created if None)
            session_manager: The session manager to use (created if None)
            confidence_threshold: Minimum confidence score to consider a prompt acceptable
            max_iterations: Maximum number of refinement iterations
        """
        # Create default orchestrator if not provided
        self.orchestrator = (
            orchestrator
            or OrchestratorFactory.create_default_orchestrator(
                confidence_threshold=confidence_threshold, max_iterations=max_iterations
            )
        )

        # Create default session manager if not provided
        self.session_manager = session_manager or SessionManager()

        # Create artist prompt designer
        self.prompt_designer = ArtistPromptDesigner()

        logger.info("Initialized artist prompt orchestrator")

    async def create_artist_prompt(
        self, artist_parameters: Dict[str, str], session_id: Optional[str] = None
    ) -> Tuple[str, OrchestrationResult]:
        """
        Create an artist identity prompt through orchestrated generation and review.

        Args:
            artist_parameters: Parameters for the artist identity (genre, vibe, etc.)
            session_id: ID of the session to use (created if None)

        Returns:
            A tuple of (final prompt, orchestration result)
        """
        # Create a session if not provided
        if not session_id:
            session = self.session_manager.create_session(
                metadata={"type": "artist_prompt", "parameters": artist_parameters}
            )
            session_id = session.id
        else:
            # Get existing session or create new one with provided ID
            session = self.session_manager.get_session(session_id)
            if not session:
                session = self.session_manager.create_session(
                    session_id=session_id,
                    metadata={"type": "artist_prompt", "parameters": artist_parameters},
                )

        # Set the orchestrator's session ID
        self.orchestrator.session_id = session_id

        # Generate initial prompt
        initial_prompt_package = self.prompt_designer.generate_prompt_for_review(
            artist_parameters
        )
        initial_prompt = initial_prompt_package["generated_prompt"]

        # Create orchestration prompt for review and refinement
        orchestration_prompt = self._create_orchestration_prompt(initial_prompt_package)

        # Orchestrate the prompt
        logger.info(f"Orchestrating artist prompt with parameters: {artist_parameters}")
        result = await self.orchestrator.orchestrate_prompt(
            orchestration_prompt, parameters={"artist_parameters": artist_parameters}
        )

        # Add the result to the session
        self.session_manager.add_orchestration_to_session(session_id, result)

        # Extract the final prompt from the result
        final_prompt = self._extract_final_prompt(result.content)

        logger.info(
            f"Created artist prompt with confidence score: {result.confidence_score}"
        )
        return final_prompt, result

    def _create_orchestration_prompt(self, prompt_package: Dict[str, Any]) -> str:
        """
        Create a prompt for the orchestrator based on the artist prompt package.

        Args:
            prompt_package: The artist prompt package from the designer

        Returns:
            A prompt for the orchestrator
        """
        # Extract components from the package
        parameters = prompt_package["parameters"]
        generated_prompt = prompt_package["generated_prompt"]

        # Create a detailed prompt for the orchestrator
        orchestration_prompt = f"""
        # Artist Identity Prompt Review and Refinement
        
        ## Original Parameters
        {json.dumps(parameters, indent=2)}
        
        ## Generated Prompt
        {generated_prompt}
        
        ## Review Instructions
        Please review this artist identity prompt for:
        1. Coherence and clarity
        2. Alignment with the specified parameters
        3. Creativity and uniqueness
        4. Professional tone and language
        
        Provide specific feedback on how to improve the prompt if needed.
        If the prompt is already high quality, indicate that it meets all requirements.
        """

        return orchestration_prompt

    def _extract_final_prompt(self, orchestration_content: str) -> str:
        """
        Extract the final prompt from the orchestration result content.

        Args:
            orchestration_content: The content from the orchestration result

        Returns:
            The extracted final prompt
        """
        # For mock implementations, the content might be the full response
        # In a real implementation, we would parse the structured response

        # Simple extraction: look for the last occurrence of text that looks like a prompt
        lines = orchestration_content.split("\n")
        prompt_lines = []
        in_prompt_section = False

        for line in lines:
            line = line.strip()

            # Look for markers that might indicate the start of the final prompt
            if (
                "final prompt" in line.lower()
                or "improved prompt" in line.lower()
                or "refined prompt" in line.lower()
            ):
                in_prompt_section = True
                prompt_lines = []  # Reset to capture only the latest prompt
                continue

            # If we're in a prompt section, collect lines until we hit a section marker
            if in_prompt_section:
                if line.startswith("#") or line.startswith("##") or not line:
                    if prompt_lines:  # Only end if we've collected something
                        in_prompt_section = False
                else:
                    prompt_lines.append(line)

        # If we didn't find a clearly marked prompt section, use heuristics
        if not prompt_lines:
            # Look for the longest paragraph that doesn't look like feedback
            paragraphs = orchestration_content.split("\n\n")
            candidate_prompt = ""

            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if len(paragraph) > len(candidate_prompt) and not any(
                    x in paragraph.lower()
                    for x in ["feedback", "review", "suggestion", "improve"]
                ):
                    candidate_prompt = paragraph

            if candidate_prompt:
                return candidate_prompt

            # Fallback: just return the whole content
            return orchestration_content

        return "\n".join(prompt_lines)


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_artist_prompt_orchestrator():
        # Create an artist prompt orchestrator
        orchestrator = ArtistPromptOrchestrator()

        # Define artist parameters
        artist_parameters = {
            "genre": "Dark Trap",
            "vibe": "Mysterious, Cold",
            "lifestyle": "Urban night life",
            "appearance": "Always wears a black hood and mask",
            "voice": "Deep and raspy",
        }

        # Create an artist prompt
        prompt, result = await orchestrator.create_artist_prompt(artist_parameters)

        # Print the results
        print(f"Final Prompt:\n{prompt}\n")
        print(f"Confidence Score: {result.confidence_score}")
        print(f"Iterations: {result.iterations}")

    # Run the test
    asyncio.run(test_artist_prompt_orchestrator())
