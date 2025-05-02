"""
Tests for the LLMOrchestrator class.

Uses pytest and pytest-asyncio.
Mocks the OpenAI API calls to avoid actual API interaction during testing.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock

# Adjust the import path based on the test file location relative to the source code
# Assuming tests/llm_integration/test_llm_orchestrator.py
from ...ai_artist_system.noktvrn_ai_artist.llm_orchestrator.orchestrator import (
    LLMOrchestrator,
)


# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")
    monkeypatch.setenv("OPENAI_MODEL_NAME", "gpt-test-model")


# Mock response structure similar to OpenAI's ChatCompletion
class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)


class MockMessage:
    def __init__(self, content):
        self.content = content


class MockUsage:
    def __init__(self, prompt_tokens=10, completion_tokens=20, total_tokens=30):
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
    return LLMOrchestrator()


@pytest.mark.asyncio
@patch("openai.AsyncOpenAI", new_callable=AsyncMock)  # Mock the AsyncOpenAI class
async def test_generate_text_success(mock_async_openai_class, orchestrator):
    """Test successful text generation."""
    mock_client_instance = mock_async_openai_class.return_value
    mock_client_instance.chat.completions.create.return_value = MockChatCompletion(
        content=" Successful generation "
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
    mock_client_instance.chat.completions.create.return_value = MockChatCompletion(
        content=" ```Adapted prompt content``` "
    )

    original = "Original prompt."
    instructions = "Make it better."
    context = {"key": "value"}

    result = await orchestrator.adapt_prompt(original, instructions, context)

    assert result == "Adapted prompt content"
    mock_client_instance.chat.completions.create.assert_awaited_once()
    call_args = mock_client_instance.chat.completions.create.call_args[1]
    assert "INSTRUCTIONS:\nMake it better." in call_args["messages"][0]["content"]
    assert (
        "ORIGINAL PROMPT:\n```\nOriginal prompt.\n```"
        in call_args["messages"][0]["content"]
    )
    assert (
        "Relevant Context:\n```json\n{'key': 'value'}\n```"
        in call_args["messages"][0]["content"]
    )


@pytest.mark.asyncio
@patch("openai.AsyncOpenAI", new_callable=AsyncMock)
async def test_evolve_description_success(mock_async_openai_class, orchestrator):
    """Test successful description evolution."""
    mock_client_instance = mock_async_openai_class.return_value
    mock_client_instance.chat.completions.create.return_value = MockChatCompletion(
        content=" Evolved description content "
    )

    current = "Current description."
    goal = "Make it more evolved."
    context = {"trend": "up"}

    result = await orchestrator.evolve_description(current, goal, context)

    assert result == "Evolved description content"
    mock_client_instance.chat.completions.create.assert_awaited_once()
    call_args = mock_client_instance.chat.completions.create.call_args[1]
    assert (
        "EVOLUTION GOAL:\nMake it more evolved." in call_args["messages"][0]["content"]
    )
    assert (
        "CURRENT ARTIST DESCRIPTION:\n```\nCurrent description.\n```"
        in call_args["messages"][0]["content"]
    )
    assert (
        "Relevant Context:\n```json\n{'trend': 'up'}\n```"
        in call_args["messages"][0]["content"]
    )


@pytest.mark.asyncio
@patch("openai.AsyncOpenAI", new_callable=AsyncMock)
async def test_llm_call_retry_on_rate_limit(mock_async_openai_class, orchestrator):
    """Test retry logic on RateLimitError."""
    mock_client_instance = mock_async_openai_class.return_value

    # Simulate RateLimitError on first call, success on second
    mock_client_instance.chat.completions.create.side_effect = [
        # Use the actual RateLimitError if available, otherwise a generic Exception
        getattr(
            __import__("openai", fromlist=["RateLimitError"]),
            "RateLimitError",
            Exception,
        )("Rate limit exceeded"),
        MockChatCompletion(content="Success after retry"),
    ]

    # Reduce retry settings for faster test
    orchestrator.max_retries = 2
    orchestrator.initial_delay = 0.1

    prompt = "Test retry"
    result = await orchestrator.generate_text(prompt)

    assert result == "Success after retry"
    assert mock_client_instance.chat.completions.create.call_count == 2


@pytest.mark.asyncio
@patch("openai.AsyncOpenAI", new_callable=AsyncMock)
async def test_llm_call_fail_after_retries(mock_async_openai_class, orchestrator):
    """Test failure after exhausting retries."""
    mock_client_instance = mock_async_openai_class.return_value

    # Simulate RateLimitError on all calls
    RateLimitError = getattr(
        __import__("openai", fromlist=["RateLimitError"]), "RateLimitError", Exception
    )
    mock_client_instance.chat.completions.create.side_effect = RateLimitError(
        "Rate limit exceeded"
    )

    # Reduce retry settings for faster test
    orchestrator.max_retries = 2
    orchestrator.initial_delay = 0.1

    prompt = "Test failure"
    with pytest.raises(RateLimitError):  # Expect the specific error after retries
        await orchestrator.generate_text(prompt)

    assert mock_client_instance.chat.completions.create.call_count == 2


@pytest.mark.asyncio
async def test_orchestrator_init_no_api_key(monkeypatch):
    """Test orchestrator initialization fails without API key."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
        LLMOrchestrator()
