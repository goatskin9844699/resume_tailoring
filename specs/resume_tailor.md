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

### Content Analysis & Scoring

#### Overview
The scoring system:
- Processes all experience entries against job requirements
- Identifies natural keyword matches in existing content
- Provides relevance scores for content selection
- Feeds into content selection and resume customization

**Why:** Create comprehensive relevance mapping while preserving all content, using both efficient local processing and advanced semantic understanding. The hybrid approach ensures both speed and accuracy in matching experiences to job requirements.

#### Implementation

The scoring system uses a hybrid approach combining two complementary scoring mechanisms:

1. **Local Embedding-Based Scoring**
   - Processes text locally using pre-trained embeddings
   - Provides fast, efficient semantic similarity matching
   - Handles basic semantic relationships and keyword matching
   - No ongoing API costs after initial model download

2. **LLM-Based Scoring**
   - Uses advanced language models for nuanced understanding
   - Processes experiences in batches for efficiency
   - Provides deeper context and relationship analysis
   - Handles complex semantic relationships

```mermaid
graph TD
    subgraph Input
        JD[Job Description]
        MR[Master Resume]
    end

    subgraph Scoring System
        direction TB
        subgraph Local Processing
            E[Embedding Model]
            ES[Embedding Scores]
        end
        
        subgraph LLM Processing
            L[LLM Model]
            LS[LLM Scores]
        end
        
        C[Score Combiner]
    end

    subgraph Output
        FS[Final Scores]
        CS[Content Selection]
        RC[Resume Customization]
    end

    JD --> E
    JD --> L
    MR --> E
    MR --> L
    
    E --> ES
    L --> LS
    
    ES --> C
    LS --> C
    
    C --> FS
    FS --> CS
    CS --> RC

    style JD fill:#f9f,stroke:#333,stroke-width:2px
    style MR fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#bfb,stroke:#333,stroke-width:2px
    style L fill:#bfb,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style FS fill:#f9f,stroke:#333,stroke-width:2px
```

### Smart Content Refinement

#### Overview

The refinement system:
- Uses a single LLM call to process all content refinement tasks
- Leverages scoring results to guide content organization
- Maintains professional tone and narrative flow
- Optimizes content for both human readers and ATS
- Preserves the original voice while enhancing relevance

**Why:** Create a polished, professional resume that effectively communicates the candidate's qualifications while maintaining authenticity and optimizing for both human readers and automated systems. The single LLM approach ensures consistency across all refinement tasks while minimizing API calls.

#### Implementation

The refinement system processes scored content to create an optimized resume using a single LLM-based refinement step:

1. **Input Processing**
   - Scored content containing:
     - Original resume content
     - Relevance scores and relationships
     - Similar content mappings
   - Job description for context and requirements

2. **Content Organization**
   - Combines similar experiences based on scoring results
   - Preserves strongest original phrasing and style
   - Maintains narrative flow and career progression
   - Optimizes section ordering by relevance

3. **Content Enhancement**
   - Generates role-specific professional summary
   - Refines bullet points for impact and clarity
   - Ensures consistent tone and style
   - Maintains authentic voice and achievements

```mermaid
graph TD
    subgraph Input
        SC[Scored Content]
        JD[Job Description]
    end

    subgraph Refinement System
        direction TB
        subgraph Content Analysis
            CA[Content Analyzer]
            CR[Content Relationships]
        end
        
        subgraph LLM Refinement
            R[Refinement Engine]
            O[Order Optimizer]
            S[Summary Generator]
            B[Bullet Refiner]
        end
    end

    subgraph Output
        TR[Tailored Resume]
    end

    SC --> CA
    JD --> CA
    
    CA --> CR
    CR --> R
    R --> O
    O --> S
    S --> B
    B --> TR

    style SC fill:#f9f,stroke:#333,stroke-width:2px
    style JD fill:#f9f,stroke:#333,stroke-width:2px
    style CA fill:#bfb,stroke:#333,stroke-width:2px
    style R fill:#bfb,stroke:#333,stroke-width:2px
    style O fill:#bfb,stroke:#333,stroke-width:2px
    style S fill:#bfb,stroke:#333,stroke-width:2px
    style B fill:#bfb,stroke:#333,stroke-width:2px
    style TR fill:#bbf,stroke:#333,stroke-width:2px
```


### ATS Optimization
- Insert required keywords in appropriate sections
- Ensure proper formatting and structure
- Optimize content for machine readability
- Maintain natural language flow

**Why:** Ensure resume passes automated screening while remaining engaging for human readers
