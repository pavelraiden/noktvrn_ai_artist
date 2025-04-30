"""
Orchestrator Module

This module provides the core orchestration functionality for LLM interactions,
focusing on specific tasks like profile evolution and prompt adaptation.
"""

import logging
import os
from typing import Dict, Any, Optional
import asyncio

# Attempt to import necessary components
try:
    from openai import OpenAI, AsyncOpenAI, APIError, RateLimitError
except ImportError:
    # Handle cases where openai might not be installed, though it should be
    # In a real application, might raise a more specific error or log warning
    OpenAI = None
    AsyncOpenAI = None
    APIError = Exception
    RateLimitError = Exception
    print("Warning: OpenAI library not found. LLM functionality will be limited.")

try:
    # Adjust the import path based on the project structure
    # Assuming orchestrator.py is in llm_orchestrator/
    from ..scripts.utils.env_utils import load_env_vars
except ImportError:
    # Fallback if the relative import fails (e.g., running script directly)
    try:
        from scripts.utils.env_utils import load_env_vars
    except ImportError:
        print("Warning: env_utils not found. API keys must be provided directly.")
        def load_env_vars():
            return {}

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class LLMOrchestrator:
    """
    Orchestrates interactions with a primary LLM provider for various tasks,
    including profile evolution and prompt adaptation.
    Uses AsyncOpenAI for non-blocking operations.
    """

    def __init__(
        self,
        provider_type: str = "openai",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the orchestrator with a primary LLM provider.

        Args:
            provider_type: The type of LLM provider (currently only 'openai' supported).
            model_name: The specific model to use (e.g., 'gpt-4'). Reads from env if None.
            api_key: The API key. Reads from env if None.
            config: Additional configuration for the provider (e.g., temperature, max_retries).
        """
        if provider_type.lower() != "openai":
            raise NotImplementedError("Currently, only the 'openai' provider is supported.")
        if not AsyncOpenAI:
             raise ImportError("OpenAI library is required but not installed or failed to import.")

        env_vars = load_env_vars()
        self.config = config or {}
        self.api_key = api_key or env_vars.get("OPENAI_API_KEY")
        # Use a sensible default model if not provided or found in env
        self.model_name = model_name or env_vars.get("OPENAI_MODEL_NAME", "gpt-4o") 

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables or provided directly.")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.max_retries = self.config.get("max_retries", 3)
        self.initial_delay = self.config.get("initial_delay", 1.0)

        logger.info(f"Initialized LLMOrchestrator with provider: {provider_type}, model: {self.model_name}")

    async def _call_llm_with_retry(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Internal method to call the LLM API with retry logic."""
        retries = 0
        delay = self.initial_delay
        last_exception = None

        while retries < self.max_retries:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    n=1,
                    stop=None,
                )
                # Ensure response.choices exists and has at least one item
                if response.choices and len(response.choices) > 0:
                    # Ensure the choice has a message attribute
                    if response.choices[0].message:
                        # Ensure the message has a content attribute
                        if response.choices[0].message.content:
                             # Log token usage if available
                            if response.usage:
                                logger.info(f"LLM API call successful. Usage: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}, Total={response.usage.total_tokens}")
                            else:
                                logger.info("LLM API call successful. Usage data not available.")
                            return response.choices[0].message.content.strip()
                        else:
                            raise ValueError("LLM response message content is empty or None.")
                    else:
                         raise ValueError("LLM response choice does not contain a message.")
                else:
                    raise ValueError("LLM response did not contain any choices.")
                    
            except RateLimitError as e:
                retries += 1
                logger.warning(f"Rate limit exceeded. Retrying in {delay} seconds... ({retries}/{self.max_retries})")
                last_exception = e
                await asyncio.sleep(delay)
                delay *= 2 # Exponential backoff
            except APIError as e:
                retries += 1
                logger.warning(f"API error occurred: {e}. Retrying in {delay} seconds... ({retries}/{self.max_retries})")
                last_exception = e
                await asyncio.sleep(delay)
                delay *= 2
            except Exception as e:
                # Catch other potential errors (network, unexpected response format)
                logger.error(f"An unexpected error occurred during LLM call: {e}", exc_info=True)
                last_exception = e
                break # Don't retry on unexpected errors

        error_msg = f"LLM call failed after {self.max_retries} retries."
        logger.error(error_msg)
        if last_exception:
             raise last_exception from None # Reraise the last caught exception
        else:
             raise Exception(error_msg) # Raise generic exception if no specific one was caught

    async def generate_text(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """
        Generates text based on a given prompt using the configured LLM.

        Args:
            prompt: The input prompt.
            max_tokens: Maximum tokens for the response.
            temperature: Sampling temperature.

        Returns:
            The generated text.

        Raises:
            Exception: If the API call fails after retries.
        """
        logger.info(f"Generating text for prompt (first 100 chars): {prompt[:100]}...")
        return await self._call_llm_with_retry(prompt, max_tokens, temperature)

    async def adapt_prompt(
        self,
        original_prompt: str,
        adaptation_instructions: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """
        Adapts an existing prompt based on instructions and context.

        Args:
            original_prompt: The original prompt to be adapted.
            adaptation_instructions: Specific instructions on how to modify the prompt.
            context: Optional dictionary providing context (e.g., trend analysis results).
            max_tokens: Maximum tokens for the response.
            temperature: Sampling temperature.

        Returns:
            The adapted prompt string.

        Raises:
            Exception: If the API call fails after retries.
        """
        context_str = f"\n\nRelevant Context:\n```json\n{context}\n```" if context else ""
        # Enhanced prompt structure for clarity
        combined_prompt = f"""
        **Task:** Adapt the following ORIGINAL PROMPT based on the provided INSTRUCTIONS and CONTEXT.
        **Output Requirements:** Respond with *only* the adapted prompt text, ready for direct use. Do not include explanations or introductions.

        **INSTRUCTIONS:**
        {adaptation_instructions}
        {context_str}

        **ORIGINAL PROMPT:**
        ```
        {original_prompt}
        ```
        """
        logger.info(f"Adapting prompt based on instructions (first 100 chars): {adaptation_instructions[:100]}...")
        adapted_prompt = await self.generate_text(combined_prompt, max_tokens, temperature)
        # Clean up potential markdown code blocks if the LLM includes them
        if adapted_prompt.startswith("```") and adapted_prompt.endswith("```"):
             adapted_prompt = adapted_prompt[3:-3].strip()
        return adapted_prompt

    async def evolve_description(
        self,
        current_description: str,
        evolution_goal: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 512,
        temperature: float = 0.8
    ) -> str:
        """
        Evolves an artist's description based on a goal and context.

        Args:
            current_description: The current artist description.
            evolution_goal: The goal for the evolution (e.g., "Make it more appealing to a younger audience", "Incorporate recent success in country X").
            context: Optional dictionary providing context (e.g., performance data, trend analysis).
            max_tokens: Maximum tokens for the response.
            temperature: Sampling temperature.

        Returns:
            The evolved description string.

        Raises:
            Exception: If the API call fails after retries.
        """
        context_str = f"\n\nRelevant Context:\n```json\n{context}\n```" if context else ""
        # Enhanced prompt structure
        combined_prompt = f"""
        **Task:** Rewrite the following CURRENT ARTIST DESCRIPTION to achieve the EVOLUTION GOAL, considering the provided CONTEXT.
        **Output Requirements:** Respond with *only* the new description text. Do not include explanations or introductions.

        **EVOLUTION GOAL:**
        {evolution_goal}
        {context_str}

        **CURRENT ARTIST DESCRIPTION:**
        ```
        {current_description}
        ```
        """
        logger.info(f"Evolving description based on goal (first 100 chars): {evolution_goal[:100]}...")
        evolved_description = await self.generate_text(combined_prompt, max_tokens, temperature)
        # Clean up potential markdown code blocks
        if evolved_description.startswith("```") and evolved_description.endswith("```"):
             evolved_description = evolved_description[3:-3].strip()
        return evolved_description

# Note: Removed OrchestrationResult, OrchestrationStatus, OrchestratorFactory, and complex loop logic
# as per the simplified design for Phase 2. Can be reintroduced later if needed.

