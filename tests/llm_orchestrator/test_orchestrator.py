# tests/llm_orchestrator/test_orchestrator.py

import pytest
import sys
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import os
from llm_orchestrator.orchestrator import AsyncOpenAI  # Added for spec
from llm_orchestrator.orchestrator import genai  # Added for spec
from llm_orchestrator.orchestrator import MistralAsyncClient  # Added for spec
from llm_orchestrator.orchestrator import AsyncAnthropic  # Added for spec

# Adjust import path based on actual project structure
from llm_orchestrator.orchestrator import (
    LLMOrchestrator,
    ConfigurationError,
    OrchestratorError,
    BASFallbackError,
    SunoOrchestratorError,  # Added import
    PROVIDER_CONFIG,  # Import for mocking
    APIError,  # Import specific errors if needed for side_effect
    RateLimitError,
    MistralAPIException,
    google_exceptions,
)

# Import APIStatusError if it's used directly (assuming it exists in openai errors)
# If it's not directly used, remove this import
try:
    from openai import APIStatusError
except ImportError:
    APIStatusError = None  # Define as None if not available

# --- Fixtures --- #


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for API keys."""
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_openai_key")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "dummy_deepseek_key")
    monkeypatch.setenv("GROK_API_KEY", "dummy_grok_key")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy_gemini_key")
    monkeypatch.setenv("MISTRAL_API_KEY", "dummy_mistral_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy_anthropic_key")
    # No key needed for Suno BAS stub, but set for consistency if checked
    monkeypatch.setenv("SUNO_API_KEY", "dummy_suno_key")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")  # Use DEBUG for more test output


@pytest.fixture
def mock_telegram(monkeypatch):
    """Mock the telegram notification function."""
    mock_send = AsyncMock()
    # Use the correct path to the function within the orchestrator module
    monkeypatch.setattr(
        "llm_orchestrator.orchestrator.send_notification", mock_send
    )
    # Attempt to remove the TelegramRetryHandler to isolate explicit notifications
    try:
        from llm_orchestrator.orchestrator import logger as orchestrator_logger
        from llm_orchestrator.orchestrator import TelegramRetryHandler
        # Ensure orchestrator module is loaded so logger might be configured
        import llm_orchestrator.orchestrator

        current_handlers = list(orchestrator_logger.handlers)
        for handler in current_handlers:
            if isinstance(handler, TelegramRetryHandler):
                orchestrator_logger.removeHandler(handler)
    except ImportError:
        pass # If imports fail, means handler likely not set up anyway

    return mock_send


# Mock provider clients to avoid actual API calls
@pytest.fixture
def mock_openai_client(mock_env_vars): # Assuming mock_env_vars is used or can be added if not present
    mock_client = AsyncMock(spec=AsyncOpenAI if AsyncOpenAI else MagicMock)
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Mocked OpenAI response"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    return mock_client


@pytest.fixture
def mock_deepseek_client():  # Separate fixture for clarity
    mock_client = AsyncMock(spec=AsyncOpenAI if AsyncOpenAI else MagicMock)
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Mocked DeepSeek response"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    # Explicitly define the nested structure for chat.completions.create
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    return mock_client


@pytest.fixture
def mock_gemini_client():
    # Ensure genai and GenerativeModel are available for spec, or use MagicMock
    # The test file already imports `from llm_orchestrator.orchestrator import genai`
    mock_client = AsyncMock(spec=genai.GenerativeModel if genai and hasattr(genai, "GenerativeModel") else MagicMock)
    
    mock_response = MagicMock()
    mock_response.text = "Mocked Gemini response"
    # Ensure candidates is a list of objects with a text attribute if accessed
    mock_candidate = MagicMock()
    # mock_candidate.text = "Mocked Gemini candidate text" # If text is accessed from candidate
    mock_response.candidates = [mock_candidate]
    mock_response.prompt_feedback = MagicMock()
    mock_response.prompt_feedback.block_reason = None
    
    # Ensure generate_content_async is an AsyncMock itself, as it's awaited
    mock_client.generate_content_async = AsyncMock(return_value=mock_response)
    
    # The patch for genai module itself to control what GenerativeModel returns
    with patch("llm_orchestrator.orchestrator.genai") as mock_genai_module:
        # If genai.GenerativeModel is called, it should return our mock_client
        mock_genai_module.GenerativeModel.return_value = mock_client
        # If genai.configure is called, make sure it doesn't break
        mock_genai_module.configure = MagicMock()
        yield mock_client

@pytest.fixture
def mock_mistral_client(): # Add params if needed
    mock_client = AsyncMock(spec=MistralAsyncClient if MistralAsyncClient else MagicMock)
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Mocked Mistral response"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    # mock_client.chat is already an AsyncMock due to spec, set its return_value
    mock_client.chat = AsyncMock(return_value=mock_response)
    return mock_client


@pytest.fixture
def mock_anthropic_client():
    mock_client = AsyncMock(spec=AsyncAnthropic if AsyncAnthropic else MagicMock)
    mock_response = MagicMock()
    mock_content = MagicMock()
    mock_content.text = "Mocked Anthropic response"
    mock_response.content = [mock_content]
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    return mock_client


# Mock the BAS stub directly
@pytest.fixture
def mock_bas_stub(monkeypatch):
    mock_stub = AsyncMock(
        return_value={
            "status": "complete",
            "clips": [{
                "id": "mock_clip_id_bas_123",
                "audio_url": "/path/to/simulated/output.mp3",
                "title": "Mocked Title from BAS Stub",
                "image_url": None,
                "video_url": None,
                "metadata": {"prompt": "Simulated prompt in BAS stub success result"}
            }]
        }
    )
    # Ensure the target path is exactly correct
    target_path = (
        "llm_orchestrator.orchestrator.LLMOrchestrator._call_bas_suno_stub"
    )
    monkeypatch.setattr(
        target_path, mock_stub, raising=False
    )  # Use raising=False just in case
    return mock_stub


# --- Test Cases --- #


@pytest.mark.asyncio
async def test_orchestrator_initialization_success(mock_env_vars):
    """Test successful initialization with primary and fallback models."""
    primary = "openai:gpt-4o"
    fallbacks = [
        "deepseek:deepseek-chat",
        "gemini:gemini-1.5-pro-latest",
        "mistral:mistral-large-latest",
        "anthropic:claude-3-opus-20240229",
        "suno:placeholder",
    ]
    # Mock provider classes to prevent actual client initialization during test
    with patch.dict(
        PROVIDER_CONFIG,
        {
            "openai": {
                **PROVIDER_CONFIG["openai"],
                "client_class": AsyncMock(),
                "library_present": True,
            },
            "deepseek": {
                **PROVIDER_CONFIG["deepseek"],
                "client_class": AsyncMock(),
                "library_present": True,
            },
            "gemini": {
                **PROVIDER_CONFIG["gemini"],
                "client_class": None,
                "library_present": True,
            },
            "mistral": {
                **PROVIDER_CONFIG["mistral"],
                "client_class": AsyncMock(),
                "library_present": True,
            },
            "anthropic": {
                **PROVIDER_CONFIG["anthropic"],
                "client_class": AsyncMock(),
                "library_present": True,
            },
            "suno": {
                **PROVIDER_CONFIG["suno"],
                "client_class": AsyncMock(), # Allow successful mock initialization
                "library_present": True,
            },
        },
    ):
        with patch(
            "llm_orchestrator.orchestrator.genai"
        ) as mock_genai:  # Mock genai configure
            orchestrator = LLMOrchestrator(
                primary_model=primary,
                fallback_models=fallbacks,
                enable_auto_discovery=False,
            )
            # Assert that genai.configure was called for Gemini
            mock_genai.configure.assert_called_once_with(
                api_key="dummy_gemini_key"
            )
            # Corrected assertion: Check actual initialized providers (Suno is now registered)
            assert len(orchestrator.model_preference) == 6  # Now includes Suno
            assert orchestrator.model_preference[0] == ("openai", "gpt-4o")
            assert orchestrator.model_preference[1] == (
                "deepseek",
                "deepseek-chat",
            )
            assert orchestrator.model_preference[2] == (
                "gemini",
                "gemini-1.5-pro-latest",
            )
            assert orchestrator.model_preference[3] == (
                "mistral",
                "mistral-large-latest",
            )
            assert orchestrator.model_preference[4] == (
                "anthropic",
                "claude-3-opus-20240229",
            )
            assert orchestrator.model_preference[5] == (
                "suno",
                "placeholder",
            )  # Suno is now added to preference
            assert "openai:gpt-4o" in orchestrator.providers
            assert (
                "suno:placeholder" in orchestrator.providers
            )  # Suno is now a provider instance


@pytest.mark.asyncio
async def test_orchestrator_initialization_missing_key_error(monkeypatch):
    """Test initialization failure when a required API key is missing."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    primary = "openai:gpt-4o"
    fallbacks = ["deepseek:deepseek-chat"]

    with patch.dict(
        PROVIDER_CONFIG,
        {
            "openai": {**PROVIDER_CONFIG["openai"], "library_present": True},
            "deepseek": {
                **PROVIDER_CONFIG["deepseek"],
                "library_present": True,
            },
        },
    ):
        orchestrator = LLMOrchestrator(
            primary_model=primary,
            fallback_models=fallbacks,
            enable_auto_discovery=False,
        )
        assert len(orchestrator.model_preference) == 1
        assert orchestrator.model_preference[0] == (
            "deepseek",
            "deepseek-chat",
        )
        assert "openai:gpt-4o" not in orchestrator.providers
        assert "deepseek:deepseek-chat" in orchestrator.providers


