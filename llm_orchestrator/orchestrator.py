"""
Orchestrator Module - Multi-Provider Support

This module provides the core orchestration functionality for LLM interactions,
supporting multiple providers (OpenAI, DeepSeek, Grok, Gemini, Mistral).
"""

import logging
import os
import sys
import json # Added import for json
from typing import Dict, Any, Optional, Literal
import asyncio

# Add project root to sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# Import necessary components
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
    # Define default safety settings only if import is successful
    DEFAULT_GEMINI_SAFETY_SETTINGS = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
except ImportError:
    genai = None
    # Define dummy values if import fails
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
    # Assuming env_utils is in scripts/utils/
    from scripts.utils.env_utils import load_env_vars
except ImportError:
    print("Warning: env_utils not found. API keys must be loaded manually from os.environ.")
    def load_env_vars():
        return os.environ

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Provider Configuration --- #
# Define base URLs for OpenAI-compatible APIs
PROVIDER_CONFIG = {
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url": None, # Uses default OpenAI base URL
        "client_class": AsyncOpenAI,
        "library_present": AsyncOpenAI is not None
    },
    "deepseek": {
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1",
        "client_class": AsyncOpenAI, # Uses OpenAI client
        "library_present": AsyncOpenAI is not None
    },
    "grok": {
        "api_key_env": "GROK_API_KEY",
        "base_url": "https://api.x.ai/v1",
        "client_class": AsyncOpenAI, # Uses OpenAI client
        "library_present": AsyncOpenAI is not None
    },
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "base_url": None,
        "client_class": None, # Uses google.generativeai directly
        "library_present": genai is not None
    },
    "mistral": {
        "api_key_env": "MISTRAL_API_KEY",
        "base_url": None, # Uses default Mistral base URL
        "client_class": MistralAsyncClient,
        "library_present": MistralAsyncClient is not None
    },
}

class LLMOrchestratorError(Exception):
    """Custom exception for LLM Orchestrator errors."""
    pass

