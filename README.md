# Resume Tailor

A Python module for extracting job descriptions and tailoring resumes based on them.

## Features

- Extract structured data from job descriptions using LLM
- Parse master resumes in YAML format
- Tailor resumes based on job requirements
- Type hints and docstrings for better code clarity

## Installation

```bash
# Install base dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

## Project Structure

```
resume_tailor/
├── __init__.py
├── exceptions.py
├── extractor/
│   └── extractor.py      # Job description extraction
├── llm/
│   └── client.py         # LLM client interface
├── parser.py             # Resume parsing
└── tailor/
    └── tailor.py         # Resume tailoring
```

## Usage

```python
from resume_tailor.extractor import JobDescriptionExtractor
from resume_tailor.tailor import ResumeTailor
from resume_tailor.llm.client import LLMClient
from resume_tailor.parser import Resume

# Initialize components
llm = LLMClient()
extractor = JobDescriptionExtractor(llm)
tailor = ResumeTailor(llm)

# Extract job description
job_desc = extractor.extract("https://example.com/job")

# Load master resume
master_resume = Resume.from_yaml("master_resume.yaml")

# Create tailored resume
tailored_resume = tailor.tailor_resume(job_desc, master_resume)
```

## Development

### Testing

```bash
# Run tests with coverage
pytest --cov=resume_tailor tests/

# Run type checking
mypy resume_tailor

# Run linting
pylint resume_tailor
```

### Code Style

This project uses:
- Black for code formatting
- MyPy for type checking
- Pylint for linting

## License

MIT License 