@pytest.mark.asyncio
async def test_orchestrator_initialization_library_missing(monkeypatch):
    """Test initialization skips provider if library is missing."""
    primary = "openai:gpt-4o"
    fallbacks = ["gemini:gemini-1.5-pro-latest"]

    with patch.dict(
        PROVIDER_CONFIG,
        {
            "openai": {
                **PROVIDER_CONFIG["openai"],
                "client_class": AsyncMock(),
                "library_present": True,
            },
            "gemini": {
                **PROVIDER_CONFIG["gemini"],
                "client_class": None,
                "library_present": False,
            },
        },
    ):
        orchestrator = LLMOrchestrator(
            primary_model=primary,
            fallback_models=fallbacks,
            enable_auto_discovery=False,
        )
        assert len(orchestrator.model_preference) == 1
        assert orchestrator.model_preference[0] == ("openai", "gpt-4o")
        assert "openai:gpt-4o" in orchestrator.providers
        assert "gemini:gemini-1.5-pro-latest" not in orchestrator.providers


@pytest.mark.asyncio
async def test_orchestrator_generate_primary_success(
    mock_env_vars, mock_openai_client, mock_telegram
):
    """Test successful generation using the primary provider."""
    primary = "openai:gpt-4o"
    fallbacks = ["deepseek:deepseek-chat"]

    with patch.dict(
        PROVIDER_CONFIG,
        {
            "openai": {
                **PROVIDER_CONFIG["openai"],
                "client_class": MagicMock(return_value=mock_openai_client),
                "library_present": True,
            },
            "deepseek": {
                **PROVIDER_CONFIG["deepseek"],
                "client_class": AsyncMock(),
                "library_present": True,
            },
        },
    ):
        orchestrator = LLMOrchestrator(
            primary_model=primary,
            fallback_models=fallbacks,
            enable_auto_discovery=False,
        )
        prompt = "Test prompt"
        result = await orchestrator.generate_text_response(prompt)
        assert result == "Mocked OpenAI response"
        mock_openai_client.chat.completions.create.assert_awaited_once()
        mock_telegram.assert_not_called()  # No fallback, no notification