class LLMOrchestrator:
    """
    Orchestrates interactions with multiple LLM providers (OpenAI, DeepSeek, Grok, Gemini, Mistral).
    Handles API key loading, client initialization, and API calls with retries.
    """

    def __init__(
        self,
        model_name: str, # e.g., "gpt-4o", "deepseek-chat", "gemma-7b", "mistral-large-latest"
        provider_type: Optional[Literal["openai", "deepseek", "grok", "gemini", "mistral"]] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the orchestrator for a specific model and provider.

        Args:
            model_name: The specific model to use.
            provider_type: (Optional) Explicitly specify the provider. If None, inferred from model_name prefixes.
            config: Additional configuration (e.g., temperature, max_retries, initial_delay).
        """
        self.model_name = model_name
        self.config = config or {}
        self.max_retries = self.config.get("max_retries", 3)
        self.initial_delay = self.config.get("initial_delay", 1.0)

        # Infer provider if not specified
        if provider_type:
            self.provider = provider_type.lower()
        else:
            self.provider = self._infer_provider(model_name)

        if self.provider not in PROVIDER_CONFIG:
            raise ValueError(f"Unsupported provider type: {self.provider}")

        provider_info = PROVIDER_CONFIG[self.provider]
        if not provider_info["library_present"]:
            raise ImportError(f"Required library for provider \'{self.provider}\' is not installed or failed to import.")

        # Load API key
        env_vars = load_env_vars()
        self.api_key = env_vars.get(provider_info["api_key_env"])
        if not self.api_key:
            raise ValueError(f"{provider_info["api_key_env"]} not found in environment variables.")

        # Initialize client
        self.client = self._initialize_client(provider_info)

        logger.info(f"Initialized LLMOrchestrator for provider: {self.provider}, model: {self.model_name}")

    def _infer_provider(self, model_name: str) -> str:
        """Infers the provider based on common model name prefixes."""
        model_lower = model_name.lower()
        if model_lower.startswith("gpt-"):
            return "openai"
        if model_lower.startswith("deepseek-"):
            return "deepseek"
        if model_lower.startswith("grok-"):
            return "grok"
        if model_lower.startswith("gemini-") or model_lower.startswith("gemma-"):
            return "gemini"
        if model_lower.startswith("mistral-") or model_lower.startswith("open-mixtral-") or model_lower.startswith("codestral-"):
            return "mistral"
        # Default or raise error if ambiguous
        logger.warning(f"Could not infer provider from model name \'{model_name}\'. Defaulting to \'openai\'. Specify provider_type explicitly if needed.")
        return "openai"

    def _initialize_client(self, provider_info: Dict[str, Any]) -> Any:
        """Initializes the appropriate API client based on the provider."""
        client_class = provider_info["client_class"]
        base_url = provider_info["base_url"]

        if self.provider == "gemini":
            if not genai:
                 raise ImportError("Gemini library (google.generativeai) is required but not available.")
            genai.configure(api_key=self.api_key)
            # Return the generative model instance directly for Gemini
            return genai.GenerativeModel(self.model_name)
        elif client_class:
            # For OpenAI, DeepSeek, Grok, Mistral
            client_args = {"api_key": self.api_key}
            if base_url:
                client_args["base_url"] = base_url
            return client_class(**client_args)
        else:
            # Should not happen if checks pass, but added for safety
            raise LLMOrchestratorError(f"Client class not defined for provider {self.provider}")

    async def _call_llm_with_retry(
        self, prompt: str, max_tokens: int, temperature: float
    ) -> str:
        """Internal method to call the LLM API with retry logic, handling different providers."""
        retries = 0
        delay = self.initial_delay
        last_exception = None

        while retries < self.max_retries:
            try:
                logger.debug(f"Attempt {retries + 1}/{self.max_retries} calling {self.provider} model {self.model_name}")
                if self.provider in ["openai", "deepseek", "grok"]:
                    if not AsyncOpenAI: raise ImportError("OpenAI library required for this provider.")
                    response = await self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens,
                        temperature=temperature,
                        n=1,
                        stop=None,
                    )
                    if response.choices and response.choices[0].message and response.choices[0].message.content:
                        # Log token usage if available (OpenAI format)
                        if response.usage:
                            logger.info(f"{self.provider} API call successful. Usage: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}, Total={response.usage.total_tokens}")
                        else:
                            logger.info(f"{self.provider} API call successful. Usage data not available.")
                        return response.choices[0].message.content.strip()
                    else:
                        raise LLMOrchestratorError(f"{self.provider} response format invalid: {response}")

                elif self.provider == "gemini":
                    if not genai: raise ImportError("Gemini library required for this provider.")
                    # Gemini uses generate_content_async
                    generation_config = genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=temperature
                    )
                    # Use safety settings defined during import or empty dict if import failed
                    safety_settings = self.config.get("gemini_safety_settings", DEFAULT_GEMINI_SAFETY_SETTINGS)
                    response = await self.client.generate_content_async(
                        prompt,
                        generation_config=generation_config,
                        safety_settings=safety_settings
                    )
                    # Handle potential blocks
                    if not response.candidates:
                         block_reason = response.prompt_feedback.block_reason if response.prompt_feedback else "Unknown"
                         raise LLMOrchestratorError(f"Gemini generation blocked. Reason: {block_reason}")
                    if response.candidates[0].content and response.candidates[0].content.parts:
                        # Log token usage if available (Gemini format)
                        if response.usage_metadata:
                             logger.info(f"Gemini API call successful. Usage: Prompt={response.usage_metadata.prompt_token_count}, Completion={response.usage_metadata.candidates_token_count}, Total={response.usage_metadata.total_token_count}")
                        else:
                             logger.info("Gemini API call successful. Usage data not available.")
                        return response.candidates[0].content.parts[0].text.strip()
                    else:
                        finish_reason = response.candidates[0].finish_reason if response.candidates else "Unknown"
                        raise LLMOrchestratorError(f"Gemini response content empty. Finish reason: {finish_reason}")

                elif self.provider == "mistral":
                    if not MistralAsyncClient or not ChatMessage: raise ImportError("Mistral library required for this provider.")
                    # Mistral uses chat_async
                    messages = [ChatMessage(role="user", content=prompt)]
                    response = await self.client.chat_async(
                        model=self.model_name,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    if response.choices and response.choices[0].message and response.choices[0].message.content:
                        # Log token usage if available (Mistral format)
                        if response.usage:
                            logger.info(f"Mistral API call successful. Usage: Prompt={response.usage.prompt_tokens}, Completion={response.usage.completion_tokens}, Total={response.usage.total_tokens}")
                        else:
                            logger.info("Mistral API call successful. Usage data not available.")
                        return response.choices[0].message.content.strip()
                    else:
                        raise LLMOrchestratorError(f"Mistral response format invalid: {response}")

            except RateLimitError as e:
                retries += 1
                logger.warning(f"{self.provider} rate limit exceeded. Retrying in {delay} seconds... ({retries}/{self.max_retries})")
                last_exception = e
                await asyncio.sleep(delay)
                delay *= 2 # Exponential backoff
            except APIError as e:
                # General API errors (could be auth, server issues, etc.)
                retries += 1
                logger.warning(f"{self.provider} API error occurred: {e}. Retrying in {delay} seconds... ({retries}/{self.max_retries})")
                last_exception = e
                await asyncio.sleep(delay)
                delay *= 2
            except ImportError as e:
                # Library missing error - should not happen if checks pass, but handle defensively
                logger.error(f"Missing required library for {self.provider}: {e}")
                last_exception = e
                break # Cannot retry if library is missing
            except Exception as e:
                # Catch other potential errors (network, unexpected response format, Gemini blocks)
                logger.error(f"An unexpected error occurred during {self.provider} LLM call: {e}", exc_info=True)
                last_exception = e
                # Decide whether to retry based on error type if needed, for now, break on unexpected
                # If it's a Gemini block error, retrying won't help.
                if isinstance(e, LLMOrchestratorError) and "blocked" in str(e):
                    break
                # For other unexpected errors, maybe retry once?
                if retries < 1: # Retry unexpected errors once
                    retries += 1
                    logger.warning(f"Retrying unexpected error once in {delay} seconds...")
                    await asyncio.sleep(delay)
                    delay *= 2
                else:
                    break

        error_msg = f"{self.provider} LLM call failed after {retries} retries for model {self.model_name}."
        logger.error(error_msg)
        if last_exception:
             # Wrap the original exception
             raise LLMOrchestratorError(error_msg) from last_exception
        else:
             # Should not happen often, but raise a generic error
             raise LLMOrchestratorError(error_msg)

    async def generate_text(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        """
        Generates text based on a given prompt using the configured LLM.
        """
        logger.info(f"Generating text using {self.provider}/{self.model_name} (Prompt starts: {prompt[:100]}...)")
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
        """
        context_str = f"\n\nRelevant Context:\n```json\n{json.dumps(context, indent=2)}\n```" if context else ""
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
        logger.info(f"Adapting prompt using {self.provider}/{self.model_name} (Instructions start: {adaptation_instructions[:100]}...)")
        adapted_prompt = await self.generate_text(combined_prompt, max_tokens, temperature)
        # Clean up potential markdown code blocks
        if adapted_prompt.startswith("```") and adapted_prompt.endswith("```"):
             adapted_prompt = adapted_prompt[3:-3].strip()
        elif adapted_prompt.startswith("`") and adapted_prompt.endswith("`"):
             adapted_prompt = adapted_prompt[1:-1].strip()
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
        """
        context_str = f"\n\nRelevant Context:\n```json\n{json.dumps(context, indent=2)}\n```" if context else ""
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
        logger.info(f"Evolving description using {self.provider}/{self.model_name} (Goal starts: {evolution_goal[:100]}...)")
        evolved_description = await self.generate_text(combined_prompt, max_tokens, temperature)
        # Clean up potential markdown code blocks
        if evolved_description.startswith("```") and evolved_description.endswith("```"):
             evolved_description = evolved_description[3:-3].strip()
        elif evolved_description.startswith("`") and evolved_description.endswith("`"):
             evolved_description = evolved_description[1:-1].strip()
        return evolved_description

    # Added method for direct profile generation call, needed by llm_pipeline
    async def generate_profile(self, input_data: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Generates a full artist profile based on input data using the specified model."""
        # This method might need more sophisticated prompting depending on requirements
        # For now, just use generate_text with a basic prompt
        prompt = f"Create a detailed AI artist profile based on the following input:\n{json.dumps(input_data, indent=2)}\n\nRespond with only the JSON object for the profile."

        # Ensure the orchestrator instance matches the requested model
        if model != self.model_name:
            # This indicates a potential mismatch in how the pipeline uses the orchestrator.
            # The pipeline should ideally instantiate the correct orchestrator per model.
            # For now, log a warning and proceed with the instance's configured model.
            logger.warning(f"generate_profile called with model \'{model}\' but orchestrator is configured for \'{self.model_name}\'. Using \'{self.model_name}\'.")
            # Alternatively, could raise an error or re-initialize, but that's complex here.

        logger.info(f"Generating profile using {self.provider}/{self.model_name}")
        profile_json_str = await self.generate_text(prompt, max_tokens=2048, temperature=0.7)

        # Attempt to parse the JSON response
        try:
            # Clean potential markdown fences
            if profile_json_str.startswith("```json"):
                profile_json_str = profile_json_str[7:]
            if profile_json_str.startswith("```"):
                profile_json_str = profile_json_str[3:]
            if profile_json_str.endswith("```"):
                profile_json_str = profile_json_str[:-3]

            profile_data = json.loads(profile_json_str.strip())
            if not isinstance(profile_data, dict):
                raise ValueError("LLM response was not a JSON object.")
            logger.info(f"Successfully parsed generated profile from {self.provider}/{self.model_name}")
            return profile_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from {self.provider}/{self.model_name}: {e}")
            logger.debug(f"Raw response: {profile_json_str}")
            raise LLMOrchestratorError(f"Failed to parse JSON response from LLM: {e}") from e
        except ValueError as e:
            logger.error(f"LLM response validation failed: {e}")
            logger.debug(f"Raw response: {profile_json_str}")
            raise LLMOrchestratorError(f"LLM response validation failed: {e}") from e

# Example Usage (for testing purposes)
async def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.info("--- Testing Multi-Provider LLM Orchestrator --- ")

    test_providers = ["openai", "deepseek", "gemini", "mistral", "grok"]
    test_models = {
        "openai": "gpt-4o", # Replace with a model you have access to
        "deepseek": "deepseek-chat",
        "gemini": "gemini-1.5-flash-latest",
        "mistral": "mistral-large-latest",
        "grok": "grok-1" # Replace with actual Grok model name if different
    }

    for provider in test_providers:
        print(f"\n--- Testing Provider: {provider.upper()} ---")
        model = test_models.get(provider)
        if not model:
            print(f"Skipping {provider}: No test model specified.")
            continue

        try:
            orchestrator = LLMOrchestrator(model_name=model, provider_type=provider)
            prompt = f"Write a short, cheerful haiku about the {provider} API."
            print(f"Prompt: {prompt}")
            response = await orchestrator.generate_text(prompt, max_tokens=100, temperature=0.7)
            print(f"Response from {provider}/{model}:\n{response}")
        except (ValueError, ImportError, LLMOrchestratorError) as e:
            print(f"Error testing {provider}: {e}")
        except Exception as e:
            print(f"Unexpected error testing {provider}: {e}")

    # Test profile generation (using one provider, e.g., deepseek)
    print("\n--- Testing Profile Generation (DeepSeek) ---")
    try:
        profile_orchestrator = LLMOrchestrator(model_name="deepseek-chat", provider_type="deepseek")
        test_input = {"genre": "Cyberpunk Electro", "mood": "Energetic & Dark"}
        profile = await profile_orchestrator.generate_profile(test_input, model="deepseek-chat")
        print("Generated Profile (DeepSeek):")
        print(json.dumps(profile, indent=2))
    except (ValueError, ImportError, LLMOrchestratorError) as e:
        print(f"Error testing profile generation: {e}")
    except Exception as e:
        print(f"Unexpected error testing profile generation: {e}")

if __name__ == "__main__":
    # Load env vars from .env file if present for local testing
    try:
        from dotenv import load_dotenv
        if load_dotenv():
             logger.info("Loaded environment variables from .env file.")
        else:
             logger.info(".env file not found or empty.")
    except ImportError:
        logger.info("dotenv library not installed, skipping .env file loading.")

    asyncio.run(main())

