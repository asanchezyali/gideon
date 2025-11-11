# Contributing to Gideon

First off, thank you for considering contributing to Gideon! 🎉

It's people like you that make Gideon such a great tool for the research community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to asanchezyali@gmail.com.

### Our Pledge

We are committed to making participation in this project a harassment-free experience for everyone, regardless of level of experience, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if applicable**
- **Mention your environment** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and the expected behavior**
- **Explain why this enhancement would be useful**

### Your First Code Contribution

Unsure where to begin? You can start by looking through these issues:

- **good-first-issue** - Issues which should only require a few lines of code
- **help-wanted** - Issues which should be a bit more involved

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Follow the [coding standards](#coding-standards)
- Include tests when adding new features
- Update documentation when necessary
- End all files with a newline

---

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- pip

### Setup Steps

1. **Fork the repository**
   ```bash
   # Click the "Fork" button on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/gideon.git
   cd gideon
   ```

3. **Set up remote**
   ```bash
   git remote add upstream https://github.com/asanchezyali/gideon.git
   ```

4. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

6. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Pull Request Process

1. **Update your fork**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Write meaningful commit messages
   - Keep commits atomic and focused
   - Test your changes thoroughly

4. **Run tests and linters**
   ```bash
   # Run tests
   pytest

   # Run linter
   ruff check src/

   # Format code (if available)
   black src/
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**
   - Fill out the PR template
   - Link related issues
   - Add screenshots/GIFs if applicable
   - Request review from maintainers

### Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning (formatting, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvements
- `test`: Adding missing tests
- `chore`: Changes to build process or auxiliary tools

**Examples:**
```
feat(search): add semantic search with ChromaDB
fix(rename): handle special characters in filenames
docs: update installation guide for Windows
refactor(llm): simplify factory pattern
```

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 120 characters (configured in pyproject.toml)
- **Imports**: Use absolute imports
- **Type hints**: Add type hints for function signatures
- **Docstrings**: Use Google-style docstrings

### Example

```python
from pathlib import Path
from typing import List, Optional

def process_documents(
    directory: Path,
    max_files: int = 100,
    filter_by: Optional[str] = None
) -> List[str]:
    """
    Process documents in a directory.

    Args:
        directory: Path to the directory containing documents
        max_files: Maximum number of files to process
        filter_by: Optional filter criterion

    Returns:
        List of processed document paths

    Raises:
        ValueError: If directory doesn't exist
    """
    if not directory.exists():
        raise ValueError(f"Directory not found: {directory}")

    # Implementation here
    pass
```

### Linting

We use `ruff` for linting:

```bash
# Check for issues
ruff check src/

# Auto-fix issues
ruff check src/ --fix
```

---

## Testing Guidelines

### Writing Tests

- Place tests in the same directory as the module, prefixed with `test_`
- Use pytest for all tests
- Aim for >80% code coverage
- Write both unit tests and integration tests
- Use fixtures for common setup

### Example Test

```python
import pytest
from pathlib import Path
from gideon.search import SemanticSearchEngine

@pytest.fixture
def search_engine():
    """Create a test search engine."""
    return SemanticSearchEngine(persist_directory=Path("/tmp/test_db"))

@pytest.mark.asyncio
async def test_index_document(search_engine):
    """Test document indexing."""
    doc_path = Path("test.pdf")
    content = "Test content"

    chunks = await search_engine.index_document(doc_path, content)

    assert chunks > 0
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/gideon

# Run specific test file
pytest tests/test_search.py

# Run specific test
pytest tests/test_search.py::test_index_document
```

---

## Documentation

### Docstrings

Use Google-style docstrings for all public functions, classes, and modules:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Longer description if needed. Can span multiple lines.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this error is raised
        TypeError: Description of when this error is raised

    Example:
        >>> function_name("hello", 42)
        True
    """
    pass
```

### README Updates

When adding new features:
- Update the Features section
- Add usage examples
- Update the command reference
- Update the roadmap if applicable

### Inline Comments

- Use comments sparingly
- Explain *why*, not *what*
- Keep comments up-to-date

---

## Feature Branches

We follow this branching strategy:

- `main`: Stable, production-ready code
- `feature/*`: New features
- `fix/*`: Bug fixes
- `docs/*`: Documentation updates
- `refactor/*`: Code refactoring

---

## Release Process

Releases are managed by maintainers:

1. Version bump in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a git tag
4. Push to PyPI (automated)
5. Create GitHub release with notes

---

## Getting Help

- 💬 [GitHub Discussions](https://github.com/asanchezyali/gideon/discussions) for questions
- 🐛 [GitHub Issues](https://github.com/asanchezyali/gideon/issues) for bugs
- 📧 Email: asanchezyali@gmail.com

---

## Recognition

Contributors will be:
- Added to the README contributors section
- Mentioned in release notes
- Given credit in the documentation

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Gideon! 🚀

