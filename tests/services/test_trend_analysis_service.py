# /home/ubuntu/ai_artist_system_clone/tests/services/test_trend_analysis_service.py
"""Unit tests for the Trend Analysis Service."""

import pytest
import os
import sys
import json

# Add project root to sys.path to allow importing services
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

# Mock the data_api module before importing the service
# This prevents the service from trying to import the real ApiClient during test collection
from unittest.mock import Mock

sys.modules["data_api"] = Mock()

# Now import the service
from services.trend_analysis_service import TrendAnalysisService

# --- Test Setup and Fixtures ---


@pytest.fixture
def mock_api_client(mocker):
    """Fixture to mock the ApiClient and its call_api method."""
    mock_client_instance = mocker.Mock()
    # Configure the mock call_api to return a default successful response
    mock_client_instance.call_api.return_value = {
        "result": {
            "timeline": {
                "instructions": [
                    {
                        "entries": [
                            {
                                "content": {"entryType": "TimelineTimelineItem"}
                            },  # Tweet 1
                            {
                                "content": {"entryType": "TimelineTimelineItem"}
                            },  # Tweet 2
                            {
                                "content": {"entryType": "TimelineTimelineCursor"}
                            },  # Cursor
                        ]
                    }
                ]
            }
        }
    }
    # Patch the ApiClient class within the trend_analysis_service module
    mocker.patch(
        "services.trend_analysis_service.ApiClient", return_value=mock_client_instance
    )
    return mock_client_instance


@pytest.fixture
def trend_service(mock_api_client):  # Depends on the mock_api_client fixture
    """Provides an instance of the TrendAnalysisService with a mocked ApiClient."""
    # The ApiClient is already patched by mock_api_client fixture
    service = TrendAnalysisService()
    # Attach the mock client instance for inspection if needed
    service.mock_api_client = mock_api_client
    return service


# --- Test Cases ---


def test_service_initialization(trend_service):
    """Test that the service initializes correctly."""
    assert trend_service is not None
    assert hasattr(trend_service, "api_client")
    # Check if the mocked client was used
    assert trend_service.api_client == trend_service.mock_api_client


def test_get_twitter_trends_success(trend_service):
    """Test fetching trends successfully using the mocked API."""
    query = "#TestTrend"
    count = 10
    search_type = "Latest"

    # The mock_api_client is pre-configured to return a successful response
    response = trend_service.get_twitter_trends(
        query=query, count=count, search_type=search_type
    )

    # Assert that call_api was called with the correct arguments
    trend_service.mock_api_client.call_api.assert_called_once_with(
        "Twitter/search_twitter",
        query={"query": query, "count": count, "type": search_type},
    )

    # Assert that the response matches the mocked return value
    assert response is not None
    assert "result" in response
    assert "timeline" in response["result"]


def test_calculate_trend_score_success(trend_service):
    """Test calculating the trend score from a mocked successful response."""
    # Use the default mocked response from the fixture
    mock_response = trend_service.mock_api_client.call_api.return_value

    score = trend_service.calculate_trend_score(mock_response)

    # Based on the default mock response (2 tweet items)
    assert score == 2


def test_calculate_trend_score_no_tweets(trend_service):
    """Test calculating score when the response contains no tweet entries."""
    mock_response_no_tweets = {
        "result": {
            "timeline": {
                "instructions": [
                    {
                        "entries": [
                            {
                                "content": {"entryType": "TimelineTimelineCursor"}
                            }  # Only cursor
                        ]
                    }
                ]
            }
        }
    }
    score = trend_service.calculate_trend_score(mock_response_no_tweets)
    assert score == 0


def test_calculate_trend_score_empty_response(trend_service):
    """Test calculating score with an empty or malformed response."""
    assert trend_service.calculate_trend_score(None) == 0
    assert trend_service.calculate_trend_score({}) == 0
    assert trend_service.calculate_trend_score({"result": {}}) == 0
    assert trend_service.calculate_trend_score({"result": {"timeline": {}}}) == 0
    assert (
        trend_service.calculate_trend_score(
            {"result": {"timeline": {"instructions": []}}}
        )
        == 0
    )


def test_get_twitter_trends_api_error(trend_service):
    """Test handling of an API error during trend fetching."""
    query = "#ErrorCase"
    # Configure the mock to raise an exception
    trend_service.mock_api_client.call_api.side_effect = Exception(
        "Simulated API failure"
    )

    response = trend_service.get_twitter_trends(query=query)

    # Assert that call_api was called
    trend_service.mock_api_client.call_api.assert_called_once_with(
        "Twitter/search_twitter",
        query={"query": query, "count": 20, "type": "Top"},  # Default count/type
    )

    # Assert that the method returned None or handled the error appropriately
    assert response is None


def test_calculate_trend_score_after_api_error(trend_service):
    """Test calculating score when the input is None (simulating previous API error)."""
    score = trend_service.calculate_trend_score(None)
    assert score == 0
