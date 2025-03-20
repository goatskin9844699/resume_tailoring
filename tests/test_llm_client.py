"""Tests for LLM client module."""

from unittest.mock import MagicMock, patch
import pytest
from langchain_core.messages import AIMessage
from resume_tailor.llm.client import OpenRouterLLMClient, LLMError


@pytest.fixture
def client():
    """Create a test client."""
    return OpenRouterLLMClient(api_key="test_key")


def test_init_with_api_key():
    """Test initialization with API key."""
    client = OpenRouterLLMClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert client.model == "google/gemini-2.0-flash-lite-001"


def test_init_without_api_key(monkeypatch):
    """Test client initialization with environment variable."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "env_key")
    client = OpenRouterLLMClient()
    assert client.api_key == "env_key"


def test_init_no_api_key(monkeypatch):
    """Test client initialization with no API key."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(LLMError, match="OpenRouter API key not provided"):
        OpenRouterLLMClient()


@patch("langchain_openai.ChatOpenAI")
def test_generate_success(mock_chat_openai, client):
    """Test successful response generation."""
    mock_instance = MagicMock()
    mock_instance.invoke.return_value = AIMessage(content='{"test": "response"}')
    mock_chat_openai.return_value = mock_instance

    client.client = mock_instance
    response = client.generate("Test prompt")
    assert response == {"test": "response"}


def test_generate_request_error(client):
    """Test error handling during request."""
    client.client = MagicMock()
    client.client.invoke.side_effect = Exception("Test error")

    with pytest.raises(LLMError, match="Failed to communicate with OpenRouter"):
        client.generate("Test prompt")


def test_format_response_success(client):
    """Test successful response formatting."""
    response = {
        "choices": [
            {
                "message": {
                    "content": "Test response"
                }
            }
        ]
    }
    formatted = client.format_response(response)
    assert formatted == {"content": "Test response"}


def test_format_response_invalid_type(client):
    """Test formatting with invalid response type."""
    with pytest.raises(LLMError, match="Invalid response format"):
        client.format_response("invalid")


def test_format_response_no_choices(client):
    """Test formatting with missing choices."""
    with pytest.raises(LLMError, match="No choices in response"):
        client.format_response({})


def test_format_response_invalid_message(client):
    """Test formatting with invalid message format."""
    with pytest.raises(LLMError, match="Invalid message format"):
        client.format_response({"choices": [{"message": {}}]}) 