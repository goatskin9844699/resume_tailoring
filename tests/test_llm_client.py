"""Tests for LLM client module."""

import pytest
from unittest.mock import patch, MagicMock
from resume_tailor.llm.client import OpenRouterLLMClient, LLMError


@pytest.fixture
def mock_response():
    """Create a mock successful response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Test response"
                }
            }
        ]
    }


@pytest.fixture
def client():
    """Create a test client with mock API key."""
    return OpenRouterLLMClient(api_key="test_key")


def test_init_with_api_key():
    """Test client initialization with API key."""
    client = OpenRouterLLMClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert client.model == "deepseek/deepseek-r1:free"


def test_init_without_api_key():
    """Test client initialization without API key."""
    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "env_key"}):
        client = OpenRouterLLMClient()
        assert client.api_key == "env_key"


def test_init_no_api_key():
    """Test client initialization with no API key available."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(LLMError, match="OpenRouter API key not provided"):
            OpenRouterLLMClient()


@patch("requests.post")
def test_generate_success(mock_post, client, mock_response):
    """Test successful response generation."""
    mock_post.return_value = MagicMock(
        json=lambda: mock_response,
        raise_for_status=lambda: None
    )
    
    response = client.generate("Test prompt")
    assert response == mock_response
    
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://openrouter.ai/api/v1/chat/completions"
    assert call_args[1]["headers"]["Authorization"] == "Bearer test_key"
    assert call_args[1]["json"]["model"] == "deepseek/deepseek-r1:free"
    assert call_args[1]["json"]["messages"] == [{"role": "user", "content": "Test prompt"}]


@patch("requests.post")
def test_generate_request_error(mock_post, client):
    """Test error handling during request."""
    mock_post.side_effect = Exception("Network error")
    
    with pytest.raises(LLMError, match="Failed to communicate with OpenRouter"):
        client.generate("Test prompt")


def test_format_response_success(client, mock_response):
    """Test successful response formatting."""
    formatted = client.format_response(mock_response)
    assert formatted == {"content": "Test response"}


def test_format_response_invalid_type(client):
    """Test formatting with invalid response type."""
    with pytest.raises(LLMError, match="Invalid response format"):
        client.format_response("not a dict")


def test_format_response_no_choices(client):
    """Test formatting with response missing choices."""
    with pytest.raises(LLMError, match="No choices in response"):
        client.format_response({"not_choices": []})


def test_format_response_invalid_message(client):
    """Test formatting with invalid message format."""
    with pytest.raises(LLMError, match="Invalid message format"):
        client.format_response({"choices": [{"message": {}}]}) 