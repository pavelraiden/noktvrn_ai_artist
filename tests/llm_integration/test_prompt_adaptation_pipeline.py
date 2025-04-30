"""
Tests for the PromptAdaptationPipeline class.

Uses pytest and pytest-asyncio.
Mocks the LLMOrchestrator interactions.
"""

import pytest
from unittest.mock import patch, AsyncMock

# Adjust import path based on test file location
from ...ai_artist_system.noktvrn_ai_artist.artist_builder.prompt_adaptation.prompt_adaptation_pipeline import PromptAdaptationPipeline

# Mock environment variables needed by LLMOrchestrator
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")
    monkeypatch.setenv("OPENAI_MODEL_NAME", "gpt-test-model")

@pytest.fixture
def mock_llm_orchestrator():
    """Provides a mock LLMOrchestrator."""
    orchestrator_instance = AsyncMock()
    return orchestrator_instance

@pytest.fixture
@patch("ai_artist_system.noktvrn_ai_artist.artist_builder.prompt_adaptation.prompt_adaptation_pipeline.LLMOrchestrator")
def prompt_adapter(MockLLMOrchestrator, mock_llm_orchestrator):
    """Provides an instance of PromptAdaptationPipeline with mocked LLMOrchestrator."""
    # Configure the mock LLMOrchestrator class to return our instance
    MockLLMOrchestrator.return_value = mock_llm_orchestrator
    return PromptAdaptationPipeline()

@pytest.mark.asyncio
async def test_adapt_prompt_success(prompt_adapter, mock_llm_orchestrator):
    """Test successful prompt adaptation."""
    original_prompt = "Write a song about a cat."
    instructions = "Make it a sad song."
    context = {"mood": "gloomy"}
    adapted_prompt_llm_output = "Write a melancholic song about a lonely cat watching the rain."

    # Mock LLM call
    mock_llm_orchestrator.adapt_prompt.return_value = adapted_prompt_llm_output

    result = await prompt_adapter.adapt_artist_prompt(
        original_prompt=original_prompt,
        adaptation_instructions=instructions,
        context=context
    )

    assert result == adapted_prompt_llm_output
    # Verify LLM call
    mock_llm_orchestrator.adapt_prompt.assert_awaited_once_with(
        original_prompt=original_prompt,
        adaptation_instructions=instructions,
        context=context,
        max_tokens=1024, # Default value
        temperature=0.7  # Default value
    )

@pytest.mark.asyncio
async def test_adapt_prompt_llm_fails(prompt_adapter, mock_llm_orchestrator):
    """Test prompt adaptation fails if the LLM call fails."""
    original_prompt = "Write a song about a dog."
    instructions = "Make it happy."

    # Mock LLM call failure
    mock_llm_orchestrator.adapt_prompt.side_effect = Exception("LLM API Error")

    result = await prompt_adapter.adapt_artist_prompt(
        original_prompt=original_prompt,
        adaptation_instructions=instructions
    )

    assert result is None
    mock_llm_orchestrator.adapt_prompt.assert_awaited_once() # LLM was called

@pytest.mark.asyncio
async def test_adapt_prompt_with_different_params(prompt_adapter, mock_llm_orchestrator):
    """Test prompt adaptation with non-default parameters."""
    original_prompt = "Verse 1: ..."
    instructions = "Add a chorus."
    adapted_prompt_llm_output = "Verse 1: ... Chorus: ..."
    custom_max_tokens = 2048
    custom_temperature = 0.9

    # Mock LLM call
    mock_llm_orchestrator.adapt_prompt.return_value = adapted_prompt_llm_output

    result = await prompt_adapter.adapt_artist_prompt(
        original_prompt=original_prompt,
        adaptation_instructions=instructions,
        max_tokens=custom_max_tokens,
        temperature=custom_temperature
    )

    assert result == adapted_prompt_llm_output
    # Verify LLM call with custom parameters
    mock_llm_orchestrator.adapt_prompt.assert_awaited_once_with(
        original_prompt=original_prompt,
        adaptation_instructions=instructions,
        context=None, # No context passed
        max_tokens=custom_max_tokens,
        temperature=custom_temperature
    )