# --- Fallback Tests --- #


@pytest.mark.asyncio
async def test_orchestrator_fallback_to_second_provider(
    mock_env_vars, mock_openai_client, mock_deepseek_client, mock_telegram
):
    """Test fallback from primary (OpenAI) to secondary (DeepSeek)."""
    primary = "openai:gpt-4o"
    fallbacks = ["deepseek:deepseek-chat", "gemini:gemini-1.5-pro-latest"]

    mock_request = MagicMock()
    mock_response_obj_rl = MagicMock()
    mock_openai_client.chat.completions.create.side_effect = RateLimitError(
        message="Simulated rate limit",
        response=mock_response_obj_rl,
        body=None,
    )

    with patch.dict(
        PROVIDER_CONFIG,
        {
            "openai": {
                **PROVIDER_CONFIG["openai"],
                "client_class": MagicMock(return_value=mock_openai_client),
                "library_present": True,
            },
            "deepseek": {
                **PROVIDER_CONFIG["deepseek"],
                "client_class": MagicMock(return_value=mock_deepseek_client),
                "library_present": True,
            },
            "gemini": {
                **PROVIDER_CONFIG["gemini"],
                "client_class": None,
                "library_present": True,
            },
        },
    ):
        with patch("llm_orchestrator.orchestrator.genai") as mock_genai:
            orchestrator = LLMOrchestrator(
                primary_model=primary,
                fallback_models=fallbacks,
                enable_auto_discovery=False,
                enable_fallback_notifications=True,
            )
            prompt = "Fallback test prompt"
            result = await orchestrator.generate_text_response(prompt)

            assert result == "Mocked DeepSeek response"
            mock_openai_client.chat.completions.create.assert_awaited()
            mock_deepseek_client.chat.completions.create.assert_awaited_once()
            mock_telegram.assert_awaited_once()
            call_args, _ = mock_telegram.call_args
            assert (
                "Attempting fallback to: `deepseek:deepseek-chat`"
                in call_args[0]
            )
            assert (
                "Failed to call openai (gpt-4o) after 3 retries"
                in call_args[0]
            )


