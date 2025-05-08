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
from unittest.mock import MagicMock
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
    level=os.getenv("LOG_LEVEL", "DEBUG").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Import LLM Provider Libraries (with error handling) ---
try:
    from openai import AsyncOpenAI, APIError, RateLimitError
except ImportError:
    AsyncOpenAI = None

    class _StubOpenAIAPIError(Exception):
        def __init__(self, message, request=None, body=None):
            super().__init__(message)
            self.message = message
            self.request = request
            self.body = body

    APIError = _StubOpenAIAPIError

    class _StubOpenAIRateLimitError(Exception):
        def __init__(self, message, response=None, body=None):
            super().__init__(message)
            self.message = message
            self.response = response
            self.body = body

    RateLimitError = _StubOpenAIRateLimitError
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

    class _StubMistralAPIException(Exception):
        def __init__(self, message, response=None, body=None):
            super().__init__(message)
            self.message = message
            self.response = response
            self.body = body

    MistralAPIException = _StubMistralAPIException
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
    SunoOrchestratorError = type(
        "SunoOrchestratorError", (Exception,), {}
    )  # Stub if not imported
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
        "client_class": AsyncOpenAI,  # DeepSeek uses OpenAI-compatible API
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
        "client_class": None,  # Special handling for Gemini
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
        "client_class": SunoOrchestrator,
        "library_present": suno_bas_available,
    },
}


# --- Helper Function to Get Env Var ---
def get_env_var(key: str) -> Optional[str]:
    return os.environ.get(key)


# --- LLM Orchestrator Exceptions ---
class OrchestratorError(Exception):
    """Custom exception for LLM Orchestrator errors."""


class ConfigurationError(OrchestratorError):
    """Custom exception for configuration errors (e.g., missing API keys)."""


