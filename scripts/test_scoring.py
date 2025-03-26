#!/usr/bin/env python3
"""Integration test script for resume scoring system."""

import argparse
import json
import os
import yaml
from typing import Dict, Optional, Any
import logging
from dotenv import load_dotenv

from resume_tailor.scoring import (
    EmbeddingScorer,
    LLMScorer,
    ScoreCombiner,
    SectionScore,
    ScoringResult,
    CombinedScore
)
from resume_tailor.extractor.extractor import JobDescriptionExtractor
from resume_tailor.resume_parser import ResumeParser
from resume_tailor.llm.client import OpenRouterLLMClient, LLMError
from resume_tailor.utils.logging import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

def setup_llm_client() -> OpenRouterLLMClient:
    """Set up the LLM client with API key from environment."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    return OpenRouterLLMClient(api_key=api_key)


def print_scoring_results(combined_score: CombinedScore) -> None:
    """Pretty print the scoring results."""
    print("\n=== Scoring Results ===\n")
    
    # Print overall score
    print(f"Overall Score: {combined_score.overall_score:.3f}")
    print(f"Processing Time: {combined_score.processing_time:.2f}s\n")
    
    # Print component weights
    print("Component Weights:")
    for component, weight in combined_score.component_weights.items():
        print(f"- {component}: {weight:.3f}")
    print()
    
    # Print section scores
    print("Section Scores:")
    for section_id, score in combined_score.section_scores.items():
        print(f"\n{section_id}:")
        print(f"- Score: {score.score:.3f}")
        print(f"- Confidence: {score.confidence:.3f}")
        if score.matched_keywords:
            print(f"- Matched Keywords: {', '.join(score.matched_keywords)}")
        if score.relevance_explanation:
            print(f"- Explanation: {score.relevance_explanation}")
    
    # Print metadata
    print("\nMetadata:")
    for key, value in combined_score.metadata.items():
        print(f"- {key}: {value}")


def score_resume(
    resume_content: Dict,
    job_data: Dict,
    sections_to_score: Optional[list] = None
) -> Optional[CombinedScore]:
    """
    Score resume content against job description.
    
    Args:
        resume_content: Resume content dictionary
        job_data: Job description data dictionary
        sections_to_score: Optional list of sections to score
        
    Returns:
        CombinedScore containing the scoring results or None if scoring failed
    """
    try:
        # Set up components
        llm_client = setup_llm_client()
        embedding_scorer = EmbeddingScorer()
        llm_scorer = LLMScorer(llm_client=llm_client)
        score_combiner = ScoreCombiner(
            weights={
                "embedding_all-MiniLM-L6-v2": 0.4,
                "llm_scorer": 0.6
            }
        )
        
        # Prepare job description
        job_description = f"""
Title: {job_data.get('title', 'N/A')}
Company: {job_data.get('company', 'N/A')}

Summary:
{job_data.get('summary', 'N/A')}

Requirements:
{chr(10).join(f"- {req}" for req in job_data.get('requirements', []))}

Responsibilities:
{chr(10).join(f"- {resp}" for resp in job_data.get('responsibilities', []))}

Technical Skills:
{chr(10).join(f"- {skill}" for skill in job_data.get('technical_skills', []))}

Non-Technical Skills:
{chr(10).join(f"- {skill}" for skill in job_data.get('non_technical_skills', []))}
"""
        
        # Score with embedding model
        print("\nScoring with embedding model...")
        embedding_result = embedding_scorer.score_content(
            sections=resume_content,
            sections_to_score=sections_to_score,
            job_description=job_description
        )
        
        # Score with LLM
        print("\nScoring with LLM...")
        llm_result = llm_scorer.score_content(
            job_description=job_description,
            resume_content=resume_content,
            sections=sections_to_score
        )
        
        # Combine results
        print("\nCombining scores...")
        combined_score = score_combiner.combine_results([
            embedding_result,
            llm_result
        ])
        
        return combined_score
        
    except LLMError as e:
        print(f"\nError communicating with LLM: {str(e)}")
        return None
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        return None


def run_scoring_flow(job_url: str, resume_path: str, output_file: str = None) -> None:
    """Run the complete scoring flow."""
    try:
        # Set up components
        print(f"\nSetting up LLM client...")
        llm_client = setup_llm_client()
        
        print(f"Initializing components...")
        job_extractor = JobDescriptionExtractor(llm_client=llm_client)
        resume_parser = ResumeParser(file_path=resume_path)
        
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
        
        # Score resume
        print("\nScoring resume...")
        combined_score = score_resume(
            resume_content=resume_data.model_dump(),
            job_data=job_data,
            sections_to_score=None  # Score all sections
        )
        
        if not combined_score:
            raise Exception("Failed to score resume")
        
        # Print results
        print_scoring_results(combined_score)
        
        # Save to file if requested
        if output_file:
            print(f"\nSaving scoring results to: {output_file}")
            with open(output_file, 'w') as f:
                json.dump(combined_score.model_dump(), f, indent=2)
        
        return combined_score
        
    except Exception as e:
        print(f"\nError in scoring flow: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test resume scoring system")
    parser.add_argument("url", help="URL of the job posting")
    parser.add_argument("resume", help="Path to resume YAML file")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for scoring results (optional)",
        type=str
    )
    return parser.parse_args()


def main():
    """Main function to run the test script."""
    # Load environment variables from .env file
    load_dotenv()
    
    args = parse_args()
    
    # Run the scoring flow
    result = run_scoring_flow(
        job_url=args.url,
        resume_path=args.resume,
        output_file=args.output
    )
    
    if result:
        print("\nResume scoring completed successfully!")
    else:
        print("\nResume scoring failed.")


if __name__ == "__main__":
    main() 