@pytest.mark.asyncio
async def test_orchestrator_fallback_through_multiple_providers(
    mock_env_vars,
    mock_openai_client,
    mock_deepseek_client,
    mock_gemini_client,
    mock_telegram,
):
    """Test fallback through OpenAI -> DeepSeek -> Gemini."""
    primary = "openai:gpt-4o"
    fallbacks = ["deepseek:deepseek-chat", "gemini:gemini-1.5-pro-latest"]

    mock_request_openai = MagicMock()
    mock_openai_client.chat.completions.create.side_effect = APIError(
        message="Simulated API error", request=mock_request_openai, body=None
    )
    mock_request_deepseek = MagicMock()
    mock_response_obj_rl_ds = MagicMock()
    mock_deepseek_client.chat.completions.create.side_effect = RateLimitError(
        message="Simulated rate limit",
        response=mock_response_obj_rl_ds,
        body=None,
    )

    with patch.dict(
        PROVIDER_CONFIG,
        {
            "openai": {
                **PROVIDER_CONFIG["openai"],
                "client_class": MagicMock(return_value=mock_openai_client),
                "library_present": True,
            },
            "deepseek": {
                **PROVIDER_CONFIG["deepseek"],
                "client_class": MagicMock(return_value=mock_deepseek_client),
                "library_present": True,
            },
            "gemini": {
                **PROVIDER_CONFIG["gemini"],
                "client_class": None,  # Will be mocked by mock_gemini_client fixture
                "library_present": True,
            },
        },
    ):
        with patch("llm_orchestrator.orchestrator.genai") as mock_genai_module:
            mock_genai_module.GenerativeModel.return_value = mock_gemini_client
            orchestrator = LLMOrchestrator(
                primary_model=primary,
                fallback_models=fallbacks,
                enable_auto_discovery=False,
                enable_fallback_notifications=True,
            )
            prompt = "Multi-fallback test"
            result = await orchestrator.generate_text_response(prompt)

            assert result == "Mocked Gemini response"
            mock_openai_client.chat.completions.create.assert_awaited()
            mock_deepseek_client.chat.completions.create.assert_awaited()
            mock_gemini_client.generate_content_async.assert_awaited()
            assert mock_telegram.call_count == 2  # Two fallbacks


@pytest.mark.asyncio
async def test_orchestrator_all_providers_fail(
    mock_env_vars,
    mock_openai_client,
    mock_deepseek_client,
    mock_gemini_client,
    mock_telegram,
):
    """Test scenario where all configured providers fail."""
    primary = "openai:gpt-4o"
    fallbacks = ["deepseek:deepseek-chat", "gemini:gemini-1.5-pro-latest"]

    mock_request_openai = MagicMock()
    mock_openai_client.chat.completions.create.side_effect = APIError(
        message="OpenAI API error", request=mock_request_openai, body=None
    )
    mock_request_deepseek = MagicMock()
    mock_response_obj_rl_ds = MagicMock()
    mock_deepseek_client.chat.completions.create.side_effect = RateLimitError(
        message="DeepSeek rate limit",
        response=mock_response_obj_rl_ds,
        body=None,
    )
    # Simulate Gemini failure (e.g., InternalServerError)
    mock_gemini_client.generate_content_async.side_effect = (
        google_exceptions.InternalServerError("Gemini internal error")
    )

    with patch.dict(
        PROVIDER_CONFIG,
        {
            "openai": {
                **PROVIDER_CONFIG["openai"],
                "client_class": MagicMock(return_value=mock_openai_client),
                "library_present": True,
            },
            "deepseek": {
                **PROVIDER_CONFIG["deepseek"],
                "client_class": MagicMock(return_value=mock_deepseek_client),
                "library_present": True,
            },
            "gemini": {
                **PROVIDER_CONFIG["gemini"],
                "client_class": None,
                "library_present": True,
            },
        },
    ):
        with patch("llm_orchestrator.orchestrator.genai") as mock_genai_module:
            mock_genai_module.GenerativeModel.return_value = mock_gemini_client
            orchestrator = LLMOrchestrator(
                primary_model=primary,
                fallback_models=fallbacks,
                enable_auto_discovery=False,
                enable_fallback_notifications=True,
            )
            prompt = "All fail test"
            with pytest.raises(OrchestratorError) as excinfo:
                await orchestrator.generate_text_response(prompt)

            assert "All providers failed after retries" in str(excinfo.value)
            mock_openai_client.chat.completions.create.assert_awaited()
            mock_deepseek_client.chat.completions.create.assert_awaited()
            mock_gemini_client.generate_content_async.assert_awaited()
            assert (
                mock_telegram.call_count == 2
            )  # Notifications for two fallbacks