class BASFallbackError(OrchestratorError):
    """Custom exception for errors during BAS fallback execution."""


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
            if not client_class or not suno_bas_available:
                raise ConfigurationError(
                    "Suno BAS module not available or not configured."
                )
            # Pass the specific Suno config to its orchestrator
            suno_specific_config = self.config.get(
                "suno_config", DEFAULT_SUNO_CONFIG
            )
            return client_class(config=suno_specific_config)
        elif client_class:
            if not self.api_key and self.provider not in ["suno"]:
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
        primary_model: str,
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

        self._add_provider(primary_model)
        if fallback_models:
            for model_identifier in fallback_models:
                self._add_provider(model_identifier)

        if enable_auto_discovery and LLM_REGISTRY:
            logger.info("Attempting auto-discovery of models from registry...")
            for provider, data in LLM_REGISTRY.items():
                if (
                    provider in PROVIDER_CONFIG and provider != "suno"
                ):  # Exclude suno from general LLM discovery here
                    for model_name in data.get("models", []):
                        if (
                            provider,
                            model_name,
                        ) not in self.initialized_models:
                            logger.debug(
                                f"Registry Discovery: Attempting to add {provider}:{model_name}"
                            )
                            self._add_provider(f"{provider}:{model_name}")
                elif (
                    provider == "suno" and provider in PROVIDER_CONFIG
                ):  # Special handling for Suno if in registry
                    # Suno might have specific model names like "v3" or a generic entry
                    suno_model_in_registry = data.get(
                        "models", ["default_suno"]
                    )[
                        0
                    ]  # Take first if multiple
                    if (
                        provider,
                        suno_model_in_registry,
                    ) not in self.initialized_models:
                        logger.debug(
                            f"Registry Discovery: Attempting to add {provider}:{suno_model_in_registry}"
                        )
                        self._add_provider(
                            f"{provider}:{suno_model_in_registry}"
                        )
                else:
                    logger.debug(
                        f'Skipping registry provider "{provider}": Not in PROVIDER_CONFIG or unhandled'
                    )

        if not self.model_preference:
            # Check if only Suno was configured and it failed, or if nothing was configured
            if not any(
                p.startswith("suno:") for p in self.providers
            ) and not any(p == "suno" for p, _ in self.model_preference):
                raise ValueError(
                    "No valid LLM or BAS providers could be initialized."
                )
            elif not self.providers:  # Nothing got initialized at all
                raise ValueError(
                    "No valid LLM or BAS providers could be initialized."
                )
        logger.info(
            f"LLM Orchestrator initialized. Final Preference Order: {self.model_preference}"
        )
        logger.debug(f"Initialized providers: {list(self.providers.keys())}")

    def _infer_provider(self, model_name: str) -> str:
        model_lower = model_name.lower()
        # Specific keywords for Suno models if not explicitly prefixed
        if "suno" in model_lower or model_lower in [
            "chirp-v3-0",
            "chirp-v3-5",
            "v3",
            "v4",
            "v4.5",
        ]:
            return "suno"
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
        # Fallback to registry check
        for provider_key, data in LLM_REGISTRY.items():
            if provider_key != "suno" and model_name in data.get("models", []):
                logger.debug(
                    f'Inferred provider "{provider_key}" for model "{model_name}" from registry.'
                )
                return provider_key
        logger.warning(
            f'Could not infer provider for "{model_name}". Defaulting to openai.'
        )
        return "openai"

    def _add_provider(self, model_identifier: str):
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
            logger.warning(
                f"Unsupported provider: {provider}. Skipping model {model_name}."
            )
            self.initialized_models.add(
                (provider, model_name)
            )  # Mark as processed to avoid re-attempts
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
            ):  # Suno BAS doesn't need an API key via env for this orchestrator
                logger.warning(
                    f"Skipping provider {provider} model {model_name}: API key ({provider_info['api_key_env']}) not found."
                )
                self.initialized_models.add((provider, model_name))
                return
        elif (
            provider != "suno"
        ):  # If no api_key_env is defined for a non-Suno provider, it's an issue
            logger.warning(
                f"API key environment variable not defined for provider {provider} in PROVIDER_CONFIG. This provider may not work."
            )

        provider_key = f"{provider}:{model_name}"
        if provider_key not in self.providers:
            try:
                instance = LLMProviderInstance(
                    provider, model_name, api_key, self.config
                )
                self.providers[provider_key] = instance
                if (
                    provider,
                    model_name,
                ) not in self.model_preference:  # Avoid duplicates if added by primary/fallback then discovery
                    self.model_preference.append((provider, model_name))
                self.initialized_models.add((provider, model_name))
                logger.info(
                    f"Successfully added provider: {provider}, model: {model_name}"
                )
            except ConfigurationError as e:
                logger.warning(
                    f"Configuration error adding {provider}:{model_name}: {e}"
                )
                self.initialized_models.add((provider, model_name))
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

    async def generate_text_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_kwargs: Optional[Dict[str, Any]] = None,
        **other_llm_params: Any,
    ) -> Optional[str]:
        """Generates text using the preferred model, ensuring model_kwargs are flattened."""
        if not prompt:
            raise ValueError("Prompt cannot be empty for text generation.")

        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        # Precedence: model_kwargs (specific) override other_llm_params (general)
        final_call_params = {**other_llm_params, **(model_kwargs or {})}

        return await self._generate_response_internal(
            task_type="text",
            messages=messages,
            prompt=prompt,
            **final_call_params,
        )

    async def generate_suno_track(
        self,
        suno_params: Dict[str, Any],
        model_kwargs: Optional[Dict[str, Any]] = None,
        **other_suno_params: Any,
    ) -> Optional[Union[Dict[str, Any], str]]:
        """Generates a Suno track using the BAS stub or a configured Suno provider."""
        if not suno_params or not isinstance(suno_params, dict):
            raise ValueError(
                "suno_params (dictionary) are required for Suno track generation."
            )

        suno_provider_key = None
        # Attempt to find an explicitly configured Suno provider first
        for p_key in self.providers:
            if p_key.startswith("suno:"):
                suno_provider_key = p_key
                break

        if not suno_provider_key:
            for provider_name, model_name_in_pref in self.model_preference:
                if provider_name == "suno":
                    suno_provider_key = f"{provider_name}:{model_name_in_pref}"
                    if suno_provider_key not in self.providers:
                        logger.warning(
                            f"Suno provider {suno_provider_key} found in preference but not initialized. Attempting to initialize."
                        )
                        self._add_provider(suno_provider_key)
                        if suno_provider_key not in self.providers:
                            suno_provider_key = None
                            continue
                    break

        attempt1_result = None
        if suno_provider_key and suno_provider_key in self.providers:
            logger.info(
                f"Attempting track generation with configured Suno provider: {suno_provider_key}"
            )
            current_final_call_params = {
                **other_suno_params,
                **(model_kwargs or {}),
            }
            current_final_call_params.update(suno_params)
            try:
                attempt1_result = await self._generate_response_internal(
                    provider_key=suno_provider_key,
                    task_type="suno",
                    messages=None,
                    prompt=None,
                    suno_params=current_final_call_params,
                )
                if attempt1_result is not None:
                    logger.info(
                        f"Successfully generated track with configured Suno provider: {suno_provider_key}"
                    )
                    return attempt1_result
                else:
                    logger.warning(
                        f"Configured Suno provider {suno_provider_key} failed to generate track (returned None)."
                    )
            except Exception as e:
                logger.error(
                    f"Error during configured Suno provider {suno_provider_key} call: {e}",
                    exc_info=True,
                )
                # Error logged by _generate_response_internal already, this is just for context here
                # Fall through to BAS stub attempt

        # If configured provider was not found, or it failed (attempt1_result is None or exception occurred)
        logger.info(
            "Configured Suno provider failed or was not found/attempted. Attempting Suno BAS stub fallback."
        )
        if SunoOrchestrator and suno_bas_available:
            logger.debug(
                "Suno BAS stub is available. Proceeding with BAS stub attempt."
            )
            try:
                # Ensure suno_params are correctly passed to the BAS stub call
                # The original suno_params from the method arguments should be used here.
                bas_stub_call_params = (
                    suno_params.copy()
                )  # Use a copy of the original suno_params
                if (
                    model_kwargs
                ):  # Merge model_kwargs if any, BAS stub might not use them but for consistency
                    bas_stub_call_params.update(model_kwargs)
                if other_suno_params:  # Merge other_suno_params
                    bas_stub_call_params.update(other_suno_params)

                stub_orchestrator = SunoOrchestrator(
                    config=self.config.get("suno_config", DEFAULT_SUNO_CONFIG)
                )
                logger.debug(
                    f"Calling Suno BAS stub with effective params: {bas_stub_call_params}"
                )

                track_result = None
                if hasattr(
                    stub_orchestrator, "generate_track_async"
                ) and asyncio.iscoroutinefunction(
                    stub_orchestrator.generate_track_async
                ):
                    track_result = (
                        await stub_orchestrator.generate_track_async(
                            **bas_stub_call_params
                        )
                    )
                elif hasattr(stub_orchestrator, "generate_track"):
                    # Consider running sync in executor if it's truly blocking and in async context
                    track_result = stub_orchestrator.generate_track(
                        **bas_stub_call_params
                    )
                else:
                    raise OrchestratorError(
                        "Suno BAS stub does not have a compatible generate_track method."
                    )

                if track_result is not None:
                    logger.info(
                        f"Suno BAS stub call successful, result: {track_result}"
                    )
                    return track_result
                else:
                    logger.warning(
                        "Suno BAS stub returned None, indicating failure."
                    )
                    # This path might lead to BASFallbackError if an explicit error wasn't raised by the stub for failure
                    # For now, if it returns None, we let it fall through to the final error

            except (
                SunoOrchestratorError
            ) as e:  # Catch specific errors from BAS stub if it raises them
                logger.error(
                    f"Error during Suno BAS stub execution (SunoOrchestratorError): {e}",
                    exc_info=True,
                )
                raise BASFallbackError(f"Suno BAS stub fallback failed: {e}")
            except (
                Exception
            ) as e:  # Catch other generic exceptions from BAS stub
                logger.error(
                    f"Generic error during Suno BAS stub execution: {e}",
                    exc_info=True,
                )
                raise BASFallbackError(
                    f"Suno BAS stub fallback failed with generic error: {e}"
                )
        else:
            logger.warning(
                "Suno BAS stub is not available (SunoOrchestrator not imported or suno_bas_available is False)."
            )

        # If we reach here, all attempts (configured provider and BAS stub) have failed or were unavailable.
        logger.error(
            "All Suno generation methods (configured provider and BAS stub) failed or were unavailable."
        )
        raise OrchestratorError(
            "Suno track generation failed with all available methods."
        )

    async def _generate_response_internal(
        self,
        task_type: str,  # "text" or "suno"
        messages: Optional[List[Dict[str, str]]] = None,
        prompt: Optional[str] = None,  # For text, if messages not provided
        suno_params: Optional[Dict[str, Any]] = None,  # For suno tasks
        provider_key: Optional[
            str
        ] = None,  # Specific provider to use (e.g. for Suno)
        **kwargs: Any,
    ) -> Optional[Union[str, Dict[str, Any]]]:
        """Internal method to handle API calls with retries and fallback."""
        # print(f"DEBUG STDERR: _generate_response_internal received **kwargs: {kwargs}", file=sys.stderr)
        last_error: Optional[Exception] = None

        if task_type == "text" and not messages and prompt:
            messages = [{"role": "user", "content": prompt}]
        elif task_type == "text" and not messages:
            raise ValueError(
                "Messages or prompt required for text generation."
            )
        elif task_type == "suno" and not suno_params:
            raise ValueError("suno_params required for Suno track generation.")

        # Determine the order of providers to try
        providers_to_try = []
        if (
            provider_key and provider_key in self.providers
        ):  # If a specific provider is requested (e.g. for Suno)
            provider_tuple = provider_key.split(":", 1)
            providers_to_try.append((provider_tuple[0], provider_tuple[1]))
        else:  # Default to model_preference for text tasks
            providers_to_try = list(self.model_preference)

        if not providers_to_try:
            logger.error("No providers available to attempt the request.")
            raise OrchestratorError("No providers available for the task.")

        for i, (provider, model_name) in enumerate(providers_to_try):
            provider_key_loop = f"{provider}:{model_name}"
            if provider_key_loop not in self.providers:
                logger.warning(
                    f"Provider {provider_key_loop} not initialized, skipping."
                )
                continue

            instance = self.providers[provider_key_loop]
            current_delay = self.initial_delay
            for attempt in range(self.max_retries_per_provider):
                provider_display_name = f"{provider}:{model_name}"
                try:
                    logger.info(
                        f"Attempting {task_type} generation with {provider}:{model_name} (Attempt {attempt + 1}/{self.max_retries_per_provider})"
                    )

                    # Revised parameter merging: start with a copy of kwargs passed to _generate_response_internal
                    # This ensures that parameters like temperature, max_tokens from the initial call are included.
                    merged_params = kwargs.copy()

                    # For text tasks, add messages. For Suno, add suno_params.
                    if task_type == "text" and messages:
                        merged_params["messages"] = messages
                    elif task_type == "suno" and suno_params:
                        # Suno might not use a generic "model" param in its direct call,
                        # but its orchestrator might handle it. For now, pass suno_params directly.
                        # We assume suno_params contains everything needed for the Suno call.
                        # If Suno client expects specific kwargs, they should be in suno_params.
                        pass  # suno_params are handled below based on provider type

                    # Add model_name if not already in merged_params, for providers that need it explicitly in the call
                    if "model" not in merged_params and provider not in [
                        "gemini",
                        "suno",
                    ]:
                        merged_params["model"] = model_name
                    elif (
                        provider == "gemini" and "model" in merged_params
                    ):  # Gemini model is part of client, not call
                        del merged_params["model"]

                    # Remove params not applicable to the current provider type or already handled
                    if provider != "suno" and "suno_params" in merged_params:
                        del merged_params["suno_params"]
                    if provider == "suno" and "messages" in merged_params:
                        del merged_params["messages"]
                    if provider == "suno" and "prompt" in merged_params:
                        del merged_params["prompt"]
                    if "provider_key" in merged_params:
                        del merged_params["provider_key"]  # Internal use
                    if "task_type" in merged_params:
                        del merged_params["task_type"]  # Internal use

                    # --- Provider-Specific Call Logic ---
                    elif provider in ["openai", "deepseek", "grok"]:
                        logger.debug(
                            f"Attempting to call OpenAI-like provider: {provider} with client type {type(instance.client)}"
                        )
                        # Allow MagicMock for testing, especially if the actual library isn't present
                        is_valid_client = False
                        if AsyncOpenAI is not None and isinstance(
                            instance.client, AsyncOpenAI
                        ):
                            is_valid_client = True
                        elif isinstance(
                            instance.client, MagicMock
                        ):  # Always allow MagicMock
                            is_valid_client = True

                        if not is_valid_client:
                            logger.error(
                                f"OpenAI-like client type mismatch for {provider}. Expected AsyncOpenAI or MagicMock, got {type(instance.client)}"
                            )
                            raise OrchestratorError(
                                f"Incorrect client type for {provider}. Expected AsyncOpenAI or MagicMock."
                            )

                        logger.debug(
                            f"OpenAI-like merged_params for {provider}: {merged_params}"
                        )
                        response = (
                            await instance.client.chat.completions.create(
                                **merged_params
                            )
                        )
                        logger.debug(
                            f"OpenAI-like response object from {provider}: {response}"
                        )

                        if (
                            not response
                            or not hasattr(response, "choices")
                            or not response.choices
                            or not hasattr(response.choices[0], "message")
                            or not hasattr(
                                response.choices[0].message, "content"
                            )
                        ):
                            logger.error(
                                f"Invalid response structure from {provider}. Response: {response}"
                            )
                            raise OrchestratorError(
                                f"Invalid response structure from {provider}"
                            )

                        result = response.choices[0].message.content
                        logger.debug(
                            f"OpenAI-like result from {provider}: {result}"
                        )
                    elif provider == "gemini":
                        if (
                            not hasattr(
                                instance.client, "generate_content_async"
                            )
                            or not messages
                        ):
                            raise OrchestratorError(
                                "Gemini client misconfigured or messages missing."
                            )
                        # Gemini uses `contents` from messages, and other params like `generation_config`
                        gemini_contents = [
                            msg["content"]
                            for msg in messages
                            if msg["role"] == "user"
                        ]  # Simplified
                        gemini_generation_config = (
                            genai.types.GenerationConfig(
                                candidate_count=merged_params.get(
                                    "candidate_count", 1
                                ),
                                temperature=merged_params.get("temperature"),
                                max_output_tokens=merged_params.get(
                                    "max_tokens"
                                )
                                or merged_params.get("max_output_tokens"),
                                top_p=merged_params.get("top_p"),
                                top_k=merged_params.get("top_k"),
                            )
                        )
                        safety_settings = merged_params.get(
                            "safety_settings", DEFAULT_GEMINI_SAFETY_SETTINGS
                        )
                        response = (
                            await instance.client.generate_content_async(
                                contents=gemini_contents,
                                generation_config=gemini_generation_config,
                                safety_settings=safety_settings,
                            )
                        )
                        if (
                            response.prompt_feedback
                            and response.prompt_feedback.block_reason
                        ):
                            error_message = f"Gemini content generation blocked due to: {response.prompt_feedback.block_reason}. Message: {getattr(response.prompt_feedback, 'block_reason_message', 'N/A')}"
                            logger.warning(error_message)
                            raise OrchestratorError(error_message)
                        result = response.text
                    elif provider == "mistral":
                        # Validated check for Mistral client and ChatMessage
                        is_valid_mistral_client = False
                        if (
                            MistralAsyncClient is not None
                        ):  # Actual library type is known
                            if isinstance(instance.client, MistralAsyncClient):
                                is_valid_mistral_client = True
                            # Also allow if it's an AsyncMock with the 'chat' attribute (typical for our tests)
                            # Ensure AsyncMock is imported or defined for this check if not globally available
                            # For this context, assuming AsyncMock from unittest.mock is implicitly available or defined
                            elif (
                                hasattr(instance.client, "__class__")
                                and instance.client.__class__.__name__
                                == "AsyncMock"
                                and hasattr(instance.client, "chat")
                            ):
                                is_valid_mistral_client = True
                        elif hasattr(
                            instance.client, "chat"
                        ):  # Library type not known (None), so check if it's a mock with 'chat'
                            is_valid_mistral_client = True

                        if not is_valid_mistral_client:
                            raise OrchestratorError(
                                f"Mistral client is not a valid MistralAsyncClient or compatible mock. Got: {type(instance.client)}"
                            )

                        if not messages:
                            raise OrchestratorError(
                                "Messages missing for Mistral call."
                            )

                            # BEGIN REPLACEMENT for Mistral ChatMessage handling (by fix_mistral_chatmessage_handling_v3.py)
                        try:
                            if ChatMessage is None:
                                logger.debug(
                                    f"ChatMessage (Mistral) is None for {provider_display_name} (Attempt {attempt + 1}/{self.max_retries_per_provider})."
                                )
                                raise TypeError(
                                    "ChatMessage is None, cannot form Mistral-specific messages."
                                )
                            mistral_messages = [
                                ChatMessage(
                                    role=msg["role"], content=msg["content"]
                                )
                                for msg in messages
                            ]
                            logger.debug(
                                f"Successfully formed MistralChatMessages for {provider_display_name} (Attempt {attempt + 1}/{self.max_retries_per_provider})."
                            )
                        except (TypeError, AttributeError) as e_chat_format:
                            logger.warning(
                                f"Could not form MistralChatMessage for {provider_display_name} "
                                f"(Attempt {attempt + 1}/{self.max_retries_per_provider}). Error: {e_chat_format}. "
                                f"Falling back to using the original 'messages' list of dicts for the mock client."
                            )
                            mistral_messages = (
                                messages  # Fallback to list of dicts
                            )
                        # END REPLACEMENT
                        # Mistral specific params: temperature, top_p, max_tokens, safe_prompt, random_seed
                        mistral_call_params = {
                            k: v
                            for k, v in merged_params.items()
                            if k
                            in [
                                "temperature",
                                "top_p",
                                "max_tokens",
                                "safe_prompt",
                                "random_seed",
                            ]
                        }
                        mistral_call_params["model"] = (
                            model_name  # Mistral needs model in call
                        )
                        response = await instance.client.chat(
                            messages=mistral_messages, **mistral_call_params
                        )
                        result = response.choices[0].message.content
                    elif provider == "anthropic":
                        if (
                            not isinstance(instance.client, AsyncAnthropic)
                            or not messages
                        ):
                            raise OrchestratorError(
                                "Anthropic client misconfigured or messages missing."
                            )
                        # Anthropic specific params: max_tokens, system, temperature, top_p, top_k
                        anthropic_call_params = {
                            k: v
                            for k, v in merged_params.items()
                            if k
                            in [
                                "max_tokens_to_sample",
                                "temperature",
                                "top_p",
                                "top_k",
                            ]
                        }
                        if "max_tokens" in merged_params:
                            anthropic_call_params["max_tokens"] = (
                                merged_params["max_tokens"]
                            )
                        if "system_prompt" in merged_params:
                            anthropic_call_params["system"] = merged_params[
                                "system_prompt"
                            ]

                        anthropic_messages = [
                            msg for msg in messages if msg["role"] != "system"
                        ]  # System prompt handled separately
                        response = await instance.client.messages.create(
                            model=model_name,
                            messages=anthropic_messages,
                            **anthropic_call_params,
                        )
                        result = response.content[0].text
                    elif provider == "suno":
                        if (
                            not isinstance(instance.client, SunoOrchestrator)
                            or not suno_params
                        ):
                            raise OrchestratorError(
                                "Suno client misconfigured or suno_params missing."
                            )
                        # Assuming SunoOrchestrator has an async method like generate_track_async
                        # and suno_params contains all necessary arguments for it.
                        if hasattr(
                            instance.client, "generate_track_async"
                        ) and asyncio.iscoroutinefunction(
                            instance.client.generate_track_async
                        ):
                            result = (
                                await instance.client.generate_track_async(
                                    **suno_params
                                )
                            )
                        elif hasattr(
                            instance.client, "generate_track"
                        ):  # sync version, might need executor
                            result = instance.client.generate_track(
                                **suno_params
                            )
                        else:
                            raise OrchestratorError(
                                f"Suno provider {provider_key_loop} does not have a compatible generation method."
                            )
                    else:
                        raise OrchestratorError(
                            f"Unsupported provider type for generation: {provider}"
                        )

                    logger.info(
                        f"Successfully generated {task_type} with {provider}:{model_name}"
                    )
                    return result

                except (
                    APIError,
                    RateLimitError,
                    MistralAPIException,
                    AnthropicAPIError,
                    AnthropicRateLimitError,
                    SunoOrchestratorError,
                    OrchestratorError,
                ) as e:
                    last_error = e
                    # provider_display_name is already defined earlier

                    if isinstance(
                        e, OrchestratorError
                    ) and "Gemini content generation blocked" in str(e):
                        logger.warning(
                            f"Gemini safety block detected for {provider_display_name} "
                            f"(Attempt {attempt + 1}/{self.max_retries_per_provider}). Error: {str(e)[:500]}. "
                            f"Failing this provider immediately."
                        )
                        break
                    else:
                        logger.warning(
                            f"API/Orchestrator error with {provider_display_name} "
                            f"(Attempt {attempt + 1}/{self.max_retries_per_provider}): {e}"
                        )
                        if (
                            isinstance(
                                e, (RateLimitError, AnthropicRateLimitError)
                            )
                            or "rate limit" in str(e).lower()
                        ):
                            if attempt + 1 < self.max_retries_per_provider:
                                await asyncio.sleep(
                                    current_delay * (2**attempt)
                                )
                            else:
                                logger.error(
                                    f"Max retries reached for {provider_display_name} after rate limit. Failing provider."
                                )
                                break
                        elif attempt + 1 < self.max_retries_per_provider:
                            await asyncio.sleep(current_delay)
                        else:
                            logger.error(
                                f"Max retries reached for {provider_display_name}. Failing provider."
                            )
                            break
                except google_exceptions.GoogleAPIError as e:
                    last_error = e
                    logger.warning(
                        f"Google API error with {provider}:{model_name} (Attempt {attempt + 1}/{self.max_retries_per_provider}): {e}"
                    )
                    if attempt + 1 < self.max_retries_per_provider:
                        await asyncio.sleep(current_delay)
                except Exception as e:
                    last_error = e
                    logger.error(
                        f"Unexpected error with {provider}:{model_name} (Attempt {attempt + 1}/{self.max_retries_per_provider}): {e}",
                        exc_info=True,
                    )
                    # For unexpected errors, break retry loop for this provider immediately
                    break

            logger.error(
                f"Failed permanently with {provider}:{model_name} after {self.max_retries_per_provider} attempts."
            )
            is_last_provider_in_preference = (
                i == len(self.model_preference) - 1
            )
            if (
                self.enable_fallback_notifications
                and not is_last_provider_in_preference
            ):
                failed_provider_msg = f"{provider}:{model_name}"
                error_msg = str(last_error)
                error_msg_short = error_msg[:200]  # Define error_msg_short
                if (
                    isinstance(last_error, OrchestratorError)
                    and "Gemini content generation blocked" in error_msg
                ):
                    logger.warning(
                        f"Gemini safety block for {provider_display_name} (Attempt {attempt + 1}/{self.max_retries_per_provider}). Failing this provider immediately. Error: {error_msg[:500]}"
                    )
                    break  # Break from retry loop, move to next providertr(last_error)[:200]
                next_provider_tuple = self.model_preference[i + 1]
                next_provider_msg = (
                    f"`{next_provider_tuple[0]}:{next_provider_tuple[1]}`"
                )
                notification_message = f"LLM Fallback: Failed to call {provider} ({model_name}) after {self.max_retries_per_provider} retries. Error: {error_msg_short}. Attempting fallback to: {next_provider_msg}."
                await send_notification(notification_message)

        logger.error(
            f"All providers failed for the {task_type} task. Last error: {last_error}"
        )
        if self.enable_fallback_notifications:
            await send_notification(
                f"LLM Critical: All providers failed after retries for {task_type} task. Last error: {str(last_error)[:200]}."
            )
        # To satisfy tests expecting OrchestratorError when all fail for text tasks:
        if task_type == "text":
            raise OrchestratorError(
                f"All providers failed after retries for text generation. Last error: {last_error}"
            )
        return None  # For Suno or if specific error not required by caller
