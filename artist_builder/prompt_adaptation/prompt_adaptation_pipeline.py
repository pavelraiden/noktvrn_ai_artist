"""
Prompt Adaptation Pipeline Module

This module is responsible for adapting content generation prompts based on
analysis results, strategic goals, and other contextual information using LLMs.
It leverages the LLMOrchestrator to perform the actual adaptation.
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional

# Assuming LLMOrchestrator is in the llm_orchestrator directory
# Adjust import path based on actual project structure
try:
    from ...llm_orchestrator.orchestrator import LLMOrchestrator
except ImportError:
    # Fallback for different execution contexts or potential restructuring
    try:
        from llm_orchestrator.orchestrator import LLMOrchestrator
    except ImportError as e:
        print(f"Error importing LLMOrchestrator: {e}. Ensure it is correctly placed.")
        LLMOrchestrator = None # Set to None if import fails

# Database interaction is generally handled by the calling module which builds the context.
# This pipeline focuses solely on the LLM interaction for adaptation.

logger = logging.getLogger(__name__)

class PromptAdaptationPipeline:
    """
    Manages the adaptation of content generation prompts using an LLM.
    Takes original prompts, adaptation instructions, and rich context (potentially
    derived from real-time data analysis) to generate new, optimized prompts.
    """

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        """
        Initializes the PromptAdaptationPipeline.

        Args:
            llm_config: Configuration dictionary for the LLMOrchestrator.
        """
        if not LLMOrchestrator:
            raise ImportError("LLMOrchestrator could not be imported. Prompt adaptation is unavailable.")
        
        # Initialize LLM Orchestrator (reads API keys/model from env by default)
        self.llm_orchestrator = LLMOrchestrator(config=llm_config)
        logger.info("PromptAdaptationPipeline initialized.")

    async def adapt_artist_prompt(
        self,
        original_prompt: str,
        adaptation_instructions: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1024, # Default max tokens for adapted prompt
        temperature: float = 0.7 # Default temperature
    ) -> Optional[str]:
        """
        Adapts a given prompt based on instructions and context using the LLM.

        The context dictionary can be rich and include various data points derived
        from real-time analysis, such as:
        - artist_profile: {genre, style, target_audience, ...}
        - performance: {recent_metrics, top_countries, ...}
        - country_trends: {country_code: [trend_data, ...], ...}
        - competitor_analysis: {summary, gaps, ...}
        - evolution_history: [previous_evolution_data, ...]

        Args:
            original_prompt: The original prompt string to be adapted.
            adaptation_instructions: Specific instructions guiding the adaptation 
                                     (e.g., "Make it suitable for German market trends").
            context: Optional dictionary providing context for the adaptation.
            max_tokens: Maximum tokens for the LLM response (the adapted prompt).
            temperature: Sampling temperature for the LLM.

        Returns:
            The adapted prompt string if successful, otherwise None.
        """
        logger.info(f"Starting prompt adaptation. Instructions: {adaptation_instructions[:100]}...")
        if context:
            # Log context keys for debugging, avoid logging full potentially large context
            logger.debug(f"Using context keys: {list(context.keys())}")
        else:
            logger.debug("No context provided for prompt adaptation.")

        try:
            adapted_prompt = await self.llm_orchestrator.adapt_prompt(
                original_prompt=original_prompt,
                adaptation_instructions=adaptation_instructions,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature
            )
            if adapted_prompt:
                logger.info("Successfully generated adapted prompt.")
            else:
                # Handle cases where LLM might return empty/None without exception
                logger.warning("LLM returned an empty or None result for prompt adaptation.")
                return None
                
            return adapted_prompt
        except Exception as e:
            logger.error(f"LLM call failed during prompt adaptation: {e}", exc_info=True)
            return None

# Example Usage (requires async context)
async def main_example():
    # This is a conceptual example. Actual usage requires setting up
    # environment variables (like OPENAI_API_KEY).
    logging.basicConfig(level=logging.INFO)
    
    prompt_adapter = PromptAdaptationPipeline()
    
    original = "Generate lyrics for a pop song about summer love."
    # Instructions derived from analysis (e.g., by ArtistEvolutionManager)
    instructions = "Adapt the prompt for an indie folk artist. Incorporate themes of nostalgia and changing seasons based on recent trend analysis showing a shift towards introspective music in the target US market."
    
    # Context built from real data analysis (e.g., by ArtistEvolutionManager)
    analysis_context = {
        "artist_profile": {"genre": "Indie Folk", "style": "Acoustic, melancholic vocals"},
        "performance": {"recent_metrics": [{"streams": 10000, "sentiment": "positive"}], "top_countries": ["US", "DE"]},
        "country_trends": {"US": [{"genre_trend": "Indie Folk gaining popularity", "theme_trend": "Nostalgia and introspection resonating well"}]},
        "evolution_history": [{"goal": "Shift towards more acoustic sound", "outcome": "positive engagement"}]
    }
    
    print(f"Attempting to adapt prompt: ")
    print(f"  Original: {original}")
    print(f"  Instructions: {instructions}")
    
    new_prompt = await prompt_adapter.adapt_artist_prompt(
        original_prompt=original,
        adaptation_instructions=instructions,
        context=analysis_context
    )
    
    if new_prompt:
        print("\n--- Adapted Prompt ---")
        print(new_prompt)
        print("----------------------")
    else:
        print("\nFailed to adapt prompt.")

# if __name__ == "__main__":
#     asyncio.run(main_example())

