#!/usr/bin/env python3
"""Integration test script for the OpenRouter LLM client.

This script performs end-to-end testing of the OpenRouter LLM client
by sending various types of prompts and validating responses.
"""

import os
import time
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from resume_tailor.llm.client import OpenRouterLLMClient
from resume_tailor.utils.logging import setup_logging

logger = logging.getLogger(__name__)

def test_prompts(client: OpenRouterLLMClient, prompts: List[str]) -> Dict[str, Any]:
    """Test a list of prompts with the LLM client.
    
    Args:
        client: The LLM client instance
        prompts: List of prompts to test
        
    Returns:
        Dict containing test results with timing and success status
    """
    results = {
        "total_tests": len(prompts),
        "successful": 0,
        "failed": 0,
        "results": []
    }
    
    for prompt in prompts:
        logger.info("\nTesting prompt: %s", prompt)
        print("\nPrompt:", prompt)
        print("-" * 50)
        
        result = {
            "prompt": prompt,
            "success": False,
            "time_taken": 0
        }
        
        try:
            start_time = time.time()
            response = client.generate(prompt)
            end_time = time.time()
            time_taken = end_time - start_time
            
            result.update({
                "success": True,
                "time_taken": time_taken,
                "response": response.get("content", response)
            })
            
            results["successful"] += 1
            logger.info("Response received in %.2f seconds", time_taken)
            print(f"Response time: {time_taken:.2f} seconds")
            print("Response:", response.get("content", response))
            
        except Exception as e:
            results["failed"] += 1
            error_msg = f"Error: {str(e)}"
            result["error"] = error_msg
            logger.error(error_msg)
            print(error_msg)
            
        results["results"].append(result)
        print("-" * 50)
    
    return results

def main() -> None:
    """Run the LLM integration tests."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY not found in environment variables")
        return

    # Initialize the LLM client
    client = OpenRouterLLMClient(api_key=api_key)
    logger.info("Using model: %s", client.model)
    print(f"Using model: {client.model}")

    # Test prompts - covering different types of queries
    prompts = [
        "What is the capital of France?",
        "Write a haiku about programming.",
        "Explain what a REST API is in one sentence."
    ]

    # Run tests and get results
    results = test_prompts(client, prompts)
    
    # Print summary
    print("\nTest Summary:")
    print(f"Total tests: {results['total_tests']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")

if __name__ == "__main__":
    setup_logging()
    main() 