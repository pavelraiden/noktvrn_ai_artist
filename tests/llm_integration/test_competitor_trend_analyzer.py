"""
Tests for the CompetitorTrendAnalyzer class.

Uses pytest and pytest-asyncio.
Mocks the LLMOrchestrator and DatabaseConnectionManager interactions.
"""

import pytest
from unittest.mock import patch, AsyncMock # Removed MagicMock

# Adjust import path based on test file location
from ...ai_artist_system.noktvrn_ai_artist.artist_builder.trend_analyzer.competitor_trend_analyzer import (
    CompetitorTrendAnalyzer,
)


# Mock environment variables needed by LLMOrchestrator
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")
    monkeypatch.setenv("OPENAI_MODEL_NAME", "gpt-test-model")


@pytest.fixture
def mock_db_manager():
    """Provides a mock DatabaseConnectionManager."""
    manager = AsyncMock()
    conn = AsyncMock()
    cur = AsyncMock()
    manager.get_connection.return_value.__aenter__.return_value = conn
    conn.cursor.return_value.__aenter__.return_value = cur
    return manager, cur  # Return manager and cursor for setting expectations


@pytest.fixture
def mock_llm_orchestrator():
    """Provides a mock LLMOrchestrator."""
    orchestrator_instance = AsyncMock()
    return orchestrator_instance


@pytest.fixture
@patch(
    "ai_artist_system.noktvrn_ai_artist.artist_builder.trend_analyzer.competitor_trend_analyzer.LLMOrchestrator"
)
def trend_analyzer(
    MockLLMOrchestrator, mock_db_manager, mock_llm_orchestrator
):
    """Provides an instance of CompetitorTrendAnalyzer with mocked dependencies."""
    # Configure the mock LLMOrchestrator class to return our instance
    MockLLMOrchestrator.return_value = mock_llm_orchestrator
    db_manager, _ = mock_db_manager
    return CompetitorTrendAnalyzer(db_manager=db_manager)


# Sample competitor data for mocking DB response
MOCK_COMPETITOR_DATA = [
    {
        "competitor_id": "comp1",
        "data": {
            "genre": "Synthwave",
            "country_code": "US",
            "strategy_notes": "Focuses on retro visuals",
        },
    },
    {
        "competitor_id": "comp2",
        "data": {
            "genre": "Synthwave",
            "country_code": "US",
            "strategy_notes": "Collaborates with influencers",
        },
    },
]


@pytest.mark.asyncio
async def test_summarize_strategies_success(
    trend_analyzer, mock_db_manager, mock_llm_orchestrator
):
    """Test successful summarization of competitor strategies."""
    db_manager, mock_cursor = mock_db_manager
    artist_id = "artist_xyz"
    genre = "Synthwave"
    country = "US"
    llm_summary = (
        "- Competitor 1 uses retro visuals.\n- Competitor 2 uses influencers."
    )

    # Mock DB fetch
    mock_cursor.fetchall.return_value = [
        ("comp1", MOCK_COMPETITOR_DATA[0]["data"]),
        ("comp2", MOCK_COMPETITOR_DATA[1]["data"]),
    ]
    # Mock LLM call
    mock_llm_orchestrator.generate_text.return_value = llm_summary

    result = await trend_analyzer.summarize_competitor_strategies(
        artist_id, genre, country
    )

    assert result == llm_summary
    # Verify DB fetch call
    mock_cursor.execute.assert_awaited_once()
    assert genre in mock_cursor.execute.call_args[0][1]
    assert country in mock_cursor.execute.call_args[0][1]
    # Verify LLM call
    mock_llm_orchestrator.generate_text.assert_awaited_once()
    prompt_arg = mock_llm_orchestrator.generate_text.call_args[1]["prompt"]
    assert "Summarize the key strategies" in prompt_arg
    assert "Competitor Data:" in prompt_arg
    assert "comp1" in prompt_arg
    assert "comp2" in prompt_arg


@pytest.mark.asyncio
async def test_identify_gaps_success(
    trend_analyzer, mock_db_manager, mock_llm_orchestrator
):
    """Test successful identification of market gaps."""
    db_manager, mock_cursor = mock_db_manager
    artist_id = "artist_xyz"
    genre = "Synthwave"
    country = "US"
    llm_gap_analysis = "Potential gap: Synthwave with live instrumentation."

    # Mock DB fetch
    mock_cursor.fetchall.return_value = [
        ("comp1", MOCK_COMPETITOR_DATA[0]["data"]),
        ("comp2", MOCK_COMPETITOR_DATA[1]["data"]),
    ]
    # Mock LLM call
    mock_llm_orchestrator.generate_text.return_value = llm_gap_analysis

    result = await trend_analyzer.identify_market_gaps(
        artist_id, genre, country
    )

    assert result == llm_gap_analysis
    # Verify DB fetch call
    mock_cursor.execute.assert_awaited_once()
    # Verify LLM call
    mock_llm_orchestrator.generate_text.assert_awaited_once()
    prompt_arg = mock_llm_orchestrator.generate_text.call_args[1]["prompt"]
    assert "identify potential market gaps" in prompt_arg
    assert "Competitor Data:" in prompt_arg


