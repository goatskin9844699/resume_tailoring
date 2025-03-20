#!/usr/bin/env python3
"""Integration test script for the OpenRouter LLM client."""

import os
from typing import List
from dotenv import load_dotenv
from resume_tailor.llm.client import OpenRouterLLMClient
from resume_tailor.utils.logging import setup_logging

# Set up logging
setup_logging()

def test_prompts(client: OpenRouterLLMClient, prompts: List[str]) -> None:
    """
    Test a list of prompts with the LLM client.
    
    Args:
        client: The LLM client instance
        prompts: List of prompts to test
    """
    for prompt in prompts:
        print("\nPrompt:", prompt)
        print("-" * 50)
        try:
            response = client.generate(prompt)
            print("Response:", response.get("content", response))
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 50)

def main() -> None:
    """Run the LLM integration tests."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables")
        return

    # Initialize the LLM client
    client = OpenRouterLLMClient(api_key=api_key)

    # Test prompts
    prompts = [
        "What is the capital of France?",
        "Write a haiku about programming.",
        "Explain what a REST API is in one sentence."
    ]

    test_prompts(client, prompts)

if __name__ == "__main__":
    main() 