# llm_orchestrator/orchestrator.py Modification

"""
Orchestrator Module - Multi-Provider Support with Fallback & Auto-Discovery

This module provides the core orchestration functionality for LLM interactions,
supporting multiple providers (OpenAI, DeepSeek, Grok, Gemini, Mistral,
Anthropic)
and implementing inter-provider fallback logic.

Includes basic auto-discovery of models listed in llm_registry.py.
"""

import logging
import os
import sys

# Removed unused json
from typing import List, Tuple, Dict, Any, Optional  # Keep used typing imports
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
    load_dotenv(
        dotenv_path=DOTENV_PATH, override=True
    )  # Local can override root

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
        "OpenAI library not found. OpenAI, DeepSeek, Grok functionality "
        "will be limited."
    )

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    from google.api_core import (
        exceptions as google_exceptions,
    )  # Specific exceptions

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
    google_exceptions = None  # Define as None if import fails
    DEFAULT_GEMINI_SAFETY_SETTINGS = {}
    logger.warning(
        "google-generativeai library not found. Gemini functionality "
        "will be limited."
    )

try:
    # Removed unused MistralClient
    from mistralai.async_client import MistralAsyncClient
    from mistralai.models.chat_completion import ChatMessage
    from mistralai.exceptions import (
        MistralAPIException,
    )  # Import the exception
except ImportError:
    MistralAsyncClient = None
    ChatMessage = None
    MistralAPIException = Exception  # Define as generic if import fails
    logger.warning(
        "mistralai library not found. Mistral functionality "
        "will be limited."
    )

try:
    from anthropic import (
        AsyncAnthropic,
        APIError as AnthropicAPIError,  # Keep for exception handling
        RateLimitError as AnthropicRateLimitError,
        # Keep for exception handling
    )
except ImportError:
    AsyncAnthropic = None

    # Define dummy exceptions if library is missing
    class AnthropicAPIError(Exception):
        pass

    class AnthropicRateLimitError(Exception):
        pass

    logger.warning(
        "Anthropic library not found. Claude functionality " "will be limited."
    )

# Import the registry
try:
    from llm_orchestrator.llm_registry import LLM_REGISTRY
except ImportError:
    LLM_REGISTRY = {}
    logger.warning(
        "llm_registry.py not found or LLM_REGISTRY not defined. "
        "Auto-discovery disabled."
    )

# Import Telegram Service for notifications
try:
    from services.telegram_service import send_notification
except ImportError:
    logger.warning(
        "Telegram service not found, fallback notifications disabled."
    )

    async def send_notification(message: str):
        logger.debug(
            f"Telegram notification skipped (service unavailable): {message}"
        )
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
    "suno": {  # Added Suno entry for BAS stub
        "api_key_env": "SUNO_API_KEY",  # Placeholder, not strictly needed for stub
        "base_url": None,
        "client_class": None,  # No client class for BAS stub
        "library_present": True,  # Assume BAS capability is always present
    },
}


# --- Helper Function to Get Env Var ---
def get_env_var(key: str) -> Optional[str]:
    return os.environ.get(key)


# --- LLM Orchestrator --- #
class OrchestratorError(Exception):
    """Custom exception for LLM Orchestrator errors."""

    pass


class ConfigurationError(OrchestratorError):
    """Custom exception for configuration errors (e.g., missing API keys)."""

    pass


class BASFallbackError(OrchestratorError):
    """Custom exception for errors during BAS fallback execution."""

    pass


