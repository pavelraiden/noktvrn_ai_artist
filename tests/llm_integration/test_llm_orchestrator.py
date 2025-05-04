"""
Tests for the LLMOrchestrator class.

Uses pytest and pytest-asyncio.
Mocks the OpenAI API calls to avoid actual API interaction during testing.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
import sys  # Added
import os  # Added

# --- Add project root to sys.path for imports ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# Assuming tests are run from the project root
from llm_orchestrator.orchestrator import LLMOrchestrator, LLMOrchestratorError


# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")
    monkeypatch.setenv("OPENAI_MODEL_NAME", "gpt-test-model")
    # Mock other potential env vars used by orchestrator if needed
    monkeypatch.setenv(
        "LLM_FALLBACK_MODELS", "fallback-model-1,fallback-model-2"
    )
    monkeypatch.setenv("LLM_MAX_RETRIES", "3")
    monkeypatch.setenv("LLM_INITIAL_DELAY", "1")
    monkeypatch.setenv("LLM_MAX_DELAY", "10")
    monkeypatch.setenv("LLM_TIMEOUT", "60")


# Mock response structure similar to OpenAI's ChatCompletion
class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)


class MockMessage:
    def __init__(self, content):
        self.content = content


class MockUsage:
    def __init__(
        self, prompt_tokens=10, completion_tokens=20, total_tokens=30
    ):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class MockChatCompletion:
    def __init__(self, content="Mocked response content", usage=None):
        self.choices = [MockChoice(content)]
        self.usage = usage or MockUsage()


@pytest.fixture
def orchestrator():
    """Provides an instance of LLMOrchestrator for testing."""
    # Ensure orchestrator uses mocked env vars
    return LLMOrchestrator(
        primary_model="gpt-test-model",
        fallback_models=["fallback-model-1", "fallback-model-2"],
        max_retries=2,  # Override for specific tests if needed
        initial_delay=0.1,  # Override for specific tests if needed
    )


@pytest.mark.asyncio
@patch(
    "openai.AsyncOpenAI", new_callable=AsyncMock
)  # Mock the AsyncOpenAI class
async def test_generate_text_success(mock_async_openai_class, orchestrator):
    """Test successful text generation."""
    mock_client_instance = mock_async_openai_class.return_value
    mock_client_instance.chat.completions.create.return_value = (
        MockChatCompletion(content=" Successful generation ")
    )

    prompt = "Generate a short story."
    result = await orchestrator.generate_text(prompt)

    assert result == "Successful generation"
    mock_client_instance.chat.completions.create.assert_awaited_once()
    call_args = mock_client_instance.chat.completions.create.call_args[1]
    assert call_args["model"] == "gpt-test-model"
    assert call_args["messages"] == [{"role": "user", "content": prompt}]


@pytest.mark.asyncio
@patch("openai.AsyncOpenAI", new_callable=AsyncMock)
async def test_adapt_prompt_success(mock_async_openai_class, orchestrator):
    """Test successful prompt adaptation."""
    mock_client_instance = mock_async_openai_class.return_value
    mock_client_instance.chat.completions.create.return_value = (
        MockChatCompletion(content=" ```Adapted prompt content``` ")
    )

    original = "Original prompt."
    instructions = "Make it better."
    context = {"key": "value"}

    result = await orchestrator.adapt_prompt(original, instructions, context)

    assert result == "Adapted prompt content"
    mock_client_instance.chat.completions.create.assert_awaited_once()
    call_args = mock_client_instance.chat.completions.create.call_args[1]
    # Check parts of the system prompt construction
    system_prompt = call_args["messages"][0]["content"]
    assert "INSTRUCTIONS:\nMake it better." in system_prompt
    assert "ORIGINAL PROMPT:\n```\nOriginal prompt.\n```" in system_prompt
    assert (
        'Relevant Context:\n```json\n{\n    "key": "value"\n}\n```'
        in system_prompt
    )


@pytest.mark.asyncio
@patch("openai.AsyncOpenAI", new_callable=AsyncMock)
async def test_evolve_description_success(
    mock_async_openai_class, orchestrator
):
    """Test successful description evolution."""
    mock_client_instance = mock_async_openai_class.return_value
    mock_client_instance.chat.completions.create.return_value = (
        MockChatCompletion(content=" Evolved description content ")
    )

    current = "Current description."
    goal = "Make it more evolved."
    context = {"trend": "up"}

    result = await orchestrator.evolve_description(current, goal, context)

    assert result == "Evolved description content"
    mock_client_instance.chat.completions.create.assert_awaited_once()
    call_args = mock_client_instance.chat.completions.create.call_args[1]
    system_prompt = call_args["messages"][0]["content"]
    assert "EVOLUTION GOAL:\nMake it more evolved." in system_prompt
    assert (
        "CURRENT ARTIST DESCRIPTION:\n```\nCurrent description.\n```"
        in system_prompt
    )
    assert (
        'Relevant Context:\n```json\n{\n    "trend": "up"\n}\n```'
        in system_prompt
    )


@pytest.mark.asyncio
@patch("openai.AsyncOpenAI", new_callable=AsyncMock)
async def test_llm_call_retry_on_rate_limit(
    mock_async_openai_class, orchestrator
):
    """Test retry logic on RateLimitError."""
    mock_client_instance = mock_async_openai_class.return_value

    # Dynamically get RateLimitError if available, otherwise use generic Exception
    try:
        from openai import RateLimitError
    except ImportError:
        RateLimitError = Exception  # Fallback if specific error not found

    # Simulate RateLimitError on first call, success on second
    mock_client_instance.chat.completions.create.side_effect = [
        RateLimitError(
            "Rate limit exceeded",
            response=AsyncMock(),  # Mock response object
            body=None,  # Mock body
        ),
        MockChatCompletion(content="Success after retry"),
    ]

    # Reduce retry settings for faster test (already done in fixture, but can override)
    orchestrator.max_retries = 2
    orchestrator.initial_delay = 0.1

    prompt = "Test retry"
    result = await orchestrator.generate_text(prompt)

    assert result == "Success after retry"
    assert mock_client_instance.chat.completions.create.call_count == 2


@pytest.mark.asyncio
@patch("openai.AsyncOpenAI", new_callable=AsyncMock)
async def test_llm_call_fail_after_retries(
    mock_async_openai_class, orchestrator
):
    """Test failure after exhausting retries."""
    mock_client_instance = mock_async_openai_class.return_value

    # Dynamically get RateLimitError if available, otherwise use generic Exception
    try:
        from openai import RateLimitError
    except ImportError:
        RateLimitError = (
            LLMOrchestratorError  # Use the orchestrator's base error
        )

    # Simulate RateLimitError on all calls
    mock_client_instance.chat.completions.create.side_effect = RateLimitError(
        "Rate limit exceeded",
        response=AsyncMock(),  # Mock response object
        body=None,  # Mock body
    )

    # Reduce retry settings for faster test
    orchestrator.max_retries = 2
    orchestrator.initial_delay = 0.1

    prompt = "Test failure"
    # Expect the orchestrator's base error after retries fail
    with pytest.raises(
        LLMOrchestratorError, match="LLM call failed after 2 retries"
    ):
        await orchestrator.generate_text(prompt)

    # Call count should be max_retries + 1 (initial call + retries)
    assert mock_client_instance.chat.completions.create.call_count == 3


@pytest.mark.asyncio
async def test_orchestrator_init_no_api_key(monkeypatch):
    """Test orchestrator initialization fails without API key."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    # The orchestrator might fall back to other providers or raise later
    # Depending on implementation, this might not raise ValueError immediately
    # Let's test a call instead
    with pytest.raises(
        ValueError, match="API key is missing for provider: openai"
    ):
        orchestrator_no_key = LLMOrchestrator()
        # This call should fail if OpenAI is the only provider configured/available
        # await orchestrator_no_key.generate_text("test")
        # Or check internal state if possible
        orchestrator_no_key._get_client_for_model("gpt-test-model")


# Add more tests for fallback logic, different error types, etc.
