"""LLM client abstraction module."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(self, prompt: str) -> Dict:
        """
        Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The LLM's response as a dictionary

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

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key. If None, reads from OPENROUTER_API_KEY env var.

        Raises:
            LLMError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise LLMError("OpenRouter API key not provided")

        self.model = "deepseek/deepseek-r1:free"
        self.client = ChatOpenAI(
            api_key="dummy",  # Required by LangChain but not used
            base_url="https://openrouter.ai/api/v1",
            model=self.model,
            max_retries=3,
            request_timeout=30,
            default_headers={
                "HTTP-Referer": "https://github.com/resume-tailoring",
                "Authorization": f"Bearer {self.api_key}"
            }
        )

    def generate(self, prompt: str) -> Dict:
        """
        Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The LLM's response as a dictionary

        Raises:
            LLMError: If there's an error communicating with the LLM
        """
        try:
            print(f"Sending prompt to OpenRouter: {prompt[:50]}...")
            # Get response from LLM
            response = self.client.invoke([HumanMessage(content=prompt)])
            
            if not isinstance(response, AIMessage):
                raise LLMError("Invalid response format from LLM")
            
            print("Successfully received response from OpenRouter")
            
            # Try to parse as JSON if possible
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                # If not JSON, return as plain text
                return {"response": response.content}
                
        except Exception as e:
            error_msg = f"Failed to communicate with OpenRouter: {str(e)}"
            print(f"Error: {error_msg}")
            raise LLMError(error_msg)

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
        if not isinstance(response, dict):
            raise LLMError("Invalid response format")

        if "choices" not in response:
            raise LLMError("No choices in response")

        if not response["choices"] or "message" not in response["choices"][0]:
            raise LLMError("Invalid message format")

        message = response["choices"][0]["message"]
        if "content" not in message:
            raise LLMError("Invalid message format")

        return {"content": message["content"]} 