# llm_orchestrator/orchestrator.py Modification

"""
Orchestrator Module - Multi-Provider Support with Fallback & Auto-Discovery

This module provides the core orchestration functionality for LLM interactions,
supporting multiple providers (OpenAI, DeepSeek, Grok, Gemini, Mistral, Anthropic)
and implementing inter-provider fallback logic.

Includes basic auto-discovery of models listed in llm_registry.py.
"""

import logging
import os
import sys
import json
from typing import Dict, Any, Optional, Literal, List, Tuple, Type
import asyncio
from dotenv import load_dotenv

# --- Load Environment Variables ---
# Load from project root first, then local if exists
PROJECT_ROOT_DOTENV = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(PROJECT_ROOT_DOTENV):
    load_dotenv(dotenv_path=PROJECT_ROOT_DOTENV, override=False)
DOTENV_PATH = os.path.join(
    os.path.dirname(__file__), ".env"
)  # Check for local .env too
if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH, override=True)  # Local can override root

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# --- Configure logging (Moved Up) ---
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Import necessary components ---
try:
    from openai import AsyncOpenAI, APIError, RateLimitError
except ImportError:
    AsyncOpenAI = None
    APIError = Exception
    RateLimitError = Exception
    logger.warning(
        "OpenAI library not found. OpenAI, DeepSeek, Grok functionality will be limited."
    )

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold

    DEFAULT_GEMINI_SAFETY_SETTINGS = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
except ImportError:
    genai = None
    HarmCategory = None
    HarmBlockThreshold = None
    DEFAULT_GEMINI_SAFETY_SETTINGS = {}
    logger.warning(
        "google-generativeai library not found. Gemini functionality will be limited."
    )

try:
    from mistralai.client import MistralClient
    from mistralai.async_client import MistralAsyncClient
    from mistralai.models.chat_completion import ChatMessage
except ImportError:
    MistralAsyncClient = None
    ChatMessage = None
    logger.warning(
        "mistralai library not found. Mistral functionality will be limited."
    )

try:
    from anthropic import (
        AsyncAnthropic,
        APIError as AnthropicAPIError,
        RateLimitError as AnthropicRateLimitError,
    )
except ImportError:
    AsyncAnthropic = None
    AnthropicAPIError = Exception
    AnthropicRateLimitError = Exception
    logger.warning("Anthropic library not found. Claude functionality will be limited.")

# Import the registry
try:
    from llm_orchestrator.llm_registry import LLM_REGISTRY
except ImportError:
    LLM_REGISTRY = {}
    logger.warning(
        "llm_registry.py not found or LLM_REGISTRY not defined. Auto-discovery disabled."
    )

# Import Telegram Service for notifications
try:
    from services.telegram_service import send_notification
except ImportError:
    logger.warning("Telegram service not found, fallback notifications disabled.")

    async def send_notification(message: str):
        logger.debug(f"Telegram notification skipped (service unavailable): {message}")
        await asyncio.sleep(0)  # No-op awaitable


# --- Provider Configuration --- #
# Enhanced PROVIDER_CONFIG to include Anthropic and check library presence
PROVIDER_CONFIG = {
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "client_class": AsyncOpenAI,
        "library_present": AsyncOpenAI is not None,
    },
    "deepseek": {
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
        "client_class": AsyncOpenAI,
        "library_present": AsyncOpenAI is not None,
    },
    "grok": {
        "api_key_env": "GROK_API_KEY",
        "base_url": "https://api.x.ai/v1",
        "client_class": AsyncOpenAI,
        "library_present": AsyncOpenAI is not None,
    },
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "base_url": None,
        "client_class": None,  # Special handling
        "library_present": genai is not None,
    },
    "mistral": {
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": None,
        "client_class": MistralAsyncClient,
        "library_present": MistralAsyncClient is not None,
    },
    "anthropic": {
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": None,
        "client_class": AsyncAnthropic,
        "library_present": AsyncAnthropic is not None,
    },
}


# --- Helper Function to Get Env Var ---
def get_env_var(key: str) -> Optional[str]:
    return os.environ.get(key)


# --- LLM Orchestrator --- #
class LLMOrchestratorError(Exception):
    """Custom exception for LLM Orchestrator errors."""

    pass