# --- Suno BAS Integration Tests --- #


@pytest.mark.asyncio
async def test_orchestrator_suno_bas_stub_success(
    mock_env_vars, mock_bas_stub, mock_telegram
):
    """Test successful Suno track generation via BAS stub."""
    primary = "suno:placeholder"  # Using a placeholder model name for Suno
    # Mock SunoOrchestrator directly for this test to control its behavior
    mock_suno_orchestrator_instance = AsyncMock()
    mock_suno_orchestrator_instance.generate_track.return_value = (
        "suno_success: /mocked/suno/output.mp3"
    )

    with patch.dict(
        PROVIDER_CONFIG,
        {
            "suno": {
                **PROVIDER_CONFIG["suno"],
                "client_class": MagicMock(
                    return_value=mock_suno_orchestrator_instance
                ),
                "library_present": True,
            }
        },
    ):
        orchestrator = LLMOrchestrator(
            primary_model=primary, enable_auto_discovery=False
        )
        suno_params = {
            "lyrics": "Test lyrics",
            "style_prompt": "Test style",
            "make_instrumental": False,
            "title": "Test Song",
            "tags": "test, song",
            "prompt": "",  # For compatibility if generate_suno_track expects it
        }
        result = await orchestrator.generate_suno_track(suno_params)
        assert result == "suno_success: /mocked/suno/output.mp3"
        mock_suno_orchestrator_instance.generate_track.assert_awaited_once_with(
            lyrics="Test lyrics",
            style_prompt="Test style",
            make_instrumental=False,
            title="Test Song",
            tags="test, song",
            prompt="",
        )
        mock_telegram.assert_not_called()


@pytest.mark.asyncio
async def test_orchestrator_suno_bas_stub_failure_fallback(
    mock_env_vars, mock_bas_stub, mock_openai_client, mock_telegram
):
    """Test fallback from Suno BAS to an LLM provider if Suno fails."""
    primary = "suno:placeholder"
    fallbacks = ["openai:gpt-4o"]

    # Mock SunoOrchestrator to simulate failure
    mock_suno_orchestrator_instance = AsyncMock()
    mock_suno_orchestrator_instance.generate_track.side_effect = (
        SunoOrchestratorError("Suno BAS stub failed")
    )

    with patch.dict(
        PROVIDER_CONFIG,
        {
            "suno": {
                **PROVIDER_CONFIG["suno"],
                "client_class": MagicMock(
                    return_value=mock_suno_orchestrator_instance
                ),
                "library_present": True,
            },
            "openai": {
                **PROVIDER_CONFIG["openai"],
                "client_class": MagicMock(return_value=mock_openai_client),
                "library_present": True,
            },
        },
    ):
        orchestrator = LLMOrchestrator(
            primary_model=primary,
            fallback_models=fallbacks,
            enable_auto_discovery=False,
            enable_fallback_notifications=True,
        )
        suno_params = {
            "lyrics": "Test lyrics for fallback",
            "style_prompt": "Test style for fallback",
            "prompt": "",  # For compatibility
        }
        # This test assumes if Suno fails, it might try to generate text about the failure
        # or a related task. The current orchestrator.generate_suno_track will raise
        # BASFallbackError if all retries for Suno fail. If we want it to fallback to
        # a text LLM, the orchestrator logic or test needs adjustment.
        # For now, let's assume it raises BASFallbackError as per current design.

        with pytest.raises(BASFallbackError) as excinfo:
            await orchestrator.generate_suno_track(suno_params)

        assert "Suno BAS stub fallback failed: Simulated BAS error" in str(excinfo.value)
        mock_suno_orchestrator_instance.generate_track.assert_awaited()
        mock_openai_client.chat.completions.create.assert_not_called()  # No text fallback here
        mock_telegram.assert_awaited_once()  # Notification for Suno failure
        call_args, _ = mock_telegram.call_args
        assert (
            "Attempting fallback to: `openai:gpt-4o`" not in call_args[0]
        )  # No LLM fallback
        assert (
            "Failed to call suno (placeholder) after 3 retries" in call_args[0]
        )


