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

# Resume Tailoring

A tool to help tailor resumes to job descriptions using AI.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/resume-tailoring/resume-tailoring.git
cd resume-tailoring
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment:
   - Copy `.env.example` to `.env`
   - Get your API key from [OpenRouter](https://openrouter.ai/keys)
   - Add your API key to the `.env` file:
     ```
     OPENROUTER_API_KEY=your_api_key_here
     ```

## Testing the LLM Integration

To test the LLM integration:

1. Make sure you've set up your environment as described above
2. Run the integration test script:
```bash
./scripts/test_llm_integration.py
```

The script will run a few test prompts to verify that the LLM integration is working correctly. You should see responses from the model for each test prompt.

If you encounter any errors:
- Verify that your API key is correctly set in the `.env` file
- Check that all dependencies are installed
- Ensure you have an active internet connection

## Contributing

[Your existing contributing guidelines here] 