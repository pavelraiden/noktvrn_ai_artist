"""
Orchestrator Module - Multi-Provider Support with Fallback

This module provides the core orchestration functionality for LLM interactions,
supporting multiple providers (OpenAI, DeepSeek, Grok, Gemini, Mistral)
and implementing inter-provider fallback logic.
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

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Provider Configuration --- #
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
        "client_class": None,
        "library_present": genai is not None
    },
    "mistral": {
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": None,
        "client_class": MistralAsyncClient,
        "library_present": MistralAsyncClient is not None
    },
    # Add Claude support placeholder - requires Anthropic library
    # "claude": {
    #     "api_key_env": "ANTHROPIC_API_KEY",
    #     "base_url": None,
    #     "client_class": None, # Requires Anthropic client
    #     "library_present": False # Requires installation and import check
    # },
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
    Supports a primary model and a list of fallback models.
    Handles API key loading, client initialization, and API calls with retries and inter-provider fallback.
    """

    def __init__(
        self,
        primary_model: str, # e.g., "deepseek-chat"
        fallback_models: Optional[List[str]] = None, # e.g., ["gemini-pro", "mistral-large-latest"]
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the orchestrator with primary and fallback models.

        Args:
            primary_model: The preferred model to use first.
            fallback_models: A list of model names to try in order if the primary fails.
            config: Additional configuration (e.g., temperature, max_retries, initial_delay).
        """
        self.config = config or {}
        self.max_retries_per_provider = self.config.get("max_retries", 3)
        self.initial_delay = self.config.get("initial_delay", 1.0)

        self.providers: Dict[str, LLMProviderInstance] = {}
        self.model_preference: List[Tuple[str, str]] = [] # List of (provider, model_name)

        # Initialize primary model
        self._add_provider(primary_model)

        # Initialize fallback models
        if fallback_models:
            for model_name in fallback_models:
                self._add_provider(model_name)

        if not self.model_preference:
            raise ValueError("No valid LLM providers could be initialized.")

        logger.info(f"LLM Orchestrator initialized. Preference: {self.model_preference}")

    def _infer_provider(self, model_name: str) -> str:
        """Infers the provider based on common model name prefixes."""
        model_lower = model_name.lower()
        # Add more specific checks if needed
        if model_lower.startswith("gpt-"): return "openai"
        if model_lower.startswith("deepseek-"): return "deepseek"
        if model_lower.startswith("grok-"): return "grok"
        if model_lower.startswith("gemini-") or model_lower.startswith("gemma-"): return "gemini"
        if model_lower.startswith("mistral-") or model_lower.startswith("open-mixtral-") or model_lower.startswith("codestral-"): return "mistral"
        # if model_lower.startswith("claude-"): return "claude"
        logger.warning(f"Could not infer provider for \'{model_name}\'. Specify provider if ambiguous (e.g., \'openai:gpt-3.5-turbo\'). Defaulting to openai.")
        return "openai"

    def _add_provider(self, model_identifier: str):
        """Adds a provider/model to the orchestrator if valid and configured."""
        if ":" in model_identifier:
            provider, model_name = model_identifier.split(":", 1)
            provider = provider.lower()
        else:
            model_name = model_identifier
            provider = self._infer_provider(model_name)

        if provider not in PROVIDER_CONFIG:
            logger.warning(f"Skipping unsupported provider: {provider}")
            return

        provider_info = PROVIDER_CONFIG[provider]
        if not provider_info["library_present"]:
            logger.warning(f"Skipping provider {provider}: Required library not installed.")
            return

        api_key = get_env_var(provider_info["api_key_env"])
        if not api_key:
            logger.warning(f"Skipping provider {provider}: API key ({provider_info['api_key_env']}) not found in environment.")
            return

        # Use a unique key for the providers dictionary, e.g., provider:model_name
        provider_key = f"{provider}:{model_name}"
        if provider_key not in self.providers:
            try:
                instance = LLMProviderInstance(provider, model_name, api_key, self.config)
                self.providers[provider_key] = instance
                self.model_preference.append((provider, model_name))
                logger.info(f"Successfully added provider: {provider}, model: {model_name}")
            except (ImportError, ValueError, LLMOrchestratorError) as e:
                logger.error(f"Failed to initialize provider {provider} model {model_name}: {e}")
        else:
             # Already added, ensure it's in preference list if needed (e.g., primary specified again in fallback)
             if (provider, model_name) not in self.model_preference:
                 self.model_preference.append((provider, model_name))


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
                    if not response.candidates: raise LLMOrchestratorError(f"Gemini blocked: {response.prompt_feedback.block_reason if response.prompt_feedback else 'Unknown'}")
                    content = response.candidates[0].content.parts[0].text if response.candidates[0].content and response.candidates[0].content.parts else None
                    usage = response.usage_metadata
                    if content:
                        if usage: logger.info(f"Gemini API call successful. Usage: Prompt={usage.prompt_token_count}, Completion={usage.candidates_token_count}, Total={usage.total_token_count}")
                        else: logger.info("Gemini API call successful. Usage data unavailable.")
                        return content.strip()
                    else: raise LLMOrchestratorError(f"Gemini empty response. Finish reason: {response.candidates[0].finish_reason if response.candidates else 'Unknown'}")

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

                # Add Claude logic here if/when implemented
                # elif provider == "claude":
                #     # ... Claude API call logic ...
                #     pass

                else:
                    # Should not be reached if provider config is correct
                    raise LLMOrchestratorError(f"Provider '{provider}' logic not implemented.")

            except RateLimitError as e:
                retries += 1
                logger.warning(f"{provider} rate limit. Retrying in {delay:.1f}s... ({retries}/{self.max_retries_per_provider})")
                last_exception = e
                await asyncio.sleep(delay)
                delay *= 2
            except APIError as e:
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
                    break # Break inner loop after one retry for unexpected

        # If loop finishes without returning, raise the last exception
        raise LLMOrchestratorError(f"{provider} model {model_name} failed after {retries} retries.") from last_exception

    async def generate_text(
        self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7
    ) -> str:
        """
        Generates text using the preferred model, falling back to others if necessary.
        """
        last_error = None
        for provider, model_name in self.model_preference:
            provider_key = f"{provider}:{model_name}"
            if provider_key not in self.providers:
                logger.warning(f"Provider instance {provider_key} not found, skipping.")
                continue

            provider_instance = self.providers[provider_key]
            logger.info(f"Attempting generation with: {provider} / {model_name}")
            try:
                result = await self._call_provider_with_retry(
                    provider_instance, prompt, max_tokens, temperature
                )
                logger.info(f"Successfully generated text using {provider} / {model_name}.")
                return result
            except Exception as e:
                logger.warning(f"Generation failed with {provider} / {model_name}: {e}. Trying next provider.")
                last_error = e
                # Optional: Add a small delay before trying the next provider
                await asyncio.sleep(0.5)

        # If all providers failed
        error_msg = "All configured LLM providers failed to generate text."
        logger.critical(error_msg)
        if last_error:
            raise LLMOrchestratorError(error_msg) from last_error
        else:
            raise LLMOrchestratorError(error_msg)

    # --- Placeholder for Intelligent Routing --- #
    # This section requires significant future work: cost analysis, performance benchmarking,
    # task-specific model selection logic, etc.
    def _select_best_model_for_task(self, task_type: str, prompt_length: int) -> Tuple[str, str]:
        """Placeholder for intelligent model selection based on task characteristics."""
        logger.warning("Intelligent model routing not implemented. Using default preference order.")
        # Basic example: maybe use a cheaper model for short summaries?
        # if task_type == "summary" and prompt_length < 500:
        #     # Try to find a specific model known to be cheap/fast for summaries
        #     pass
        # Default to the primary model in the preference list
        if self.model_preference:
            return self.model_preference[0]
        else:
            raise LLMOrchestratorError("No models available in preference list.")

    async def generate_text_intelligently(
        self, prompt: str, task_type: str = "general", max_tokens: int = 1024, temperature: float = 0.7
    ) -> str:
        """
        Generates text, attempting intelligent model selection first (currently placeholder).
        Falls back to the standard preference list if intelligent selection fails or isn't implemented.
        """
        try:
            # Placeholder: Select best model (currently just returns the first preference)
            best_provider, best_model = self._select_best_model_for_task(task_type, len(prompt))
            provider_key = f"{best_provider}:{best_model}"
            provider_instance = self.providers[provider_key]

            logger.info(f"Intelligently selected: {best_provider} / {best_model} for task type '{task_type}'")
            result = await self._call_provider_with_retry(
                provider_instance, prompt, max_tokens, temperature
            )
            logger.info(f"Successfully generated text using intelligently selected {best_provider} / {best_model}.")
            return result
        except Exception as e:
            logger.warning(f"Intelligent selection/generation failed: {e}. Falling back to standard preference list.")
            # Fallback to the standard generate_text method which iterates through all preferences
            return await self.generate_text(prompt, max_tokens, temperature)


# --- Example Usage --- #
async def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting LLM Orchestrator example...")

    # Example: Use DeepSeek first, fallback to Gemini, then Mistral
    # Ensure relevant API keys are in the .env file
    try:
        orchestrator = LLMOrchestrator(
            primary_model="deepseek-chat",
            fallback_models=["gemini-1.5-flash", "mistral-large-latest"],
            config={"max_retries": 2, "initial_delay": 0.5}
        )
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {e}")
        return

    prompt = "Write a short poem about a robot learning to dream."

    logger.info("--- Testing Standard Generation (with fallback) ---")
    try:
        response = await orchestrator.generate_text(prompt, max_tokens=100)
        logger.info(f"\nGenerated Text:\n{response}\n")
    except LLMOrchestratorError as e:
        logger.error(f"Standard generation failed: {e}")

    logger.info("--- Testing Intelligent Generation (placeholder) ---")
    try:
        response_intelligent = await orchestrator.generate_text_intelligently(
            prompt, task_type="creative_writing", max_tokens=100
        )
        logger.info(f"\nIntelligently Generated Text:\n{response_intelligent}\n")
    except LLMOrchestratorError as e:
        logger.error(f"Intelligent generation failed: {e}")

if __name__ == "__main__":
    # Make sure API keys are set in .env file in the project root
    # e.g., DEEPSEEK_API_KEY=..., GEMINI_API_KEY=..., MISTRAL_API_KEY=...
    asyncio.run(main())

