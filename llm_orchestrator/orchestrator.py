# llm_orchestrator/orchestrator.py Modification

"""
Orchestrator Module - Multi-Provider Support with Fallback & Auto-Discovery

This module provides the core orchestration functionality for LLM interactions,
supporting multiple providers (OpenAI, DeepSeek, Grok, Gemini, Mistral,
Anthropic)
and implementing inter-provider fallback logic.

Includes basic auto-discovery of models listed in llm_registry.py.
Also includes integration with the Suno BAS module for music generation.
"""

import logging
import os
import sys
import asyncio
from typing import List, Tuple, Dict, Any, Optional, Union
from dotenv import load_dotenv

# --- Load Environment Variables ---
PROJECT_ROOT_DOTENV = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(PROJECT_ROOT_DOTENV):
    load_dotenv(dotenv_path=PROJECT_ROOT_DOTENV, override=False)
DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH, override=True)

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# --- Configure logging ---
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Import LLM Provider Libraries (with error handling) ---
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
    from google.api_core import exceptions as google_exceptions

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
    google_exceptions = None
    DEFAULT_GEMINI_SAFETY_SETTINGS = {}
    logger.warning(
        "google-generativeai library not found. Gemini functionality will be limited."
    )

try:
    from mistralai.async_client import MistralAsyncClient
    from mistralai.models.chat_completion import ChatMessage
    from mistralai.exceptions import MistralAPIException
except ImportError:
    MistralAsyncClient = None
    ChatMessage = None
    MistralAPIException = Exception
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

    class AnthropicAPIError(Exception):
        pass

    class AnthropicRateLimitError(Exception):
        pass

    logger.warning(
        "Anthropic library not found. Claude functionality will be limited."
    )

# --- Import Local Modules ---
try:
    from llm_orchestrator.llm_registry import LLM_REGISTRY
except ImportError:
    LLM_REGISTRY = {}
    logger.warning(
        "llm_registry.py not found or LLM_REGISTRY not defined. Auto-discovery disabled."
    )

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
        await asyncio.sleep(0)


# --- Import Suno BAS Module Components ---
try:
    from modules.suno.suno_orchestrator import (
        SunoOrchestrator,
        SunoOrchestratorError,
    )
    from schemas.song_metadata import SongMetadata

    # Assume a default config path or mechanism for Suno Orchestrator
    DEFAULT_SUNO_CONFIG_PATH = os.path.join(
        PROJECT_ROOT, "config", "suno_config.json"
    )
    # TODO: Load this config properly later
    DEFAULT_SUNO_CONFIG = {
        "state_dir": os.path.join(
            PROJECT_ROOT, "modules", "suno", "suno_run_states"
        ),
        "log_dir": os.path.join(
            PROJECT_ROOT, "modules", "suno", "suno_run_logs"
        ),
        "screenshot_dir": os.path.join(
            PROJECT_ROOT, "modules", "suno", "suno_validation_screenshots"
        ),
        "max_retries": 3,
        "retry_delay": 5,
        "llm_validator_config": {"api_key": "dummy", "model": "validator"},
    }
    suno_bas_available = True
except ImportError as e:
    SunoOrchestrator = None
    SunoOrchestratorError = Exception
    SongMetadata = None
    DEFAULT_SUNO_CONFIG = {}
    suno_bas_available = False
    logger.warning(
        f"Suno BAS module components not found or import error: {e}. Suno generation disabled."
    )


# --- Provider Configuration --- #
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
    "suno": {  # Added Suno entry for BAS integration
        "api_key_env": None,  # No API key needed for BAS
        "base_url": None,
        "client_class": SunoOrchestrator,  # Reference the orchestrator class
        "library_present": suno_bas_available,
    },
}


# --- Helper Function to Get Env Var ---
def get_env_var(key: str) -> Optional[str]:
    return os.environ.get(key)


# --- LLM Orchestrator Exceptions ---
class OrchestratorError(Exception):
    """Custom exception for LLM Orchestrator errors."""

    pass


class ConfigurationError(OrchestratorError):
    """Custom exception for configuration errors (e.g., missing API keys)."""

    pass


class BASFallbackError(OrchestratorError):
    """Custom exception for errors during BAS fallback execution."""

    pass


