"""Tests for LLM client module."""

import pytest
from unittest.mock import patch, MagicMock
from resume_tailor.llm.client import OpenRouterLLMClient, LLMError
from langchain_core.messages import AIMessage


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


@patch("langchain_openai.ChatOpenAI")
def test_generate_success(mock_chat_openai, client, mock_response):
    """Test successful response generation."""
    mock_instance = MagicMock()
    mock_instance.invoke.return_value = AIMessage(content="Test response")
    mock_chat_openai.return_value = mock_instance
    
    client.chat = mock_instance
    response = client.generate("Test prompt")
    
    assert response == mock_response
    mock_instance.invoke.assert_called_once()


@patch("langchain_openai.ChatOpenAI")
def test_generate_request_error(mock_chat_openai, client):
    """Test error handling during request."""
    mock_instance = MagicMock()
    mock_instance.invoke.side_effect = Exception("Network error")
    mock_chat_openai.return_value = mock_instance
    
    client.chat = mock_instance
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