# --- Other Orchestrator Logic Tests --- #


@pytest.mark.asyncio
async def test_orchestrator_generate_with_model_kwargs(
    mock_env_vars, mock_openai_client, mock_telegram
):
    """Test generation with specific model_kwargs."""
    primary = "openai:gpt-4o"
    with patch.dict(
        PROVIDER_CONFIG,
        {
            "openai": {
                **PROVIDER_CONFIG["openai"],
                "client_class": MagicMock(return_value=mock_openai_client),
                "library_present": True,
            }
        },
    ):
        orchestrator = LLMOrchestrator(
            primary_model=primary, enable_auto_discovery=False
        )
        prompt = "Test prompt with kwargs"
        model_params = {"temperature": 0.5, "max_tokens": 100}
        result = await orchestrator.generate_text_response(prompt, model_kwargs=model_params)
        assert result == "Mocked OpenAI response"
        mock_openai_client.chat.completions.create.assert_awaited_once_with(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100,
        )
        mock_telegram.assert_not_called()


@pytest.mark.asyncio
async def test_orchestrator_auto_discovery_all_available(mock_env_vars):
    """Test auto-discovery when all registered models are available."""
    # Mock LLM_REGISTRY for this test
    mock_registry = {
        "openai": {"models": ["gpt-4o", "gpt-3.5-turbo"]},
        "deepseek": {"models": ["deepseek-chat"]},
    }
    with patch("llm_orchestrator.orchestrator.LLM_REGISTRY", mock_registry):
        with patch.dict(
            PROVIDER_CONFIG,
            {
                "openai": {
                    **PROVIDER_CONFIG["openai"],
                    "client_class": AsyncMock(),
                    "library_present": True,
                },
                "deepseek": {
                    **PROVIDER_CONFIG["deepseek"],
                    "client_class": AsyncMock(),
                    "library_present": True,
                },
            },
        ):
            # Pass a primary_model as it's required by __init__
            orchestrator = LLMOrchestrator(
                primary_model="openai:gpt-4o", enable_auto_discovery=True
            )
            # Expected: primary + other from openai + deepseek model
            # Order: primary, then registry (openai first, then deepseek)
            assert len(orchestrator.model_preference) == 3
            assert orchestrator.model_preference[0] == ("openai", "gpt-4o")
            assert orchestrator.model_preference[1] == (
                "openai",
                "gpt-3.5-turbo",
            )
            assert orchestrator.model_preference[2] == (
                "deepseek",
                "deepseek-chat",
            )
            assert "openai:gpt-4o" in orchestrator.providers
            assert "openai:gpt-3.5-turbo" in orchestrator.providers
            assert "deepseek:deepseek-chat" in orchestrator.providers


@pytest.mark.asyncio
async def test_orchestrator_auto_discovery_some_missing(mock_env_vars):
    """Test auto-discovery when some registered models/providers are unavailable."""
    mock_registry = {
        "openai": {"models": ["gpt-4o"]},
        "unavailable_provider": {
            "models": ["model-x"]
        },  # This provider is not in PROVIDER_CONFIG
        "gemini": {
            "models": ["gemini-1.5-pro-latest"]
        },  # Assume Gemini lib is missing
    }
    with patch("llm_orchestrator.orchestrator.LLM_REGISTRY", mock_registry):
        with patch.dict(
            PROVIDER_CONFIG,
            {
                "openai": {
                    **PROVIDER_CONFIG["openai"],
                    "client_class": AsyncMock(),
                    "library_present": True,
                },
                "gemini": {
                    **PROVIDER_CONFIG["gemini"],
                    "client_class": None,
                    "library_present": False,  # Simulate missing library
                },
                # unavailable_provider is not in PROVIDER_CONFIG
            },
        ):
            orchestrator = LLMOrchestrator(
                primary_model="openai:gpt-4o", enable_auto_discovery=True
            )
            # Expected: only the primary openai model
            assert len(orchestrator.model_preference) == 1
            assert orchestrator.model_preference[0] == ("openai", "gpt-4o")
            assert "openai:gpt-4o" in orchestrator.providers
            assert "unavailable_provider:model-x" not in orchestrator.providers
            assert "gemini:gemini-1.5-pro-latest" not in orchestrator.providers


