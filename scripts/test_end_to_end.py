"""End-to-end tests for the Resume Tailor system.

This module contains tests that verify the complete flow of the resume tailoring system,
from job description extraction to final tailored resume generation.
"""

import argparse
import json
import os
import yaml
from typing import Dict, Any
import pytest
from unittest.mock import Mock, patch
from dotenv import load_dotenv
import logging

from resume_tailor.utils.logging import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Import components to test
from resume_tailor.extractor.extractor import JobDescriptionExtractor
from resume_tailor.resume_parser import ResumeParser
from resume_tailor.resume_tailor import ResumeTailor
from resume_tailor.llm.client import OpenRouterLLMClient

def load_resume(resume_path: str) -> str:
    """Load resume data from YAML file."""
    try:
        with open(resume_path, 'r') as f:
            content = f.read()
            logger.debug(f"Loaded resume file: {resume_path}")
            logger.debug(f"Content length: {len(content)} characters")
            return content
    except Exception as e:
        logger.error(f"Error loading resume file: {str(e)}")
        raise

def setup_llm_client() -> OpenRouterLLMClient:
    """Set up the LLM client with API key from environment."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    return OpenRouterLLMClient(api_key=api_key)

def print_tailored_resume(data: Dict) -> None:
    """Pretty print the tailored resume data."""
    print("\n=== Tailored Resume ===\n")
    
    # Print basic info
    basic = data.get("basic", {})
    print(f"Name: {basic.get('name', 'N/A')}")
    print(f"Email: {basic.get('email', 'N/A')}")
    print(f"Phone: {basic.get('phone', 'N/A')}")
    print(f"Location: {basic.get('address', 'N/A')}\n")
    
    # Print objective
    print(f"Objective:\n{data.get('objective', 'N/A')}\n")
    
    # Print experience
    print("Experience:")
    for exp in data.get("experiences", []):
        print(f"\n{exp.get('company', 'N/A')}")
        for title in exp.get("titles", []):
            print(f"- {title.get('name', 'N/A')} ({title.get('startdate', 'N/A')} - {title.get('enddate', 'N/A')})")
        print("Highlights:")
        for highlight in exp.get("highlights", []):
            print(f"  * {highlight}")
    
    # Print skills
    print("\nSkills:")
    for skill_cat in data.get("skills", []):
        print(f"\n{skill_cat.get('category', 'Other')}:")
        for skill in skill_cat.get("skills", []):
            print(f"- {skill}")

def run_resume_tailoring(job_url: str, resume_path: str, output_file: str = None) -> None:
    """Run the complete resume tailoring flow."""
    try:
        # Set up components
        print(f"\nSetting up LLM client...")
        llm_client = setup_llm_client()
        
        print(f"Initializing components...")
        job_extractor = JobDescriptionExtractor(llm_client=llm_client)
        resume_parser = ResumeParser(file_path=resume_path)
        resume_tailor = ResumeTailor(llm_client=llm_client)
        
        # Extract job description
        print(f"\nExtracting job description from URL: {job_url}")
        job_data = job_extractor.extract(job_url)
        if not job_data:
            raise Exception("Failed to extract job description")
        
        # Parse resume
        print("\nParsing resume...")
        try:
            # First try to load and parse the YAML directly to validate the file
            with open(resume_path, 'r') as f:
                resume_yaml = f.read()
                logger.debug(f"Successfully loaded YAML file: {resume_path}")
                logger.debug(f"YAML content length: {len(resume_yaml)}")
            
            # Now try to parse with ResumeParser
            resume_data = resume_parser.parse()
            if not resume_data:
                raise Exception("ResumeParser returned None")
            logger.debug(f"Successfully parsed resume with ResumeParser")
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {str(e)}")
            raise Exception(f"Invalid YAML format in resume file: {str(e)}")
        except Exception as e:
            logger.error(f"Resume parsing error: {str(e)}")
            raise Exception(f"Failed to parse resume: {str(e)}")
        
        # Tailor resume
        print("\nTailoring resume...")
        tailored_resume = resume_tailor.tailor(job_data, resume_yaml)
        if not tailored_resume:
            raise Exception("Failed to tailor resume")
        
        # Print results
        print_tailored_resume(tailored_resume.model_dump())
        
        # Save to file if requested
        if output_file:
            print(f"\nSaving tailored resume to: {output_file}")
            resume_tailor.save_tailored_resume(tailored_resume, output_file)
        
        return tailored_resume
        
    except Exception as e:
        print(f"\nError in resume tailoring flow: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

@pytest.fixture
def mock_job_url():
    """Mock job URL for testing."""
    return "https://example.com/job"

@pytest.fixture
def mock_resume_path(tmp_path):
    """Create a mock resume file for testing."""
    resume_data = {
        "basic": {
            "name": "Test User",
            "email": "test@example.com"
        },
        "education": [
            {
                "name": "Test Degree",
                "school": "Test University",
                "startdate": "2020",
                "enddate": "2024"
            }
        ],
        "experiences": [
            {
                "company": "Test Company",
                "titles": [
                    {
                        "name": "Test Role",
                        "startdate": "2020",
                        "enddate": "Present"
                    }
                ],
                "highlights": ["Test highlight"]
            }
        ]
    }
    
    resume_file = tmp_path / "test_resume.yaml"
    with open(resume_file, "w") as f:
        yaml.dump(resume_data, f)
    return str(resume_file)

def test_complete_resume_tailoring_flow(mock_job_url, mock_resume_path):
    """Test the complete resume tailoring flow."""
    with patch("resume_tailor.llm.client.OpenRouterLLMClient") as mock_llm:
        mock_llm.return_value.generate.return_value = {"content": yaml.dump({
            "basic": {"name": "Test User", "email": "test@example.com"},
            "education": [{"name": "Test Degree", "school": "Test University", "startdate": "2020", "enddate": "2024"}],
            "experiences": [{"company": "Test Company", "titles": [{"name": "Test Role", "startdate": "2020", "enddate": "Present"}], "highlights": ["Test highlight"]}]
        })}
        
        result = run_resume_tailoring(mock_job_url, mock_resume_path)
        assert result is not None
        assert result.basic["name"] == "Test User"

def main():
    """Main function to run the test script."""
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Test end-to-end resume tailoring")
    parser.add_argument("url", help="URL of the job posting")
    parser.add_argument(
        "--resume",
        "-r",
        default="resume.yaml",
        help="Path to resume YAML file (default: resume.yaml)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for tailored resume (optional)",
        type=str
    )
    
    args = parser.parse_args()
    
    # Run the test
    result = run_resume_tailoring(
        job_url=args.url,
        resume_path=args.resume,
        output_file=args.output
    )
    
    if result:
        print("\nResume tailoring completed successfully!")
    else:
        print("\nResume tailoring failed.")

if __name__ == "__main__":
    main() 