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
DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env") # Check for local .env too
if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH, override=True) # Local can override root

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# --- Import necessary components ---
try:
    from openai import AsyncOpenAI, APIError, RateLimitError
except ImportError:
    AsyncOpenAI = None
    APIError = Exception
    RateLimitError = Exception
    print("Warning: OpenAI library not found. OpenAI, DeepSeek, Grok functionality will be limited.")

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
    print("Warning: google-generativeai library not found. Gemini functionality will be limited.")

try:
    from mistralai.client import MistralClient
    from mistralai.async_client import MistralAsyncClient
    from mistralai.models.chat_completion import ChatMessage
except ImportError:
    MistralAsyncClient = None
    ChatMessage = None
    print("Warning: mistralai library not found. Mistral functionality will be limited.")

try:
    from anthropic import AsyncAnthropic, APIError as AnthropicAPIError, RateLimitError as AnthropicRateLimitError
except ImportError:
    AsyncAnthropic = None
    AnthropicAPIError = Exception
    AnthropicRateLimitError = Exception
    print("Warning: Anthropic library not found. Claude functionality will be limited.")

# Import the registry
try:
    from llm_orchestrator.llm_registry import LLM_REGISTRY
except ImportError:
    LLM_REGISTRY = {}
    print("Warning: llm_registry.py not found or LLM_REGISTRY not defined. Auto-discovery disabled.")

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Provider Configuration --- #
# Enhanced PROVIDER_CONFIG to include Anthropic and check library presence
PROVIDER_CONFIG = {
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None,
        "client_class": AsyncOpenAI,
        "library_present": AsyncOpenAI is not None
    },
    "deepseek": {
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
        "client_class": AsyncOpenAI,
        "library_present": AsyncOpenAI is not None
    },
    "grok": {
        "api_key_env": "GROK_API_KEY",
        "base_url": "https://api.x.ai/v1",
        "client_class": AsyncOpenAI,
        "library_present": AsyncOpenAI is not None
    },
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "base_url": None,
        "client_class": None, # Special handling
        "library_present": genai is not None
    },
    "mistral": {
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": None,
        "client_class": MistralAsyncClient,
        "library_present": MistralAsyncClient is not None
    },
    "anthropic": {
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": None,
        "client_class": AsyncAnthropic,
        "library_present": AsyncAnthropic is not None
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
    def __init__(self, provider: str, model_name: str, api_key: str, config: Dict[str, Any]):
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
            if not genai: raise ImportError("Gemini library required.")
            genai.configure(api_key=self.api_key)
            return genai.GenerativeModel(self.model_name)
        elif client_class:
            client_args = {"api_key": self.api_key}
            if base_url:
                client_args["base_url"] = base_url
            return client_class(**client_args)
        else:
            raise LLMOrchestratorError(f"Client class not defined or library missing for {self.provider}")

class LLMOrchestrator:
    """
    Orchestrates interactions with multiple LLM providers.
    Supports a primary model, a list of fallback models, and auto-discovery from registry.
    Handles API key loading, client initialization, and API calls with retries and inter-provider fallback.
    """

    def __init__(
        self,
        primary_model: str, # e.g., "deepseek-chat"
        fallback_models: Optional[List[str]] = None, # e.g., ["gemini-pro", "mistral-large-latest"]
        config: Optional[Dict[str, Any]] = None,
        enable_auto_discovery: bool = True, # Flag to enable/disable discovery
    ):
        """
        Initialize the orchestrator with primary, fallback, and potentially discovered models.

        Args:
            primary_model: The preferred model to use first (e.g., "deepseek:deepseek-chat").
            fallback_models: A list of model names to try in order if the primary fails.
            config: Additional configuration (e.g., temperature, max_retries, initial_delay).
            enable_auto_discovery: If True, attempts to add models from LLM_REGISTRY
                                     that are not already in primary/fallback.
        """
        self.config = config or {}
        self.max_retries_per_provider = self.config.get("max_retries", 3)
        self.initial_delay = self.config.get("initial_delay", 1.0)

        self.providers: Dict[str, LLMProviderInstance] = {}
        self.model_preference: List[Tuple[str, str]] = [] # List of (provider, model_name)
        self.initialized_models = set() # Keep track of (provider, model) tuples added

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
                if provider in PROVIDER_CONFIG: # Only consider providers we know how to handle
                    for model_name in data.get("models", []):
                        if (provider, model_name) not in self.initialized_models:
                            logger.debug(f"Registry Discovery: Attempting to add {provider}:{model_name}")
                            # Use explicit provider:model format for clarity
                            self._add_provider(f"{provider}:{model_name}")
                else:
                    logger.debug(f"Skipping registry provider \t{provider}\t: Not in PROVIDER_CONFIG")

        if not self.model_preference:
            raise ValueError("No valid LLM providers could be initialized.")

        logger.info(f"LLM Orchestrator initialized. Final Preference Order: {self.model_preference}")

    def _infer_provider(self, model_name: str) -> str:
        """Infers the provider based on common model name prefixes or registry."""
        model_lower = model_name.lower()
        # Check common prefixes first
        if model_lower.startswith("gpt-"): return "openai"
        if model_lower.startswith("deepseek-"): return "deepseek"
        if model_lower.startswith("grok-"): return "grok"
        if model_lower.startswith("gemini-") or model_lower.startswith("gemma-"): return "gemini"
        if model_lower.startswith("mistral-") or model_lower.startswith("open-mixtral-") or model_lower.startswith("codestral-"): return "mistral"
        if model_lower.startswith("claude-"): return "anthropic"

        # If no prefix match, check the registry
        for provider, data in LLM_REGISTRY.items():
            if model_name in data.get("models", []):
                logger.debug(f"Inferred provider \t{provider}\t for model \t{model_name}\t from registry.")
                return provider

        logger.warning(f"Could not infer provider for \"{model_name}\". Specify provider if ambiguous (e.g., \"openai:gpt-3.5-turbo\"). Defaulting to openai.")
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
            self.initialized_models.add((provider, model_name)) # Mark as processed even if skipped
            return

        provider_info = PROVIDER_CONFIG[provider]
        if not provider_info["library_present"]:
            logger.warning(f"Skipping provider {provider} model {model_name}: Required library not installed.")
            self.initialized_models.add((provider, model_name))
            return

        api_key = get_env_var(provider_info["api_key_env"])
        if not api_key:
            logger.warning(f"Skipping provider {provider} model {model_name}: API key ({provider_info['api_key_env']}) not found in environment.")
            self.initialized_models.add((provider, model_name))
            return

        # Use a unique key for the providers dictionary, e.g., provider:model_name
        provider_key = f"{provider}:{model_name}"
        if provider_key not in self.providers:
            try:
                instance = LLMProviderInstance(provider, model_name, api_key, self.config)
                self.providers[provider_key] = instance
                self.model_preference.append((provider, model_name))
                self.initialized_models.add((provider, model_name))
                logger.info(f"Successfully added provider: {provider}, model: {model_name}")
            except (ImportError, ValueError, LLMOrchestratorError) as e:
                logger.error(f"Failed to initialize provider {provider} model {model_name}: {e}")
                self.initialized_models.add((provider, model_name)) # Mark as processed even if failed
        else:
             # Should not happen with the initialized_models check, but log if it does
             logger.debug(f"Provider key {provider_key} already exists in self.providers, but was not in initialized_models. Adding to preference list.")
             if (provider, model_name) not in self.model_preference:
                 self.model_preference.append((provider, model_name))
             self.initialized_models.add((provider, model_name))


    async def _call_provider_with_retry(
        self, provider_instance: LLMProviderInstance, prompt: str, max_tokens: int, temperature: float
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
                logger.debug(f"Attempt {retries + 1}/{self.max_retries_per_provider} calling {provider} model {model_name}")

                if provider in ["openai", "deepseek", "grok"]:
                    if not AsyncOpenAI: raise ImportError("OpenAI library required.")
                    response = await client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens, temperature=temperature, n=1, stop=None,
                    )
                    content = response.choices[0].message.content if response.choices and response.choices[0].message else None
                    usage = response.usage
                    if content:
                        if usage: logger.info(f"{provider} API call successful. Usage: Prompt={usage.prompt_tokens}, Completion={usage.completion_tokens}, Total={usage.total_tokens}")
                        else: logger.info(f"{provider} API call successful. Usage data unavailable.")
                        return content.strip()
                    else: raise LLMOrchestratorError(f"{provider} response format invalid: {response}")

                elif provider == "gemini":
                    if not genai: raise ImportError("Gemini library required.")
                    gen_config = genai.types.GenerationConfig(max_output_tokens=max_tokens, temperature=temperature)
                    safety = self.config.get("gemini_safety_settings", DEFAULT_GEMINI_SAFETY_SETTINGS)
                    response = await client.generate_content_async(prompt, generation_config=gen_config, safety_settings=safety)
                    if not response.candidates:
                        block_reason = response.prompt_feedback.block_reason if response.prompt_feedback else "Unknown"
                        logger.warning(f"Gemini blocked prompt for model {model_name}. Reason: {block_reason}")
                        raise LLMOrchestratorError(f"Gemini blocked: {block_reason}")
                    content = response.candidates[0].content.parts[0].text if response.candidates[0].content and response.candidates[0].content.parts else None
                    usage = response.usage_metadata
                    if content:
                        if usage: logger.info(f"Gemini API call successful. Usage: Prompt={usage.prompt_token_count}, Completion={usage.candidates_token_count}, Total={usage.total_token_count}")
                        else: logger.info("Gemini API call successful. Usage data unavailable.")
                        return content.strip()
                    else:
                        finish_reason = response.candidates[0].finish_reason if response.candidates else "Unknown"
                        logger.warning(f"Gemini returned empty content for model {model_name}. Finish reason: {finish_reason}")
                        raise LLMOrchestratorError(f"Gemini empty response. Finish reason: {finish_reason}")

                elif provider == "mistral":
                    if not MistralAsyncClient or not ChatMessage: raise ImportError("Mistral library required.")
                    messages = [ChatMessage(role="user", content=prompt)]
                    response = await client.chat_async(model=model_name, messages=messages, max_tokens=max_tokens, temperature=temperature)
                    content = response.choices[0].message.content if response.choices and response.choices[0].message else None
                    usage = response.usage
                    if content:
                        if usage: logger.info(f"Mistral API call successful. Usage: Prompt={usage.prompt_tokens}, Completion={usage.completion_tokens}, Total={usage.total_tokens}")
                        else: logger.info("Mistral API call successful. Usage data unavailable.")
                        return content.strip()
                    else: raise LLMOrchestratorError(f"Mistral response format invalid: {response}")

                elif provider == "anthropic":
                    if not AsyncAnthropic: raise ImportError("Anthropic library required.")
                    response = await client.messages.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    content = response.content[0].text if response.content else None
                    usage = response.usage
                    if content:
                        if usage: logger.info(f"Anthropic API call successful. Usage: Input={usage.input_tokens}, Output={usage.output_tokens}")
                        else: logger.info("Anthropic API call successful. Usage data unavailable.")
                        return content.strip()
                    else: raise LLMOrchestratorError(f"Anthropic response format invalid: {response}")

                else:
                    # Should not be reached if provider config is correct
                    raise LLMOrchestratorError(f"Provider \t{provider}\t logic not implemented.")

            except (RateLimitError, AnthropicRateLimitError) as e:
                retries += 1
                logger.warning(f"{provider} rate limit. Retrying in {delay:.1f}s... ({retries}/{self.max_retries_per_provider})")
                last_exception = e
                await asyncio.sleep(delay)
                delay *= 2
            except (APIError, AnthropicAPIError) as e:
                retries += 1
                logger.warning(f"{provider} API error: {e}. Retrying in {delay:.1f}s... ({retries}/{self.max_retries_per_provider})")
                last_exception = e
                await asyncio.sleep(delay)
                delay *= 2
            except ImportError as e:
                logger.error(f"Missing library for {provider}: {e}")
                last_exception = e
                break # Cannot retry missing library
            except LLMOrchestratorError as e:
                 # Specific errors like blocking or invalid format - don't retry these within the provider
                 logger.error(f"LLM Orchestrator Error for {provider} model {model_name}: {e}")
                 last_exception = e
                 break # Break inner loop to try next provider
            except Exception as e:
                logger.error(f"Unexpected error for {provider} model {model_name}: {e}", exc_info=True)
                last_exception = e
                # Maybe retry unexpected errors once?
                if retries < 1:
                    retries += 1
                    logger.warning(f"Retrying unexpected error once in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                    delay *= 2
                else:
                    break # Break inner loop after one retry for unexpected errors

        # If loop finishes without returning, raise the last known exception or a generic error
        if last_exception:
            raise last_exception
        else:
            raise LLMOrchestratorError(f"Provider {provider} failed after {self.max_retries_per_provider} retries.")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        # Add specific_model parameter if needed to target one model
        # specific_model: Optional[str] = None
    ) -> str:
        """
        Generates text using the configured LLM providers with fallback.

        Iterates through the model_preference list, attempting to call each provider.
        If a provider fails (after internal retries), it moves to the next in the list.

        Args:
            prompt: The input prompt for the LLM.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.

        Returns:
            The generated text content.

        Raises:
            LLMOrchestratorError: If all configured providers fail.
        """
        last_error = None
        for provider, model_name in self.model_preference:
            provider_key = f"{provider}:{model_name}"
            if provider_key in self.providers:
                provider_instance = self.providers[provider_key]
                try:
                    logger.info(f"Attempting generation with: {provider}:{model_name}")
                    result = await self._call_provider_with_retry(
                        provider_instance,
                        prompt=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    logger.info(f"Successfully generated content using {provider}:{model_name}")
                    return result
                except Exception as e:
                    logger.warning(f"Generation failed with {provider}:{model_name}. Error: {e}. Trying next provider...")
                    last_error = e
            else:
                # This should ideally not happen if initialization is correct
                logger.error(f"Provider instance not found for {provider_key} during generation attempt.")

        # If loop completes without returning, all providers failed
        logger.critical("All configured LLM providers failed.")
        if last_error:
            raise LLMOrchestratorError(f"All LLM providers failed. Last error: {last_error}") from last_error
        else:
            raise LLMOrchestratorError("All LLM providers failed. No providers were available or initialized correctly.")

# --- Example Usage ---
async def main():
    # Example: Prioritize DeepSeek, fallback to Gemini, then Mistral, auto-discover others
    primary = "deepseek:deepseek-chat"
    fallbacks = ["gemini:gemini-1.5-pro-latest", "mistral:mistral-large-latest"]

    # Ensure API keys are set in .env for the models you want to test
    # e.g., DEEPSEEK_API_KEY, GEMINI_API_KEY, MISTRAL_API_KEY, ANTHROPIC_API_KEY etc.

    try:
        orchestrator = LLMOrchestrator(primary_model=primary, fallback_models=fallbacks, enable_auto_discovery=True)

        test_prompt = "Write a short poem about a robot discovering music."
        print(f"\n--- Generating with prompt: \"{test_prompt}\" ---")
        generated_text = await orchestrator.generate(test_prompt, max_tokens=150)
        print("\nGenerated Text:")
        print(generated_text)

    except ValueError as e:
        print(f"Initialization Error: {e}")
    except LLMOrchestratorError as e:
        print(f"Generation Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())