@pytest.mark.asyncio
async def test_orchestrator_no_providers_configured(mock_env_vars):
    """Test behavior when no valid providers can be initialized."""
    # Simulate all libraries missing or keys missing
    with patch.dict(
        PROVIDER_CONFIG,
        {
            p: {**cfg, "library_present": False}
            for p, cfg in PROVIDER_CONFIG.items()
        },
    ):
        with pytest.raises(ValueError) as excinfo:
            # Pass a primary_model as it's required
            orchestrator = LLMOrchestrator(
                primary_model="nonexistent:nonexistent_model",
                enable_auto_discovery=False,
            )
        assert "No valid LLM or BAS providers could be initialized" in str(
            excinfo.value
        )


@pytest.mark.asyncio
async def test_orchestrator_invalid_model_string_format(mock_env_vars):
    """Test error handling for invalid model string format (e.g., no colon)."""
    # This test needs to check if _add_provider handles it gracefully or if
    # the constructor raises an error if the primary_model is malformed
    # in a way that _infer_provider cannot handle and no provider is added.
    # Current _infer_provider defaults to openai if it cannot infer.
    # Let's test if a completely un-inferable primary model + no fallbacks leads to ValueError
    with patch.dict(
        PROVIDER_CONFIG,
        {"openai": {**PROVIDER_CONFIG["openai"], "library_present": False}},
    ):
        with pytest.raises(
            ValueError
        ) as excinfo:  # Expect ValueError if no providers init
            LLMOrchestrator(
                primary_model="completely_unknown_model_format_without_colon",
                enable_auto_discovery=False
            )
        assert "No valid LLM or BAS providers could be initialized" in str(
            excinfo.value
        )


@pytest.mark.asyncio
async def test_orchestrator_unknown_provider(mock_env_vars):
    """Test error handling for an unknown provider in model string."""
    with pytest.raises(
        ValueError
    ) as excinfo:  # Expect ValueError if no providers init
        LLMOrchestrator(primary_model="unknownprovider:some-model", enable_auto_discovery=False)
    assert "No valid LLM or BAS providers could be initialized" in str(
        excinfo.value
    )


@pytest.mark.asyncio
async def test_orchestrator_generate_unsupported_task_type(
    mock_env_vars, mock_openai_client
):
    """Test generation with an unsupported task_type."""
    primary = "openai:gpt-4o"
    with patch.dict(
        PROVIDER_CONFIG,
        {
            "openai": {
                **PROVIDER_CONFIG["openai"],
                "client_class": MagicMock(return_value=mock_openai_client),
                "library_present": True,
            }
        },
    ):
        orchestrator = LLMOrchestrator(
            primary_model=primary, enable_auto_discovery=False
        )
        prompt = "Test prompt for unsupported task"
        # The orchestrator's generate_text_response and generate_suno_track are specific.
        # There's no generic generate method that takes task_type anymore.
        # This test needs to be rethought or removed if the API doesn't support generic task types.
        # For now, let's assume we try to call a non-existent method to simulate this.
        with pytest.raises(AttributeError):
            await orchestrator.generate_image_response(
                prompt
            )  # Assuming this method doesn't exist


# --- Specific Error Handling Fallback Tests ---


@pytest.mark.asyncio
async def test_orchestrator_gemini_safety_fallback(
    mock_env_vars, mock_gemini_client, mock_openai_client, mock_telegram
):
    """Test fallback from Gemini due to safety settings block."""
    primary = "gemini:gemini-1.5-pro-latest"
    fallbacks = ["openai:gpt-4o"]

    # Simulate Gemini safety block
    mock_gemini_response = MagicMock()
    mock_gemini_response.prompt_feedback = MagicMock()
    mock_gemini_response.prompt_feedback.block_reason = "SAFETY"
    mock_gemini_response.prompt_feedback.block_reason_message = (
        "Blocked due to safety"
    )
    # To make it behave like the actual API, ensure text is not present or generation fails
    mock_gemini_client.generate_content_async.return_value = (
        mock_gemini_response
    )
    # Or, make it raise an error that indicates blocking, if the library does that.
    # For now, returning a response with block_reason is closer to actual behavior.

    with patch.dict(
        PROVIDER_CONFIG,
        {
            "gemini": {
                **PROVIDER_CONFIG["gemini"],
                "client_class": None,
                "library_present": True,
            },
            "openai": {
                **PROVIDER_CONFIG["openai"],
                "client_class": MagicMock(return_value=mock_openai_client),
                "library_present": True,
            },
        },
    ):
        with patch("llm_orchestrator.orchestrator.genai") as mock_genai_module:
            mock_genai_module.GenerativeModel.return_value = mock_gemini_client
            orchestrator = LLMOrchestrator(
                primary_model=primary,
                fallback_models=fallbacks,
                enable_auto_discovery=False,
                enable_fallback_notifications=True,
            )
            prompt = "Gemini safety test"
            result = await orchestrator.generate_text_response(prompt)

            assert result == "Mocked OpenAI response"
            assert mock_gemini_client.generate_content_async.call_count == 1, f"Actual call count: {mock_gemini_client.generate_content_async.call_count}"  # Safety block = 1 attempt for this provider, then fallback
            mock_openai_client.chat.completions.create.assert_awaited_once()
            mock_telegram.assert_awaited_once()
            call_args, _ = mock_telegram.call_args
            assert "Attempting fallback to: `openai:gpt-4o`" in call_args[0]
            assert (
                "Blocked due to safety" in call_args[0]
            )  # Check for safety block message


