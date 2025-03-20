# Project-Specific Rules

## Python Development Standards

### Code Style
- Follow PEP 8 style guide strictly
- Use Black code formatter with default settings
- Maximum line length: 88 characters (Black default)
- Use type hints for all function parameters and return values
- Use docstrings for all modules, classes, and functions

### Module Structure
- One class per file unless tightly coupled
- Keep `__init__.py` files empty
- Relative imports within the package
- Absolute imports for external packages
- Clear separation of public and private interfaces

### Naming Conventions
- Modules: lowercase with underscores
- Classes: CapWords convention
- Functions: lowercase with underscores
- Variables: lowercase with underscores
- Constants: UPPERCASE with underscores
- Private attributes/methods: prefix with underscore

### Documentation
- All public APIs must have docstrings
- Use Google-style docstring format
- Include type hints in docstrings
- Document exceptions that may be raised
- Keep docstrings up to date with code changes

## Virtual Environment

### Setup and Management
- Use `venv` for virtual environment creation
- Virtual environment must be named `.venv`
- Never commit virtual environment to repository
- Keep `requirements.txt` up to date
- Pin all dependency versions

### Dependencies
- Minimize number of dependencies
- Document reason for each dependency
- Regular security audits of dependencies
- Separate dev and production dependencies

## Testing

### Unit Testing
- Every code change requires unit tests
- Use pytest framework
- Tests must be in `tests/` directory
- Test files must start with `test_`
- One test file per module being tested

### Test Environment
- Tests must run in clean virtual environment
- No external service dependencies in unit tests
- Mock all external services
- Use pytest fixtures for test setup

### Test Coverage
- Minimum 90% code coverage required
- Coverage report generated with pytest-cov
- No untested code paths allowed
- Document any excluded paths

### Test Running
- Tests must pass before commit
- Run tests in isolated environment
- No side effects from tests allowed
- Clean up all test artifacts

### Test Isolation
- Each test case should be fully isolated
- Import statements should be inside test functions, not at module level
- Exception: Test framework imports (e.g., pytest) can be at module level
- Each test should test exactly one thing

Example of good test isolation:
```python
import pytest  # Framework import at module level

def test_specific_feature():
    # Imports inside test function
    from my_package import SpecificFeature
    # Test implementation
    assert SpecificFeature
```

Benefits:
- Tests fail independently
- Clear what each test is testing
- No import side effects between tests
- Easier to debug failures

### Test Organization
- One test file per module
- Clear test names describing what is being tested
- Group related tests in classes when appropriate
- Use fixtures for common setup

## Continuous Integration
- All tests must pass in CI
- Coverage report generated in CI
- Linting checks in CI
- Type checking in CI

## Version Control
- Feature branches for all changes
- Pull requests required
- Code review required
- Tests must pass before merge

## Development Workflow
1. Create feature branch
2. Set up clean virtual environment
3. Write tests first (TDD)
4. Implement changes
5. Verify test coverage
6. Run full test suite
7. Create pull request 