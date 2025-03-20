# Resume Tailor - Technical Requirements

```mermaid
graph LR
    subgraph Inputs
        JD[Job Description Data]
        MR[Master Resume Data]
    end

    subgraph Processing
        TA[Resume Tailor]
    end

    subgraph Output
        TR[Tailored Resume Data]
    end

    JD --> TA
    MR --> TA
    TA --> TR

    style JD fill:#f9f,stroke:#333,stroke-width:2px
    style MR fill:#f9f,stroke:#333,stroke-width:2px
    style TR fill:#bbf,stroke:#333,stroke-width:2px
    style TA fill:#bfb,stroke:#333,stroke-width:2px
```

## Overview
The Resume Tailor is a component that creates customized versions of resumes by analyzing job requirements and matching them with resume content. It focuses on highlighting relevant experience and skills while maintaining professional tone and narrative coherence.

## Core Concepts

### Input Processing
- Accepts structured job description data
- Accepts structured master resume data
- Validates input compatibility
- Ensures data completeness

### Content Analysis
- Matches job requirements with resume content
- Identifies relevant skills and experiences
- Scores section relevance
- Maintains narrative coherence

### Output Generation
- Creates tailored resume data
- Preserves resume structure
- Optimizes for ATS
- Maintains professional tone

### Error Management
- Handles missing data
- Manages content mismatches
- Processes validation errors
- Maintains data integrity

## Data Flow
```mermaid
graph TD
    A[Job Data] --> D[Content Analysis]
    B[Resume Data] --> D
    D --> E[Section Scoring]
    E --> F[Content Selection]
    F --> G[Output Generation]

    subgraph "Input Processing"
        A
        B
    end

    subgraph "Core Processing"
        D
        E
        F
    end

    subgraph "Output Processing"
        G
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bfb,stroke:#333,stroke-width:2px
```

## Output Format
The tailored resume maintains the same structure as the input resume with:
- Reordered sections by relevance
- Highlighted matching content
- Optimized keywords
- Preserved formatting 

## Implementation Approach

### Job Description Analysis
- Extract structured data from job postings:
  * Technical skills
  * Non-technical skills
  * ATS keywords
  * Requirements
  * Responsibilities
  * Industry context
- Use semantic understanding for skill matching
- Consider industry-specific terminology
- Identify transferable skills

### Content Matching
- Match skills semantically (e.g., "Python" matches "Python 3.8+")
- Consider industry context when matching experiences
- Look for transferable skills across different domains
- Match experience levels appropriately
- Prioritize recent and relevant experiences

### ATS Optimization
- Use extracted ATS keywords strategically
- Maintain proper keyword density
- Ensure format compatibility
- Optimize section headers
- Validate content structure