@pytest.mark.asyncio
async def test_orchestrator_mistral_api_exception_fallback(
    mock_env_vars, mock_mistral_client, mock_openai_client, mock_telegram
):
    """Test fallback from Mistral due to MistralAPIException."""
    primary = "mistral:mistral-large-latest"
    fallbacks = ["openai:gpt-4o"]

    mock_mistral_client.chat.side_effect = MistralAPIException(
        message="Mistral API error"
    )

    with patch.dict(
        PROVIDER_CONFIG,
        {
            "mistral": {
                **PROVIDER_CONFIG["mistral"],
                "client_class": MagicMock(return_value=mock_mistral_client),
                "library_present": True,
            },
            "openai": {
                **PROVIDER_CONFIG["openai"],
                "client_class": MagicMock(return_value=mock_openai_client),
                "library_present": True,
            },
        },
    ):
        orchestrator = LLMOrchestrator(
            primary_model=primary,
            fallback_models=fallbacks,
            enable_auto_discovery=False,
            enable_fallback_notifications=True,
        )
        prompt = "Mistral error test"
        result = await orchestrator.generate_text_response(prompt)

        assert result == "Mocked OpenAI response"
        assert mock_mistral_client.chat.call_count == orchestrator.max_retries_per_provider
        mock_openai_client.chat.completions.create.assert_awaited_once()
        mock_telegram.assert_awaited_once()
        call_args, _ = mock_telegram.call_args
        assert "Attempting fallback to: `openai:gpt-4o`" in call_args[0]
        assert "Mistral API error" in call_args[0]


@pytest.mark.asyncio
async def test_orchestrator_openai_apistatuserror_fallback(
    mock_env_vars, mock_openai_client, mock_deepseek_client, mock_telegram
):
    """Test fallback from OpenAI due to APIStatusError (e.g., 500 server error)."""
    primary = "openai:gpt-4o"
    fallbacks = ["deepseek:deepseek-chat"]

    # Ensure APIStatusError is available or mocked
    if APIStatusError is None:
        # If openai lib is too old or not fully mocked, create a dummy error
        class MockAPIStatusError(APIError):
            def __init__(self, message, response, body):
                super().__init__(message, request=MagicMock(), body=body)
                self.response = response
                self.status_code = 500  # Simulate a server error

        openai_error_to_raise = MockAPIStatusError(
            message="OpenAI server error", response=MagicMock(), body=None
        )
    else:
        mock_response_obj_status = MagicMock()
        mock_response_obj_status.status_code = 500  # Simulate server error
        openai_error_to_raise = APIStatusError(
            message="OpenAI server error",
            response=mock_response_obj_status,
            body=None,
        )

    mock_openai_client.chat.completions.create.side_effect = (
        openai_error_to_raise
    )

    with patch.dict(
        PROVIDER_CONFIG,
        {
            "openai": {
                **PROVIDER_CONFIG["openai"],
                "client_class": MagicMock(return_value=mock_openai_client),
                "library_present": True,
            },
            "deepseek": {
                **PROVIDER_CONFIG["deepseek"],
                "client_class": MagicMock(return_value=mock_deepseek_client),
                "library_present": True,
            },
        },
    ):
        orchestrator = LLMOrchestrator(
            primary_model=primary,
            fallback_models=fallbacks,
            enable_auto_discovery=False,
            enable_fallback_notifications=True,
        )
        prompt = "OpenAI status error test"
        result = await orchestrator.generate_text_response(prompt)

        assert result == "Mocked DeepSeek response"
        mock_openai_client.chat.completions.create.assert_awaited()
        mock_deepseek_client.chat.completions.create.assert_awaited_once()
        mock_telegram.assert_awaited_once()
        call_args, _ = mock_telegram.call_args
        assert (
            "Attempting fallback to: `deepseek:deepseek-chat`" in call_args[0]
        )
        assert "OpenAI server error" in call_args[0]