# --- LLM Provider Instance Wrapper ---
class LLMProviderInstance:
    """Holds the initialized client and config for a specific provider/model."""

    def __init__(
        self,
        provider: str,
        model_name: str,
        api_key: Optional[str],
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
            if not genai or not self.api_key:
                raise ConfigurationError("Gemini library or API key missing.")
            genai.configure(api_key=self.api_key)
            return genai.GenerativeModel(self.model_name)
        elif self.provider == "suno":
            if (
                not client_class
            ):  # Check if SunoOrchestrator class is available
                raise ConfigurationError("Suno BAS module not available.")
            # Initialize Suno Orchestrator with its specific config
            # TODO: Load config from file or pass dynamically
            return client_class(config=DEFAULT_SUNO_CONFIG)
        elif client_class:
            if not self.api_key:
                raise ConfigurationError(
                    f"API key missing for {self.provider}."
                )
            client_args = {"api_key": self.api_key}
            if base_url:
                client_args["base_url"] = base_url
            return client_class(**client_args)
        else:
            raise OrchestratorError(
                f"Client class not defined or library missing for {self.provider}"
            )


# --- Main LLM Orchestrator Class ---
class LLMOrchestrator:
    """
    Orchestrates interactions with multiple LLM providers and Suno BAS.
    Supports a primary model, fallback models, and auto-discovery.
    Handles API key loading, client initialization, and API calls with retries.
    Includes Telegram notifications for fallback events.
    """

    def __init__(
        self,
        primary_model: str,  # e.g., "deepseek:deepseek-chat" or "suno:v3"
        fallback_models: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        enable_auto_discovery: bool = True,
        enable_fallback_notifications: bool = True,
    ):
        self.config = config or {}
        self.max_retries_per_provider = self.config.get("max_retries", 3)
        self.initial_delay = self.config.get("initial_delay", 1.0)
        self.enable_fallback_notifications = enable_fallback_notifications

        self.providers: Dict[str, LLMProviderInstance] = {}
        self.model_preference: List[Tuple[str, str]] = []
        self.initialized_models = set()

        # Initialize primary model
        self._add_provider(primary_model)

        # Initialize explicit fallback models
        if fallback_models:
            for model_identifier in fallback_models:
                self._add_provider(model_identifier)

        # Auto-discovery from registry (excluding suno)
        if enable_auto_discovery and LLM_REGISTRY:
            logger.info("Attempting auto-discovery of models from registry...")
            for provider, data in LLM_REGISTRY.items():
                if (
                    provider in PROVIDER_CONFIG and provider != "suno"
                ):  # Exclude suno from registry discovery
                    for model_name in data.get("models", []):
                        if (
                            provider,
                            model_name,
                        ) not in self.initialized_models:
                            logger.debug(
                                f"Registry Discovery: Attempting to add {provider}:{model_name}"
                            )
                            self._add_provider(f"{provider}:{model_name}")
                else:
                    logger.debug(
                        f'Skipping registry provider "{provider}": Not in PROVIDER_CONFIG or is Suno'
                    )

        if not self.model_preference:
            raise ValueError(
                "No valid LLM or BAS providers could be initialized."
            )

        logger.info(
            f"LLM Orchestrator initialized. Final Preference Order: {self.model_preference}"
        )

    def _infer_provider(self, model_name: str) -> str:
        """Infers the provider based on common model name prefixes or registry."""
        model_lower = model_name.lower()
        # Check specific keywords first
        if "suno" in model_lower or model_lower in [
            "v3",
            "v4",
            "v4.5",
        ]:  # Basic Suno check
            return "suno"
        # Check common prefixes
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

        # Check registry (excluding suno)
        for provider, data in LLM_REGISTRY.items():
            if provider != "suno" and model_name in data.get("models", []):
                logger.debug(
                    f'Inferred provider "{provider}" for model "{model_name}" from registry.'
                )
                return provider

        logger.warning(
            f'Could not infer provider for "{model_name}". Specify provider (e.g., "openai:gpt-3.5-turbo"). Defaulting to openai.'
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

        if (provider, model_name) in self.initialized_models:
            logger.debug(
                f"Skipping already initialized model: {provider}:{model_name}"
            )
            return

        if provider not in PROVIDER_CONFIG:
            logger.warning(f"Skipping unsupported provider: {provider}")
            self.initialized_models.add((provider, model_name))
            return

        provider_info = PROVIDER_CONFIG[provider]
        if not provider_info["library_present"]:
            logger.warning(
                f"Skipping provider {provider} model {model_name}: Required library/module not available."
            )
            self.initialized_models.add((provider, model_name))
            return

        api_key = None
        if provider_info["api_key_env"]:
            api_key = get_env_var(provider_info["api_key_env"])
            if (
                not api_key and provider != "suno"
            ):  # Suno doesn't need an API key here
                logger.warning(
                    f"Skipping provider {provider} model {model_name}: API key ({provider_info['api_key_env']}) not found."
                )
                self.initialized_models.add((provider, model_name))
                return
        elif provider != "suno":
            logger.warning(
                f"API key environment variable not defined for provider {provider} in PROVIDER_CONFIG."
            )
            # Decide if this should prevent adding the provider or just be a warning

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
            except ConfigurationError as e:
                logger.warning(
                    f"Configuration error adding {provider}:{model_name}: {e}"
                )
                self.initialized_models.add(
                    (provider, model_name)
                )  # Mark as processed even if failed
            except ImportError as e:
                logger.warning(
                    f"Import error adding {provider}:{model_name}: {e}"
                )
                self.initialized_models.add((provider, model_name))
            except Exception as e:
                logger.error(
                    f"Unexpected error initializing {provider}:{model_name}: {e}",
                    exc_info=True,
                )
                self.initialized_models.add((provider, model_name))

    async def generate_text_async(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        suno_generation_prompt: Optional[
            Dict[str, Any]
        ] = None,  # Specific prompt for Suno
    ) -> Union[
        str, SongMetadata, None
    ]:  # Return type can be string or SongMetadata
        """
        Generates text using the preferred model, falling back to others on failure.
        Also handles Suno BAS generation if a Suno model is selected.

        Args:
            prompt: The user prompt (for simpler, non-chat models).
            messages: A list of message dictionaries (e.g., [{'role': 'user', 'content': '...'}]).
            system_prompt: An optional system message to guide the model.
            generation_params: Optional dictionary for provider-specific parameters
                               (e.g., temperature, max_tokens).
            suno_generation_prompt: Specific dictionary for Suno BAS generation task.

        Returns:
            The generated text as a string, a SongMetadata object for Suno success,
            or None if all providers fail.
        """
        if not messages and prompt:
            messages = [{"role": "user", "content": prompt}]
        elif not messages:
            raise ValueError(
                "Either 'prompt' or 'messages' must be provided for LLM generation."
            )

        merged_params = {
            **self.config,
            **(generation_params or {}),
        }  # Merge global and local params

        last_error = None

        for provider, model_name in self.model_preference:
            provider_key = f"{provider}:{model_name}"
            if provider_key not in self.providers:
                logger.debug(f"Skipping {provider_key}: Not initialized.")
                continue

            instance = self.providers[provider_key]
            logger.info(f"Attempting generation with: {provider}:{model_name}")

            # --- Suno BAS Handling ---
            if provider == "suno":
                if not suno_generation_prompt:
                    logger.warning(
                        f"Skipping Suno ({model_name}): Missing 'suno_generation_prompt'."
                    )
                    last_error = OrchestratorError(
                        "Missing 'suno_generation_prompt' for Suno task."
                    )
                    continue
                if not isinstance(instance.client, SunoOrchestrator):
                    logger.error(
                        f"Suno provider instance is not a SunoOrchestrator: {type(instance.client)}"
                    )
                    last_error = OrchestratorError(
                        "Internal configuration error for Suno BAS."
                    )
                    continue

                suno_orchestrator: SunoOrchestrator = instance.client
                current_delay = self.initial_delay
                for attempt in range(self.max_retries_per_provider):
                    try:
                        # Ensure run_id is present or generated
                        if "run_id" not in suno_generation_prompt:
                            suno_generation_prompt["run_id"] = (
                                f"suno_run_{os.urandom(4).hex()}"
                            )
                        logger.info(
                            f"Calling Suno BAS generate_song (Run ID: {suno_generation_prompt['run_id']}) - Attempt {attempt + 1}"
                        )
                        song_metadata: SongMetadata = (
                            await suno_orchestrator.generate_song(
                                suno_generation_prompt
                            )
                        )
                        logger.info(
                            f"Suno BAS generation successful for {provider}:{model_name} (Run ID: {suno_generation_prompt['run_id']})"
                        )
                        return song_metadata  # Return the SongMetadata object directly
                    except SunoOrchestratorError as e:
                        last_error = e
                        logger.warning(
                            f"Suno BAS generation failed for {provider}:{model_name} "
                            f"(Attempt {attempt + 1}/{self.max_retries_per_provider}): {e}"
                        )
                        if attempt < self.max_retries_per_provider - 1:
                            logger.info(
                                f"Retrying Suno BAS in {current_delay:.2f} seconds..."
                            )
                            await asyncio.sleep(current_delay)
                            current_delay *= 2  # Exponential backoff
                        else:
                            logger.error(
                                f"Suno BAS failed permanently for {provider}:{model_name} after {self.max_retries_per_provider} attempts."
                            )
                            break  # Exit retry loop for this provider
                    except Exception as e:
                        last_error = e
                        logger.error(
                            f"Unexpected error during Suno BAS call for {provider}:{model_name} "
                            f"(Attempt {attempt + 1}): {e}",
                            exc_info=True,
                        )
                        # Decide if unexpected errors should be retried
                        break  # Exit retry loop for this provider for unexpected errors
                # If Suno BAS failed, continue to the next provider in the preference list
                if (
                    self.enable_fallback_notifications
                    and provider != self.model_preference[0][0]
                ):
                    await send_notification(
                        f"Fallback Alert: Suno BAS ({model_name}) failed. Error: {last_error}"
                    )
                continue  # Move to next provider

            # --- Standard LLM Provider Handling ---
            current_delay = self.initial_delay
            for attempt in range(self.max_retries_per_provider):
                try:
                    logger.debug(
                        f"Calling {provider}:{model_name} (Attempt {attempt + 1}) with params: {merged_params}"
                    )
                    # --- Provider-Specific Call Logic --- #
                    if provider in ["openai", "deepseek", "grok"]:
                        if not isinstance(instance.client, AsyncOpenAI):
                            raise OrchestratorError(
                                f"Incorrect client type for {provider}"
                            )
                        response = await instance.client.chat.completions.create(
                            model=model_name,
                            messages=self._prepare_messages(
                                messages, system_prompt, provider
                            ),
                            temperature=merged_params.get("temperature", 0.7),
                            max_tokens=merged_params.get("max_tokens", 1024),
                            # Add other compatible params from merged_params
                        )
                        result = response.choices[0].message.content

                    elif provider == "gemini":
                        if not genai or not isinstance(
                            instance.client, genai.GenerativeModel
                        ):
                            raise OrchestratorError(
                                f"Incorrect client type for {provider}"
                            )
                        # Gemini uses 'contents' not 'messages'
                        gemini_contents = self._prepare_messages(
                            messages, system_prompt, provider
                        )
                        safety_settings = merged_params.get(
                            "safety_settings", DEFAULT_GEMINI_SAFETY_SETTINGS
                        )
                        generation_config_args = {
                            key: merged_params[key]
                            for key in [
                                "temperature",
                                "top_p",
                                "top_k",
                                "max_output_tokens",
                            ]
                            if key in merged_params
                        }
                        response = (
                            await instance.client.generate_content_async(
                                contents=gemini_contents,
                                generation_config=genai.types.GenerationConfig(
                                    **generation_config_args
                                ),
                                safety_settings=safety_settings,
                            )
                        )
                        # Handle potential blocks
                        if not response.candidates:
                            prompt_feedback = response.prompt_feedback
                            block_reason = (
                                prompt_feedback.block_reason.name
                                if prompt_feedback.block_reason
                                else "Unknown"
                            )
                            safety_ratings = {
                                rating.category.name: rating.probability.name
                                for rating in prompt_feedback.safety_ratings
                            }
                            error_msg = f"Gemini generation blocked. Reason: {block_reason}. Ratings: {safety_ratings}"
                            logger.warning(error_msg)
                            # Raise a specific error or handle appropriately
                            raise OrchestratorError(error_msg)
                        result = response.text

                    elif provider == "mistral":
                        if not isinstance(instance.client, MistralAsyncClient):
                            raise OrchestratorError(
                                f"Incorrect client type for {provider}"
                            )
                        # Mistral expects List[ChatMessage]
                        mistral_messages = self._prepare_messages(
                            messages, system_prompt, provider
                        )
                        response = await instance.client.chat(
                            model=model_name,
                            messages=mistral_messages,
                            temperature=merged_params.get("temperature", 0.7),
                            max_tokens=merged_params.get("max_tokens", 1024),
                            # Add other compatible params
                        )
                        result = response.choices[0].message.content

                    elif provider == "anthropic":
                        if not isinstance(instance.client, AsyncAnthropic):
                            raise OrchestratorError(
                                f"Incorrect client type for {provider}"
                            )
                        # Anthropic has specific message format and requires system prompt separately
                        anthropic_messages = self._prepare_messages(
                            messages, None, provider
                        )  # System prompt handled separately
                        response = await instance.client.messages.create(
                            model=model_name,
                            system=system_prompt if system_prompt else None,
                            messages=anthropic_messages,
                            temperature=merged_params.get("temperature", 0.7),
                            max_tokens=merged_params.get("max_tokens", 1024),
                            # Add other compatible params
                        )
                        result = response.content[0].text

                    else:
                        logger.error(
                            f"Generation logic not implemented for provider: {provider}"
                        )
                        raise NotImplementedError(
                            f"Provider {provider} not implemented"
                        )

                    logger.info(
                        f"Generation successful using {provider}:{model_name}"
                    )
                    return result  # Return the successful result

                # --- Exception Handling for LLM Providers --- #
                except (
                    APIError,
                    RateLimitError,
                    MistralAPIException,
                    AnthropicAPIError,
                    AnthropicRateLimitError,
                ) as e:
                    last_error = e
                    logger.warning(
                        f"API error with {provider}:{model_name} "
                        f"(Attempt {attempt + 1}/{self.max_retries_per_provider}): {e}"
                    )
                    # Check for specific non-retryable errors if needed
                    if (
                        isinstance(e, RateLimitError)
                        or isinstance(e, AnthropicRateLimitError)
                        or (hasattr(e, "status_code") and e.status_code == 429)
                    ):
                        # Apply longer delay for rate limits
                        retry_delay = current_delay * 2
                        logger.info(
                            f"Rate limit hit. Retrying in {retry_delay:.2f} seconds..."
                        )
                        await asyncio.sleep(retry_delay)
                        current_delay *= (
                            1.5  # Slower backoff increase for rate limits
                        )
                    elif attempt < self.max_retries_per_provider - 1:
                        logger.info(
                            f"Retrying in {current_delay:.2f} seconds..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= 2  # Exponential backoff
                    else:
                        logger.error(
                            f"Failed permanently with {provider}:{model_name} after {self.max_retries_per_provider} attempts."
                        )
                        break  # Exit retry loop for this provider
                except google_exceptions.GoogleAPIError as e:
                    last_error = e
                    logger.warning(
                        f"Google API error with {provider}:{model_name} "
                        f"(Attempt {attempt + 1}/{self.max_retries_per_provider}): {e}"
                    )
                    # Add specific handling for Google API errors (e.g., resource exhausted)
                    if isinstance(
                        e, google_exceptions.ResourceExhausted
                    ):  # Example: Rate limit equivalent
                        retry_delay = current_delay * 2
                        logger.info(
                            f"Resource exhausted (rate limit). Retrying in {retry_delay:.2f} seconds..."
                        )
                        await asyncio.sleep(retry_delay)
                        current_delay *= 1.5
                    elif attempt < self.max_retries_per_provider - 1:
                        logger.info(
                            f"Retrying in {current_delay:.2f} seconds..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= 2
                    else:
                        logger.error(
                            f"Failed permanently with {provider}:{model_name} after {self.max_retries_per_provider} attempts."
                        )
                        break
                except OrchestratorError as e:
                    # Catch errors like Gemini blocks or config issues
                    last_error = e
                    logger.error(
                        f"Orchestrator error with {provider}:{model_name}: {e}"
                    )
                    break  # Do not retry orchestrator configuration/blocking errors
                except Exception as e:
                    last_error = e
                    logger.error(
                        f"Unexpected error with {provider}:{model_name} "
                        f"(Attempt {attempt + 1}): {e}",
                        exc_info=True,
                    )
                    break  # Exit retry loop for unexpected errors

            # --- Fallback Notification --- #
            # Notify only if falling back *from* a different provider
            # and if it's not the very first attempt overall.
            if (
                provider != self.model_preference[0][0]
                or attempt == self.max_retries_per_provider
            ):
                # Check if this provider failed and we are moving to the next one
                is_final_failure_for_provider = (
                    attempt == self.max_retries_per_provider - 1
                )
                is_not_last_provider = (
                    provider,
                    model_name,
                ) != self.model_preference[-1]

                if (
                    is_final_failure_for_provider
                    and is_not_last_provider
                    and self.enable_fallback_notifications
                ):
                    await send_notification(
                        f"Fallback Alert: {provider}:{model_name} failed. "
                        f"Trying next provider. Last Error: {last_error}"
                    )

        # --- End of Provider Loop --- #
        logger.error("All LLM providers failed.", exc_info=last_error)
        if self.enable_fallback_notifications:
            await send_notification(
                f"Critical Alert: All LLM providers failed. Last Error: {last_error}"
            )
        return None  # Return None if all attempts failed

    def _prepare_messages(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
        provider: str,
    ) -> List[Union[Dict[str, str], ChatMessage]]:
        """Formats messages according to the specific provider's requirements."""
        # Ensure deep copy if modification is needed, otherwise return as is if compatible
        prepared_messages = [msg.copy() for msg in messages]

        if provider == "gemini":
            # Gemini expects alternating user/model roles, potentially merging consecutive user messages
            # and needs system prompt handled differently (often as first user message or specific param)
            gemini_contents = []
            if system_prompt:
                # Gemini doesn't have a dedicated 'system' role in the main content list
                # Prepend it or handle via specific generation config if available
                # Option 1: Prepend as first 'user' message (common workaround)
                # gemini_contents.append({'role': 'user', 'parts': [{'text': system_prompt}]})
                # Option 2: If model/API supports system instruction parameter, use that instead.
                # For now, let's assume it's handled elsewhere or implicitly.
                pass  # Assume system prompt handled by caller or model config

            current_role = None
            merged_content = ""
            for msg in prepared_messages:
                role = "model" if msg["role"] == "assistant" else "user"
                content = msg["content"]
                if role == current_role:
                    merged_content += (
                        "\n\n" + content
                    )  # Merge consecutive messages of same role
                else:
                    if current_role is not None:
                        gemini_contents.append(
                            {
                                "role": current_role,
                                "parts": [{"text": merged_content}],
                            }
                        )
                    current_role = role
                    merged_content = content
            # Append the last message
            if current_role is not None:
                gemini_contents.append(
                    {"role": current_role, "parts": [{"text": merged_content}]}
                )
            return gemini_contents

        elif provider == "mistral":
            # Mistral uses mistralai.models.chat_completion.ChatMessage objects
            mistral_messages = []
            if system_prompt:
                mistral_messages.append(
                    ChatMessage(role="system", content=system_prompt)
                )
            for msg in prepared_messages:
                mistral_messages.append(
                    ChatMessage(role=msg["role"], content=msg["content"])
                )
            return mistral_messages

        elif provider == "anthropic":
            # Anthropic requires alternating user/assistant roles and no system message in the list
            anthropic_messages = []
            last_role = None
            for msg in prepared_messages:
                # Skip system messages here, handled separately
                if msg["role"] == "system":
                    continue
                # Ensure alternating roles (user must be first if not system)
                if not anthropic_messages and msg["role"] == "assistant":
                    logger.warning(
                        "Anthropic messages should start with 'user' role. Prepending dummy user message."
                    )
                    anthropic_messages.append(
                        {"role": "user", "content": "(Context starts)"}
                    )  # Or handle error
                elif anthropic_messages and msg["role"] == last_role:
                    logger.warning(
                        f"Anthropic messages must alternate roles. Skipping duplicate role '{msg['role']}'."
                    )
                    continue  # Skip message that doesn't alternate

                anthropic_messages.append(msg)
                last_role = msg["role"]
            return anthropic_messages

        else:  # OpenAI, DeepSeek, Grok (standard OpenAI format)
            final_messages = []
            if system_prompt:
                final_messages.append(
                    {"role": "system", "content": system_prompt}
                )
            final_messages.extend(prepared_messages)
            return final_messages


# --- Example Usage --- #
async def main_example():
    logger.info("--- Starting LLM Orchestrator Example --- ")

    # --- Configuration ---
    # Define models - use provider:model_name format for clarity
    # primary = "deepseek:deepseek-chat" # Example primary
    primary = "gemini:gemini-1.5-flash-latest"  # Example primary
    # fallbacks = ["gemini:gemini-1.5-flash-latest", "mistral:mistral-large-latest", "anthropic:claude-3-haiku-20240307"]
    fallbacks = [
        "mistral:mistral-large-latest",
        "anthropic:claude-3-haiku-20240307",
        "suno:v3",
    ]  # Add suno here

    # Orchestrator config
    orchestrator_config = {
        "temperature": 0.6,
        "max_retries": 2,  # Per provider
        "initial_delay": 1.5,
    }

    # --- Initialization ---
    try:
        orchestrator = LLMOrchestrator(
            primary_model=primary,
            fallback_models=fallbacks,
            config=orchestrator_config,
            enable_auto_discovery=True,
            enable_fallback_notifications=False,  # Disable notifications for example
        )
    except ValueError as e:
        logger.error(f"Failed to initialize orchestrator: {e}")
        return
    except Exception as e:
        logger.error(
            f"Unexpected error during initialization: {e}", exc_info=True
        )
        return

    # --- Test Case 1: Standard Text Generation ---
    logger.info("\n--- Test Case 1: Standard Text Generation ---")
    messages_test_1 = [
        {
            "role": "user",
            "content": "Write a short poem about a rainy day in a city.",
        }
    ]
    system_prompt_test_1 = (
        "You are a helpful assistant that writes short, creative poems."
    )
    generation_params_test_1 = {"max_tokens": 150}

    result_1 = await orchestrator.generate_text_async(
        messages=messages_test_1,
        system_prompt=system_prompt_test_1,
        generation_params=generation_params_test_1,
    )

    if isinstance(result_1, str):
        logger.info(f"Test Case 1 Result:\n{result_1}")
    elif result_1 is None:
        logger.error("Test Case 1 Failed: No provider could generate text.")
    else:
        logger.error(
            f"Test Case 1 Failed: Unexpected return type {type(result_1)}"
        )

    # --- Test Case 2: Suno BAS Generation ---
    logger.info("\n--- Test Case 2: Suno BAS Generation (Mocked) ---")
    # Check if Suno is actually in the preference list before attempting
    suno_in_preference = any(
        p == "suno" for p, m in orchestrator.model_preference
    )

    if suno_in_preference and suno_bas_available:
        suno_prompt_test_2 = {
            # "run_id": f"test_suno_from_llm_orch_{os.urandom(3).hex()}", # Optional, will be generated if missing
            "title": "City Rain Blues",
            "lyrics": "Verse 1\nThe city sleeps under the grey\nPuddles reflect the neon fray\nChorus\nRainy day blues, tap on the pane\nWashing the streets, again and again",
            "style": "Lo-fi hip hop, melancholic piano, rain sounds",
            "model": "v3",  # Corresponds to model_name used in preference list
            "persona": "Urban Bard",
            "workspace": "Rainy Vibes",
            "genre": "Lo-fi",
        }
        generation_params_test_2 = (
            {}
        )  # No specific LLM params needed for Suno call

        result_2 = await orchestrator.generate_text_async(
            # messages/prompt not needed if suno_generation_prompt is provided
            suno_generation_prompt=suno_prompt_test_2,
            generation_params=generation_params_test_2,
        )

        if isinstance(result_2, SongMetadata):
            logger.info(
                f"Test Case 2 Result (Suno BAS Success):\n{result_2.model_dump_json(indent=2)}"
            )
        elif result_2 is None:
            logger.error(
                "Test Case 2 Failed: Suno BAS generation failed or no fallback succeeded."
            )
        else:
            logger.error(
                f"Test Case 2 Failed: Unexpected return type {type(result_2)}"
            )
    else:
        logger.warning(
            "Skipping Test Case 2: Suno BAS not available or not configured in preference list."
        )

    logger.info("--- LLM Orchestrator Example Finished --- ")


if __name__ == "__main__":
    # Ensure asyncio event loop is handled correctly
    try:
        asyncio.run(main_example())
    except KeyboardInterrupt:
        logger.info("Example run interrupted by user.")