class LLMProviderInstance:
    """Holds the initialized client and config
    for a specific provider/model."""

    def __init__(
        self,
        provider: str,
        model_name: str,
        api_key: str,
        config: Dict[str, Any],
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
            raise OrchestratorError(
                f"Client class not defined or library missing for "
                f"{self.provider}"
            )


class LLMOrchestrator:
    """
    Orchestrates interactions with multiple LLM providers.
    Supports a primary model, a list of fallback models,
    and auto-discovery from registry.
    Handles API key loading, client initialization, and API calls
    with retries and inter-provider fallback.
    Includes Telegram notifications for fallback events.
    """

    def __init__(
        self,
        primary_model: str,  # e.g., "deepseek:deepseek-chat"
        fallback_models: Optional[List[str]] = None,
        # e.g., ["gemini-pro", "mistral-large-latest"]
        config: Optional[Dict[str, Any]] = None,
        enable_auto_discovery: bool = True,
        # Flag to enable/disable discovery
        enable_fallback_notifications: bool = True,
        # Flag to enable/disable Telegram notifications
    ):
        """
        Initialize the orchestrator with primary, fallback,
        and potentially discovered models.

        Args:
            primary_model: The preferred model to use first
            # (e.g., "deepseek:deepseek-chat").
            fallback_models: A list of model names to try in order
            # if the primary fails.
            config: Additional configuration
            # (e.g., temperature, max_retries, initial_delay).
            enable_auto_discovery: If True, attempts to add models
            # from LLM_REGISTRY
                                     that are not already in
                                     primary/fallback.
            enable_fallback_notifications: If True, send Telegram
            # notifications on fallback events.
        """
        self.config = config or {}
        self.max_retries_per_provider = self.config.get("max_retries", 3)
        self.initial_delay = self.config.get("initial_delay", 1.0)
        self.enable_fallback_notifications = enable_fallback_notifications

        self.providers: Dict[str, LLMProviderInstance] = {}
        self.model_preference: List[Tuple[str, str]] = (
            []
        )  # List of (provider, model_name)
        self.initialized_models = (
            set()
        )  # Keep track of (provider, model) tuples added

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
                if provider in PROVIDER_CONFIG:
                    # Only consider providers we know how to handle
                    for model_name in data.get("models", []):
                        if (
                            provider,
                            model_name,
                        ) not in self.initialized_models:
                            logger.debug(
                                f"Registry Discovery: Attempting to add "
                                f"{provider}:{model_name}"
                            )
                            # Use explicit provider:model format for clarity
                            self._add_provider(f"{provider}:{model_name}")
                else:
                    logger.debug(
                        f'Skipping registry provider "{provider}": '
                        f"Not in PROVIDER_CONFIG"
                    )

        if not self.model_preference:
            raise ValueError("No valid LLM providers could be initialized.")

        logger.info(
            f"LLM Orchestrator initialized. "
            f"Final Preference Order: {self.model_preference}"
        )

    def _infer_provider(self, model_name: str) -> str:
        """Infers the provider based on common model name prefixes
        or registry."""
        model_lower = model_name.lower()
        # Check common prefixes first
        if model_lower.startswith("gpt-"):
            return "openai"
        if model_lower.startswith("deepseek-"):
            return "deepseek"
        if model_lower.startswith("grok-"):
            return "grok"
        if model_lower.startswith("gemini-") or model_lower.startswith(
            "gemma-"
        ):
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
                    f'Inferred provider "{provider}" for model '
                    f'"{model_name}" from registry.'
                )
                return provider

        logger.warning(
            f'Could not infer provider for "{model_name}". '
            f'Specify provider if ambiguous (e.g., "openai:gpt-3.5-turbo"). '
            f"Defaulting to openai."
        )
        return "openai"

    def _add_provider(self, model_identifier: str):
        """Adds a provider/model to the orchestrator if valid
        and configured."""
        if ":" in model_identifier:
            provider, model_name = model_identifier.split(":", 1)
            provider = provider.lower()
        else:
            model_name = model_identifier
            provider = self._infer_provider(model_name)

        # Check if already processed this specific provider/model combination
        if (provider, model_name) in self.initialized_models:
            logger.debug(
                f"Skipping already initialized model: {provider}:{model_name}"
            )
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
                f"Skipping provider {provider} model {model_name}: "
                f"Required library not installed."
            )
            self.initialized_models.add((provider, model_name))
            return

        api_key_env_var = provider_info["api_key_env"]  # Extract to variable
        api_key = get_env_var(api_key_env_var)
        if not api_key:
            logger.warning(
                f"Skipping provider {provider} model {model_name}: "
                f"API key ({api_key_env_var}) not found in environment."
            )  # Use variable here
            self.initialized_models.add((provider, model_name))
            return

        # Special handling for Suno BAS stub
        if provider == "suno":
            logger.info(f"Registering Suno BAS stub: {provider}:{model_name}")
            # No client instance needed, just add to preference and initialized set
            if (provider, model_name) not in self.initialized_models:
                self.model_preference.append((provider, model_name))
                self.initialized_models.add((provider, model_name))
            return  # Skip LLMProviderInstance creation for suno

        # Use a unique key for the providers dictionary, e.g.,
        # provider:model_name
        provider_key = f"{provider}:{model_name}"
        if provider_key not in self.providers:
            try:
                instance = LLMProviderInstance(
                    provider, model_name, api_key, self.config
                )
                self.providers[provider_key] = instance
                self.model_preference.append((provider, model_name))
                model_tuple = (provider, model_name)
                self.initialized_models.add(model_tuple)
                logger.info(
                    f"Successfully added provider: {provider}, "
                    f"model: {model_name}"
                )
            except (ImportError, ValueError, OrchestratorError) as e:
                logger.error(
                    "Failed to initialize provider %s model %s: %s",
                    provider,
                    model_name,
                    e,
                )
                self.initialized_models.add(
                    (provider, model_name)
                )  # Mark as processed even if failed
        else:
            # Should not happen with the initialized_models check, but log if
            # it does
            logger.debug(
                f"Provider key {provider_key} already exists in "
                f"self.providers, but was not in initialized_models. "
                f"Adding to preference list."
            )
            model_tuple = (provider, model_name)
            if model_tuple not in self.model_preference:
                self.model_preference.append(model_tuple)
            self.initialized_models.add(model_tuple)

    async def _call_provider_with_retry(
        self,
        provider_instance: LLMProviderInstance,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Internal method to call a specific LLM provider API
        with retry logic."""
        retries = 0
        delay = self.initial_delay
        last_exception = None  # Initialize last_exception here
        provider = provider_instance.provider
        model_name = provider_instance.model_name
        client = provider_instance.client

        while retries < self.max_retries_per_provider:
            try:
                logger.debug(
                    f"Attempt {retries + 1}/{self.max_retries_per_provider} "
                    f"calling {provider} model {model_name}"
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
                    content = None
                    if response.choices and response.choices[0].message:
                        content = response.choices[0].message.content
                    if content is None:
                        raise OrchestratorError(
                            "%s (%s) returned empty content."
                            % (provider, model_name)
                        )
                    return content.strip()

                elif provider == "gemini":
                    if not genai:
                        raise ImportError("Gemini library required.")
                    # Gemini uses generate_content_async
                    response = await client.generate_content_async(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            # candidate_count=1, # Default is 1
                            max_output_tokens=max_tokens,
                            temperature=temperature,
                        ),
                        safety_settings=DEFAULT_GEMINI_SAFETY_SETTINGS,
                    )
                    # Handle potential blocks or empty responses
                    if not response.candidates:
                        block_reason = response.prompt_feedback.block_reason
                        raise OrchestratorError(
                            f"Gemini ({model_name}) call blocked. "
                            f"Reason: {block_reason}"
                        )
                    return response.text.strip()
                elif provider == "mistral":
                    if not MistralAsyncClient or not ChatMessage:
                        raise ImportError("Mistral library required.")
                    chat_response = await client.chat(
                        model=model_name,
                        messages=[ChatMessage(role="user", content=prompt)],
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    content = (
                        chat_response.choices[0].message.content
                        if chat_response.choices
                        and chat_response.choices[0].message
                        else None
                    )
                    if content is None:
                        raise OrchestratorError(
                            f"Mistral ({model_name}) returned empty content."
                        )
                    return content.strip()

                elif provider == "anthropic":
                    if not AsyncAnthropic:
                        raise ImportError("Anthropic library required.")
                    message = await client.messages.create(
                        model=model_name,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    content = (
                        message.content[0].text if message.content else None
                    )
                    if content is None:
                        raise OrchestratorError(
                            f"Anthropic ({model_name}) returned empty content."
                        )
                    return content.strip()

                else:
                    # Should not happen if _add_provider worked correctly
                    raise OrchestratorError(
                        f"Unsupported provider: {provider}"
                    )

            except (
                APIError,  # OpenAI/DeepSeek/Grok specific
                RateLimitError,  # OpenAI/DeepSeek/Grok specific
                AnthropicAPIError,  # Anthropic specific
                AnthropicRateLimitError,  # Anthropic specific
            ) as e:
                last_exception = e
                retries += 1
                logger.warning(
                    f"API error calling {provider} ({model_name}): {e}. "
                    f"Retrying in {delay}s... "
                    f"({retries}/{self.max_retries_per_provider})"
                )
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            except ImportError as e:
                last_exception = e
                logger.error(
                    f"Import error during API call for {provider} "
                    f"({model_name}): {e}"
                )
                break  # Don't retry import errors
            except Exception as e:
                last_exception = e
                retries += 1
                logger.error(
                    f"Unexpected error calling {provider} "
                    f"({model_name}): {e}. "
                    f"Retrying in {delay}s... "
                    f"({retries}/{self.max_retries_per_provider})",
                    exc_info=True,
                )
                await asyncio.sleep(delay)
                delay *= 2

        # If loop finishes without returning, raise the last exception
        raise OrchestratorError(
            f"Failed to call {provider} ({model_name}) after "
            f"{self.max_retries_per_provider} retries."
        ) from last_exception

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """
        Generates text using the configured LLM providers, with fallback.

        Args:
            prompt: The input prompt.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.

        Returns:
            The generated text.

        Raises:
            OrchestratorError: If all providers fail after retries.
        """
        last_exception = None
        for i, (provider, model_name) in enumerate(self.model_preference):
            if provider == "suno":
                # Special handling for Suno BAS stub
                logger.info(
                    f"Attempting fallback to Suno BAS stub ({provider}:{model_name})..."
                )
                try:
                    result = await self._call_bas_suno_stub(prompt)
                    logger.info(f"Suno BAS stub fallback successful.")
                    return result
                except BASFallbackError as bas_err:
                    logger.error(f"Suno BAS stub fallback failed: {bas_err}")
                    last_error = bas_err
                    continue  # Try next provider
                except Exception as e:
                    logger.error(
                        f"Unexpected error during Suno BAS stub fallback: {e}"
                    )
                    last_error = e
                    continue  # Try next provider

            provider_key = f"{provider}:{model_name}"
            if provider_key not in self.providers:
                logger.warning(
                    f"Skipping {provider}:{model_name} in preference list: Not initialized."
                )
                continue

            provider_instance = self.providers[provider_key]
            try:
                logger.info(
                    f"Attempting generation with: {provider}:{model_name}"
                )
                result = await self._call_provider_with_retry(
                    provider_instance, prompt, max_tokens, temperature
                )
                logger.info(
                    f"Successfully generated text using "
                    f"{provider}:{model_name}"
                )
                return result
            except Exception as e:
                last_exception = e
                logger.error(
                    f"Failed to generate text with {provider}:{model_name}: "
                    f"{e}",
                    exc_info=False,  # Avoid verbose logs during fallback
                )
                # Send notification only when falling back from non-last
                # provider
                if (
                    self.enable_fallback_notifications
                    and i < len(self.model_preference) - 1
                ):
                    fallback_to_provider, fallback_to_model = (
                        self.model_preference[i + 1]
                    )
                    notification_msg = (
                        f"🚨 LLM Fallback Triggered! 🚨\n\n"
                        f"Failed Provider: `{provider}`\n"
                        f"Failed Model: `{model_name}`\n"
                        f"Error: `{str(e)[:200]}...`\n\n"
                        f"Attempting fallback to: "
                        f"`{fallback_to_provider}:{fallback_to_model}`"
                    )
                    await send_notification(notification_msg)

        # If loop completes without returning, all providers failed
        final_error_msg = (
            "All configured LLM providers failed to generate text."
        )
        logger.critical(final_error_msg)
        await send_notification(
            f"🆘 Critical LLM Failure! 🆘\n\n{final_error_msg}\n"
            f"Last Error: `{str(last_exception)[:200]}...`"
        )
        raise OrchestratorError(final_error_msg) from last_exception


# --- Example Usage --- #
async def main():
    """Example usage of the LLMOrchestrator."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting LLM Orchestrator example...")

    # --- Configuration --- #
    # Define your primary and fallback models (use provider:model format or
    # just model name)
    # Ensure corresponding API keys are in your .env file
    # Example: Prioritize DeepSeek, fallback to Gemini, then Mistral, then
    # GPT-4o
    primary = "deepseek:deepseek-chat"
    fallbacks = [
        "gemini:gemini-1.5-pro-latest",
        "mistral:mistral-large-latest",
        "openai:gpt-4o",
    ]

    try:
        orchestrator = LLMOrchestrator(
            primary_model=primary,
            fallback_models=fallbacks,
            enable_auto_discovery=True,
            # Try to add other configured models
            enable_fallback_notifications=True,  # Enable Telegram alerts
            config={
                "max_retries": 2,
                # Max retries per provider before falling back
                "initial_delay": 0.5,
            },
        )

        prompt = (
            "Write a short story about a robot who learns to paint sunsets."
        )
        logger.info(f'Generating text for prompt: "{prompt[:50]}..."')

        generated_text = await orchestrator.generate_text(
            prompt, max_tokens=150, temperature=0.8
        )

        logger.info("--- Generated Text ---")
        print(generated_text)
        logger.info("----------------------")

    except ValueError as e:
        logger.error(f"Initialization Error: {e}")
    except OrchestratorError as e:
        logger.error(f"Orchestration Failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    # Check for API keys before running example
    required_keys = [
        PROVIDER_CONFIG[p]["api_key_env"]
        for p in PROVIDER_CONFIG
        if PROVIDER_CONFIG[p]["library_present"]
    ]
    missing_keys = [key for key in required_keys if not get_env_var(key)]

    if missing_keys:
        print("\n--- Missing API Keys ---")
        print(
            "Please set the following environment variables "
            "(e.g., in a .env file):"
        )
        for key in missing_keys:
            print(f"- {key}")
        print("Example cannot run without required API keys.")
    else:
        print("\n--- Running LLM Orchestrator Example ---")
        asyncio.run(main())