@pytest.mark.asyncio
async def test_summarize_strategies_no_data(
    trend_analyzer, mock_db_manager, mock_llm_orchestrator
):
    """Test summarization returns message when no competitor data is found."""
    db_manager, mock_cursor = mock_db_manager
    artist_id = "artist_xyz"
    genre = "ObscureGenre"
    country = "US"

    # Mock DB fetch returning no data
    mock_cursor.fetchall.return_value = []

    result = await trend_analyzer.summarize_competitor_strategies(
        artist_id, genre, country
    )

    assert result == "No competitor data available for summarization."
    mock_llm_orchestrator.generate_text.assert_not_awaited()  # LLM should not be called


@pytest.mark.asyncio
async def test_identify_gaps_no_data(
    trend_analyzer, mock_db_manager, mock_llm_orchestrator
):
    """Test gap analysis returns message when no competitor data is found."""
    db_manager, mock_cursor = mock_db_manager
    artist_id = "artist_xyz"
    genre = "ObscureGenre"
    country = "US"

    # Mock DB fetch returning no data
    mock_cursor.fetchall.return_value = []

    result = await trend_analyzer.identify_market_gaps(
        artist_id, genre, country
    )

    assert result == "No competitor data available for market gap analysis."
    mock_llm_orchestrator.generate_text.assert_not_awaited()  # LLM should not be called


@pytest.mark.asyncio
async def test_summarize_strategies_llm_fails(
    trend_analyzer, mock_db_manager, mock_llm_orchestrator
):
    """Test summarization returns None if LLM call fails."""
    db_manager, mock_cursor = mock_db_manager
    artist_id = "artist_xyz"
    genre = "Synthwave"
    country = "US"

    # Mock DB fetch success
    mock_cursor.fetchall.return_value = [
        ("comp1", MOCK_COMPETITOR_DATA[0]["data"])
    ]
    # Mock LLM call failure
    mock_llm_orchestrator.generate_text.side_effect = Exception(
        "LLM API Error"
    )

    result = await trend_analyzer.summarize_competitor_strategies(
        artist_id, genre, country
    )

    assert result is None
    mock_llm_orchestrator.generate_text.assert_awaited_once()  # LLM was called


@pytest.mark.asyncio
async def test_identify_gaps_llm_fails(
    trend_analyzer, mock_db_manager, mock_llm_orchestrator
):
    """Test gap analysis returns None if LLM call fails."""
    db_manager, mock_cursor = mock_db_manager
    artist_id = "artist_xyz"
    genre = "Synthwave"
    country = "US"

    # Mock DB fetch success
    mock_cursor.fetchall.return_value = [
        ("comp1", MOCK_COMPETITOR_DATA[0]["data"])
    ]
    # Mock LLM call failure
    mock_llm_orchestrator.generate_text.side_effect = Exception(
        "LLM API Error"
    )

    result = await trend_analyzer.identify_market_gaps(
        artist_id, genre, country
    )

    assert result is None
    mock_llm_orchestrator.generate_text.assert_awaited_once()  # LLM was called


@pytest.mark.asyncio
@patch(
    "ai_artist_system.noktvrn_ai_artist.artist_builder.trend_analyzer.competitor_trend_analyzer.LLMOrchestrator",
    None,
)  # Simulate LLMOrchestrator import failure
def test_analyzer_init_no_llm(mock_db_manager):
    """Test analyzer initialization works but logs warning if LLMOrchestrator
    is unavailable."""
    db_manager, _ = mock_db_manager
    # Should not raise an error, but llm_orchestrator should be None
    analyzer = CompetitorTrendAnalyzer(db_manager=db_manager)
    assert analyzer.llm_orchestrator is None


@pytest.mark.asyncio
async def test_summarize_strategies_no_llm_support(
    trend_analyzer, mock_db_manager
):
    """Test summarization returns warning if LLM support is disabled."""
    # Manually disable LLM support for this test instance
    trend_analyzer.llm_orchestrator = None
    db_manager, mock_cursor = mock_db_manager
    artist_id = "artist_xyz"
    genre = "Synthwave"
    country = "US"

    result = await trend_analyzer.summarize_competitor_strategies(
        artist_id, genre, country
    )

    assert result is None  # Should return None when LLM is disabled
    # DB fetch might still happen depending on implementation, but LLM call
    # shouldn't