class LLMProviderInstance:
    """Holds the initialized client and config for a specific provider/model."""

    def __init__(
        self, provider: str, model_name: str, api_key: str, config: Dict[str, Any]
    ):
        self.provider = provider
        self.model_name = model_name
        self.api_key = api_key
        self.config = config
        self.provider_info = PROVIDER_CONFIG[provider]
        self.client = self._initialize_client()

    def _initialize_client(self) -> Any:
        client_class = self.provider_info["client_class"]
        base_url = self.provider_info["base_url"]

        if self.provider == "gemini":
            if not genai:
                raise ImportError("Gemini library required.")
            genai.configure(api_key=self.api_key)
            return genai.GenerativeModel(self.model_name)
        elif client_class:
            client_args = {"api_key": self.api_key}
            if base_url:
                client_args["base_url"] = base_url
            return client_class(**client_args)
        else:
            raise LLMOrchestratorError(
                f"Client class not defined or library missing for {self.provider}"
            )


class LLMOrchestrator:
    """
    Orchestrates interactions with multiple LLM providers.
    Supports a primary model, a list of fallback models, and auto-discovery from registry.
    Handles API key loading, client initialization, and API calls with retries and inter-provider fallback.
    Includes Telegram notifications for fallback events.
    """

    def __init__(
        self,
        primary_model: str,  # e.g., "deepseek:deepseek-chat"
        fallback_models: Optional[
            List[str]
        ] = None,  # e.g., ["gemini-pro", "mistral-large-latest"]
        config: Optional[Dict[str, Any]] = None,
        enable_auto_discovery: bool = True,  # Flag to enable/disable discovery
        enable_fallback_notifications: bool = True,  # Flag to enable/disable Telegram notifications
    ):
        """
        Initialize the orchestrator with primary, fallback, and potentially discovered models.

        Args:
            primary_model: The preferred model to use first (e.g., "deepseek:deepseek-chat").
            fallback_models: A list of model names to try in order if the primary fails.
            config: Additional configuration (e.g., temperature, max_retries, initial_delay).
            enable_auto_discovery: If True, attempts to add models from LLM_REGISTRY
                                     that are not already in primary/fallback.
            enable_fallback_notifications: If True, send Telegram notifications on fallback events.
        """
        self.config = config or {}
        self.max_retries_per_provider = self.config.get("max_retries", 3)
        self.initial_delay = self.config.get("initial_delay", 1.0)
        self.enable_fallback_notifications = enable_fallback_notifications

        self.providers: Dict[str, LLMProviderInstance] = {}
        self.model_preference: List[Tuple[str, str]] = (
            []
        )  # List of (provider, model_name)
        self.initialized_models = set()  # Keep track of (provider, model) tuples added

        # Initialize primary model
        self._add_provider(primary_model)

        # Initialize explicit fallback models
        if fallback_models:
            for model_identifier in fallback_models:
                self._add_provider(model_identifier)

        # Auto-discovery from registry
        if enable_auto_discovery and LLM_REGISTRY:
            logger.info("Attempting auto-discovery of models from registry...")
            for provider, data in LLM_REGISTRY.items():
                if (
                    provider in PROVIDER_CONFIG
                ):  # Only consider providers we know how to handle
                    for model_name in data.get("models", []):
                        if (provider, model_name) not in self.initialized_models:
                            logger.debug(
                                f"Registry Discovery: Attempting to add {provider}:{model_name}"
                            )
                            # Use explicit provider:model format for clarity
                            self._add_provider(f"{provider}:{model_name}")
                else:
                    logger.debug(
                        f'Skipping registry provider "{provider}": Not in PROVIDER_CONFIG'
                    )

        if not self.model_preference:
            raise ValueError("No valid LLM providers could be initialized.")

        logger.info(
            f"LLM Orchestrator initialized. Final Preference Order: {self.model_preference}"
        )

    def _infer_provider(self, model_name: str) -> str:
        """Infers the provider based on common model name prefixes or registry."""
        model_lower = model_name.lower()
        # Check common prefixes first
        if model_lower.startswith("gpt-"):
            return "openai"
        if model_lower.startswith("deepseek-"):
            return "deepseek"
        if model_lower.startswith("grok-"):
            return "grok"
        if model_lower.startswith("gemini-") or model_lower.startswith("gemma-"):
            return "gemini"
        if (
            model_lower.startswith("mistral-")
            or model_lower.startswith("open-mixtral-")
            or model_lower.startswith("codestral-")
        ):
            return "mistral"
        if model_lower.startswith("claude-"):
            return "anthropic"

        # If no prefix match, check the registry
        for provider, data in LLM_REGISTRY.items():
            if model_name in data.get("models", []):
                logger.debug(
                    f'Inferred provider "{provider}" for model "{model_name}" from registry.'
                )
                return provider

        logger.warning(
            f'Could not infer provider for "{model_name}". Specify provider if ambiguous (e.g., "openai:gpt-3.5-turbo"). Defaulting to openai.'
        )
        return "openai"

    def _add_provider(self, model_identifier: str):
        """Adds a provider/model to the orchestrator if valid and configured."""
        if ":" in model_identifier:
            provider, model_name = model_identifier.split(":", 1)
            provider = provider.lower()
        else:
            model_name = model_identifier
            provider = self._infer_provider(model_name)

        # Check if already processed this specific provider/model combination
        if (provider, model_name) in self.initialized_models:
            logger.debug(f"Skipping already initialized model: {provider}:{model_name}")
            return

        if provider not in PROVIDER_CONFIG:
            logger.warning(f"Skipping unsupported provider: {provider}")
            self.initialized_models.add(
                (provider, model_name)
            )  # Mark as processed even if skipped
            return

        provider_info = PROVIDER_CONFIG[provider]
        if not provider_info["library_present"]:
            logger.warning(
                f"Skipping provider {provider} model {model_name}: Required library not installed."
            )
            self.initialized_models.add((provider, model_name))
            return

        api_key = get_env_var(provider_info["api_key_env"])
        if not api_key:
            logger.warning(
                f"Skipping provider {provider} model {model_name}: API key ({provider_info['api_key_env']}) not found in environment."
            )
            self.initialized_models.add((provider, model_name))
            return

        # Use a unique key for the providers dictionary, e.g., provider:model_name
        provider_key = f"{provider}:{model_name}"
        if provider_key not in self.providers:
            try:
                instance = LLMProviderInstance(
                    provider, model_name, api_key, self.config
                )
                self.providers[provider_key] = instance
                self.model_preference.append((provider, model_name))
                self.initialized_models.add((provider, model_name))
                logger.info(
                    f"Successfully added provider: {provider}, model: {model_name}"
                )
            except (ImportError, ValueError, LLMOrchestratorError) as e:
                logger.error(
                    f"Failed to initialize provider {provider} model {model_name}: {e}"
                )
                self.initialized_models.add(
                    (provider, model_name)
                )  # Mark as processed even if failed
        else:
            # Should not happen with the initialized_models check, but log if it does
            logger.debug(
                f"Provider key {provider_key} already exists in self.providers, but was not in initialized_models. Adding to preference list."
            )
            if (provider, model_name) not in self.model_preference:
                self.model_preference.append((provider, model_name))
            self.initialized_models.add((provider, model_name))

    async def _call_provider_with_retry(
        self,
        provider_instance: LLMProviderInstance,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Internal method to call a specific LLM provider API with retry logic."""
        retries = 0
        delay = self.initial_delay
        last_exception = None
        provider = provider_instance.provider
        model_name = provider_instance.model_name
        client = provider_instance.client

        while retries < self.max_retries_per_provider:
            try:
                logger.debug(
                    f"Attempt {retries + 1}/{self.max_retries_per_provider} calling {provider} model {model_name}"
                )

                if provider in ["openai", "deepseek", "grok"]:
                    if not AsyncOpenAI:
                        raise ImportError("OpenAI library required.")
                    response = await client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens,
                        temperature=temperature,
                        n=1,
                        stop=None,
                    )
                    content = (
                        response.choices[0].message.content
                        if response.choices and response.choices[0].message
                        else None
                    )
                    if content is None:
                        raise LLMOrchestratorError(
                            f"{provider} ({model_name}) returned empty content."
                        )
                    return content.strip()

                elif provider == "gemini":
                    if not genai:
                        raise ImportError("Gemini library required.")
                    # Ensure safety settings are applied if needed
                    safety_settings = self.config.get(
                        "gemini_safety_settings", DEFAULT_GEMINI_SAFETY_SETTINGS
                    )
                    generation_config = genai.types.GenerationConfig(
                        max_output_tokens=max_tokens, temperature=temperature
                    )
                    response = await client.generate_content_async(
                        prompt,
                        generation_config=generation_config,
                        safety_settings=safety_settings,
                    )
                    # Handle potential blocks
                    if not response.candidates:
                        block_reason = response.prompt_feedback.block_reason.name
                        raise LLMOrchestratorError(
                            f"Gemini ({model_name}) call blocked due to: {block_reason}"
                        )
                    return response.text.strip()

                elif provider == "mistral":
                    if not MistralAsyncClient or not ChatMessage:
                        raise ImportError("MistralAI library required.")
                    messages = [ChatMessage(role="user", content=prompt)]
                    response = await client.chat(
                        model=model_name,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    content = (
                        response.choices[0].message.content
                        if response.choices and response.choices[0].message
                        else None
                    )
                    if content is None:
                        raise LLMOrchestratorError(
                            f"Mistral ({model_name}) returned empty content."
                        )
                    return content.strip()

                elif provider == "anthropic":
                    if not AsyncAnthropic:
                        raise ImportError("Anthropic library required.")
                    response = await client.messages.create(
                        model=model_name,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    content = (
                        response.content[0].text if response.content else None
                    )  # Assuming text content
                    if content is None:
                        raise LLMOrchestratorError(
                            f"Anthropic ({model_name}) returned empty content."
                        )
                    return content.strip()

                else:
                    raise LLMOrchestratorError(f"Unsupported provider: {provider}")

            except (RateLimitError, AnthropicRateLimitError) as e:
                last_exception = e
                logger.warning(
                    f"Rate limit exceeded for {provider} ({model_name}). Retrying in {delay:.2f}s... ({retries + 1}/{self.max_retries_per_provider})"
                )
            except (APIError, AnthropicAPIError) as e:
                last_exception = e
                logger.warning(
                    f"API error from {provider} ({model_name}): {e}. Retrying in {delay:.2f}s... ({retries + 1}/{self.max_retries_per_provider})"
                )
            except ImportError as e:
                logger.error(f"Missing library for {provider}: {e}")
                raise LLMOrchestratorError(f"Missing library for {provider}: {e}")
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Unexpected error calling {provider} ({model_name}): {e}. Retrying in {delay:.2f}s... ({retries + 1}/{self.max_retries_per_provider})"
                )

            retries += 1
            await asyncio.sleep(delay)
            delay *= 2  # Exponential backoff

        # If loop finishes without success
        error_message = f"Failed to get response from {provider} ({model_name}) after {self.max_retries_per_provider} retries."
        if last_exception:
            error_message += f" Last error: {last_exception}"
        logger.error(error_message)
        raise LLMOrchestratorError(error_message)

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.7,
        target_model: Optional[str] = None,  # Allow targeting a specific model
    ) -> str:
        """
        Generates text using the configured LLM providers with fallback and retry logic.

        Args:
            prompt: The input prompt for the LLM.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            target_model: (Optional) Specific model identifier (e.g., "gemini:gemini-pro") to use.
                          If provided, only this model will be attempted (with retries).
                          If None, uses the primary/fallback preference order.

        Returns:
            The generated text as a string.

        Raises:
            LLMOrchestratorError: If all providers fail after retries.
        """
        models_to_try = []
        if target_model:
            # Validate and find the target model instance
            if ":" in target_model:
                provider, model_name = target_model.split(":", 1)
                provider = provider.lower()
            else:
                model_name = target_model
                provider = self._infer_provider(model_name)

            provider_key = f"{provider}:{model_name}"
            if provider_key in self.providers:
                models_to_try.append((provider, model_name))
                logger.info(f"Targeting specific model: {provider_key}")
            else:
                raise ValueError(
                    f'Target model "{target_model}" not found or not initialized in the orchestrator.'
                )
        else:
            # Use the established preference order
            models_to_try = self.model_preference

        last_exception = None
        primary_provider, primary_model_name = self.model_preference[0]
        primary_key = f"{primary_provider}:{primary_model_name}"

        for provider, model_name in models_to_try:
            provider_key = f"{provider}:{model_name}"
            provider_instance = self.providers.get(provider_key)

            if not provider_instance:
                logger.warning(
                    f"Skipping {provider_key}: Instance not found (should not happen if initialization was correct)."
                )
                continue

            try:
                # Notify if falling back from primary
                if (
                    provider_key != primary_key
                    and not target_model
                    and self.enable_fallback_notifications
                ):
                    fallback_message = f"⚠️ LLM Fallback Triggered! ⚠️\nPrimary ({primary_key}) failed. Falling back to {provider_key}.\nLast error: {last_exception}"
                    logger.warning(fallback_message)
                    try:
                        await send_notification(fallback_message)
                    except Exception as notify_err:
                        logger.error(
                            f"Failed to send fallback notification: {notify_err}"
                        )

                logger.info(f"Attempting generation with: {provider_key}")
                result = await self._call_provider_with_retry(
                    provider_instance, prompt, max_tokens, temperature
                )
                logger.info(f"Successfully generated text using {provider_key}.")
                return result
            except LLMOrchestratorError as e:
                last_exception = e
                logger.error(f"Provider {provider_key} failed: {e}")
                # Continue to the next provider in the list
                continue
            except Exception as e:
                # Catch unexpected errors during the orchestration loop
                last_exception = e
                logger.error(
                    f"Unexpected error during orchestration with {provider_key}: {e}",
                    exc_info=True,
                )
                continue

        # If loop finishes without success
        final_error_message = (
            "All configured LLM providers failed to generate text after retries."
        )
        if last_exception:
            final_error_message += f" Last error: {last_exception}"
        logger.critical(final_error_message)
        # Send critical failure notification
        if self.enable_fallback_notifications:
            critical_message = f"🚨 CRITICAL LLM FAILURE! 🚨\nAll providers failed ({[f'{p}:{m}' for p, m in models_to_try]}). Cannot generate text.\nLast error: {last_exception}"
            try:
                await send_notification(critical_message)
            except Exception as notify_err:
                logger.error(
                    f"Failed to send critical failure notification: {notify_err}"
                )

        raise LLMOrchestratorError(final_error_message)


# --- Example Usage --- #
async def main():
    # Example: Prioritize DeepSeek, fallback to Gemini, then Mistral
    # Assumes API keys are in .env file
    orchestrator = LLMOrchestrator(
        primary_model="deepseek:deepseek-chat",
        fallback_models=["gemini:gemini-1.5-flash", "mistral:mistral-large-latest"],
        enable_auto_discovery=True,  # Try to find others like Claude if configured
    )

    test_prompt = "Write a short poem about a futuristic city."

    try:
        print(f"\n--- Test 1: Standard Generation (Primary: DeepSeek) ---")
        generated_text = await orchestrator.generate_text(test_prompt, max_tokens=100)
        print(f"Generated Text:\n{generated_text}")
    except LLMOrchestratorError as e:
        print(f"Generation failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    try:
        print(f"\n--- Test 2: Targeting Specific Model (Mistral) ---")
        generated_text = await orchestrator.generate_text(
            test_prompt, max_tokens=100, target_model="mistral:mistral-large-latest"
        )
        print(f"Generated Text (Mistral Target):\n{generated_text}")
    except (LLMOrchestratorError, ValueError) as e:
        print(f"Targeted generation failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Example of simulating failure (requires modifying a client or API key temporarily)
    # print("\n--- Test 3: Simulating Fallback (Requires manual intervention) ---")
    # Temporarily disable primary provider's API key in .env or mock the client to fail
    # try:
    #     generated_text = await orchestrator.generate_text(test_prompt, max_tokens=100)
    #     print(f"Generated Text (Fallback Scenario):\n{generated_text}")
    # except LLMOrchestratorError as e:
    #     print(f"Generation failed after fallback attempts: {e}")


if __name__ == "__main__":
    asyncio.run(main())
