"""LLM client abstraction module."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(self, prompt: str) -> Any:
        """
        Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The LLM's response

        Raises:
            LLMError: If there's an error communicating with the LLM
        """
        pass

    @abstractmethod
    def format_response(self, response: Any) -> Dict:
        """
        Format the LLM's response into structured data.

        Args:
            response: Raw response from the LLM

        Returns:
            Structured data from the response

        Raises:
            LLMError: If there's an error formatting the response
        """
        pass


class OpenRouterLLMClient(LLMClient):
    """OpenRouter LLM client implementation using LangChain."""

    def __init__(self, api_key: str):
        """
        Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key. If None, reads from OPENROUTER_API_KEY env var.
        """
        self.client = ChatOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-3.5-turbo",
            max_retries=3,
            request_timeout=30,
            default_headers={
                "HTTP-Referer": "https://github.com/resume-tailoring"
            }
        )

    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The LLM's response

        Raises:
            LLMError: If there's an error communicating with the LLM
        """
        try:
            response = self.client.invoke([HumanMessage(content=prompt)])
            return self.format_response(response)
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")

    def format_response(self, response: AIMessage) -> str:
        """
        Format the LLM's response into structured data.

        Args:
            response: Raw response from the LLM

        Returns:
            Structured data from the response

        Raises:
            LLMError: If there's an error formatting the response
        """
        if not isinstance(response, AIMessage):
            raise ValueError("Invalid response format")
        return response.content 