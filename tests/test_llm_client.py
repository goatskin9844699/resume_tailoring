"""Tests for LLM client module.

This module contains tests for the OpenRouterLLMClient class and related functionality.
"""

from typing import Dict, Any
from unittest.mock import MagicMock, patch
import pytest
from langchain_core.messages import AIMessage
from resume_tailor.llm.client import OpenRouterLLMClient, LLMError


@pytest.fixture
def client() -> OpenRouterLLMClient:
    """Create a test client.
    
    Returns:
        OpenRouterLLMClient: A configured test client instance
    """
    return OpenRouterLLMClient(api_key="test_key")


def test_init_with_api_key() -> None:
    """Test initialization with API key.
    
    Verifies that the client is properly initialized with a provided API key.
    """
    client = OpenRouterLLMClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert client.model == "google/gemini-2.0-flash-lite-001"


def test_init_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test client initialization with environment variable.
    
    Args:
        monkeypatch: pytest fixture for modifying environment
        
    Verifies that the client can initialize using an environment variable.
    """
    monkeypatch.setenv("OPENROUTER_API_KEY", "env_key")
    client = OpenRouterLLMClient()
    assert client.api_key == "env_key"


def test_init_no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test client initialization with no API key.
    
    Args:
        monkeypatch: pytest fixture for modifying environment
        
    Raises:
        LLMError: Expected when no API key is available
    """
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(LLMError, match="OpenRouter API key not provided"):
        OpenRouterLLMClient()


@patch("langchain_openai.ChatOpenAI")
def test_generate_success(mock_chat_openai: MagicMock, client: OpenRouterLLMClient) -> None:
    """Test successful response generation.
    
    Args:
        mock_chat_openai: Mock for ChatOpenAI class
        client: Test client fixture
        
    Verifies that the generate method properly processes successful responses.
    """
    mock_instance = MagicMock()
    mock_instance.invoke.return_value = AIMessage(content='{"test": "response"}')
    mock_chat_openai.return_value = mock_instance

    client.client = mock_instance
    response = client.generate("Test prompt")
    assert response == {"test": "response"}


@patch("langchain_openai.ChatOpenAI")
def test_generate_with_markdown_code_block(mock_chat_openai: MagicMock, client: OpenRouterLLMClient) -> None:
    """Test response generation with markdown code blocks.
    
    Args:
        mock_chat_openai: Mock for ChatOpenAI class
        client: Test client fixture
        
    Verifies that markdown code blocks are properly stripped from responses.
    """
    mock_instance = MagicMock()
    mock_instance.invoke.return_value = AIMessage(content='```json\n{"test": "response"}\n```')
    mock_chat_openai.return_value = mock_instance

    client.client = mock_instance
    response = client.generate("Test prompt")
    assert response == {"test": "response"}


@patch("langchain_openai.ChatOpenAI")
def test_generate_with_non_json_response(mock_chat_openai: MagicMock, client: OpenRouterLLMClient) -> None:
    """Test response generation with non-JSON content.
    
    Args:
        mock_chat_openai: Mock for ChatOpenAI class
        client: Test client fixture
        
    Verifies that non-JSON responses are properly handled.
    """
    mock_instance = MagicMock()
    mock_instance.invoke.return_value = AIMessage(content='Plain text response')
    mock_chat_openai.return_value = mock_instance

    client.client = mock_instance
    response = client.generate("Test prompt")
    assert response == {"content": "Plain text response"}


@patch("langchain_openai.ChatOpenAI")
def test_generate_invalid_response_type(mock_chat_openai: MagicMock, client: OpenRouterLLMClient) -> None:
    """Test handling of invalid response types.
    
    Args:
        mock_chat_openai: Mock for ChatOpenAI class
        client: Test client fixture
        
    Raises:
        LLMError: Expected when response type is invalid
    """
    mock_instance = MagicMock()
    mock_instance.invoke.return_value = "Invalid response type"
    mock_chat_openai.return_value = mock_instance

    client.client = mock_instance
    with pytest.raises(LLMError, match="Invalid response format from LLM"):
        client.generate("Test prompt")


def test_generate_request_error(client: OpenRouterLLMClient) -> None:
    """Test error handling during request.
    
    Args:
        client: Test client fixture
        
    Raises:
        LLMError: Expected when request fails
    """
    client.client = MagicMock()
    client.client.invoke.side_effect = Exception("Test error")

    with pytest.raises(LLMError, match="Failed to communicate with OpenRouter"):
        client.generate("Test prompt")


def test_format_response_success(client: OpenRouterLLMClient) -> None:
    """Test successful response formatting.
    
    Args:
        client: Test client fixture
        
    Verifies that response formatting works correctly with valid input.
    """
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


def test_format_response_invalid_type(client: OpenRouterLLMClient) -> None:
    """Test formatting with invalid response type.
    
    Args:
        client: Test client fixture
        
    Raises:
        LLMError: Expected when response has invalid type
    """
    with pytest.raises(LLMError, match="Invalid response format"):
        client.format_response("invalid")


def test_format_response_no_choices(client: OpenRouterLLMClient) -> None:
    """Test formatting with missing choices.
    
    Args:
        client: Test client fixture
        
    Raises:
        LLMError: Expected when response has no choices
    """
    with pytest.raises(LLMError, match="No choices in response"):
        client.format_response({})


def test_format_response_invalid_message(client: OpenRouterLLMClient) -> None:
    """Test formatting with invalid message format.
    
    Args:
        client: Test client fixture
        
    Raises:
        LLMError: Expected when message format is invalid
    """
    with pytest.raises(LLMError, match="Invalid message format"):
        client.format_response({"choices": [{"message": {}}]}) 