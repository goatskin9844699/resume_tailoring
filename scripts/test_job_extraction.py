#!/usr/bin/env python3
"""Test script for job description extraction."""

import argparse
import json
import os
from typing import Dict, Optional

from dotenv import load_dotenv
from resume_tailor.extractor.extractor import JobDescriptionExtractor
from resume_tailor.llm.client import OpenRouterLLMClient, LLMError
from resume_tailor.exceptions import ExtractorError
from resume_tailor.utils.logging import setup_logging

# Set up logging
setup_logging()

def setup_llm_client() -> OpenRouterLLMClient:
    """Set up the LLM client with API key from environment."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    return OpenRouterLLMClient(api_key=api_key)


def print_job_data(data: Dict) -> None:
    """Pretty print the extracted job data."""
    print("\n=== Extracted Job Description ===\n")
    
    # Print basic info
    print(f"Company: {data.get('company', 'N/A')}")
    print(f"Title: {data.get('title', 'N/A')}")
    print(f"\nSummary:\n{data.get('summary', 'N/A')}\n")
    
    # Print lists with headers
    for key, title in [
        ('responsibilities', 'Responsibilities'),
        ('requirements', 'Requirements'),
        ('technical_skills', 'Technical Skills'),
        ('non_technical_skills', 'Non-Technical Skills'),
        ('ats_keywords', 'ATS Keywords')
    ]:
        items = data.get(key, [])
        if items:
            print(f"\n{title}:")
            for item in items:
                print(f"- {item}")


def extract_job_description(url: str) -> Optional[Dict]:
    """
    Extract job description from URL.
    
    Args:
        url: Job posting URL
        
    Returns:
        Extracted job data or None if extraction failed
    """
    try:
        # Set up components
        llm_client = setup_llm_client()
        extractor = JobDescriptionExtractor(llm_client=llm_client)
        
        # Extract data
        print(f"\nExtracting data from: {url}")
        content = extractor.scraper.fetch_content(url)
        print("\n=== Raw Job Description ===\n")
        print(content[:1000] + "..." if len(content) > 1000 else content)
        print("\n" + "="*50)
        
        prompt = extractor._generate_prompt(content)
        job_data = extractor.llm.generate(prompt)
        
        # Process response
        if "response" in job_data and isinstance(job_data["response"], str):
            try:
                job_data = json.loads(job_data["response"])
            except json.JSONDecodeError:
                raise ExtractorError("Invalid JSON response from LLM")
        
        # Validate data
        if not job_data or not extractor._validate_job_data(job_data):
            raise ExtractorError("Invalid or incomplete job description data")
        
        return job_data
        
    except ExtractorError as e:
        print(f"\nError extracting job description: {str(e)}")
        return None
    except LLMError as e:
        print(f"\nError communicating with LLM: {str(e)}")
        return None
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        return None


def main():
    """Main function to run the test script."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables")
        return

    parser = argparse.ArgumentParser(description="Test job description extraction")
    parser.add_argument("url", help="URL of the job posting")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for JSON data (optional)",
        type=str
    )
    
    args = parser.parse_args()
    
    # Extract job description
    job_data = extract_job_description(args.url)
    
    if job_data:
        # Print results
        print_job_data(job_data)
        
        # Save to file if requested
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    json.dump(job_data, f, indent=2)
                print(f"\nData saved to: {args.output}")
            except Exception as e:
                print(f"\nError saving data: {str(e)}")
    else:
        print("\nFailed to extract job description.")


if __name__ == "__main__":
    main() 