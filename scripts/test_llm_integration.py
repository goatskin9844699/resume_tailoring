#!/usr/bin/env python3
"""Integration test script for the OpenRouter LLM client."""

import os
from dotenv import load_dotenv
from resume_tailor.llm.client import OpenRouterLLMClient

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables")
        print("Please create a .env file with your API key (see .env.example)")
        return

    # Initialize the LLM client
    client = OpenRouterLLMClient(api_key=api_key)

    # Test prompts
    prompts = [
        "What is the capital of France?",
        "Write a haiku about programming.",
        "Explain what a REST API is in one sentence."
    ]

    # Test each prompt
    for prompt in prompts:
        print("\n" + "="*50)
        print(f"Prompt: {prompt}")
        print("-"*50)
        
        try:
            response = client.generate(prompt)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 