# Contributing to Books Crawler

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Use the bug report template
3. Include:
   - Description of the issue
   - Steps to reproduce
   - Expected vs. actual behavior
   - Environment details (Python version, OS, etc.)
   - Relevant logs or screenshots

### Suggesting Enhancements

1. Check if the enhancement has been suggested
2. Use the feature request template
3. Explain:
   - Use case and motivation
   - Proposed solution
   - Alternative approaches considered

### Pull Requests

1. **Fork the repository**

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation

4. **Test your changes**
   ```bash
   make test
   make lint
   ```

5. **Commit your changes**
   ```bash
   git commit -m "feat: add new feature"
   ```

   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test changes
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Use the PR template
   - Link related issues
   - Describe your changes clearly

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/books-crawler.git
cd books-crawler

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
make dev-install

# Install pre-commit hooks
pre-commit install

# Run tests
make test
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints
- Write docstrings for all public functions/classes
- Maximum line length: 100 characters

### Code Quality

- Use `ruff` for linting
- Use `black` for formatting
- Use `mypy` for type checking
- Maintain test coverage > 80%

### Documentation

- Update README for user-facing changes
- Add docstrings for new code
- Update API documentation if endpoints change
- Include examples where helpful

## Testing

### Writing Tests

- Write unit tests for new functions
- Add integration tests for API endpoints
- Use fixtures for common test data
- Mock external dependencies

### Running Tests

```bash
# All tests
make test

# With coverage
make test-cov

# Specific suite
pytest tests/unit/test_config.py -v
```

## Review Process

1. Automated checks must pass (linting, tests, type checking)
2. Code review by maintainer
3. Address review feedback
4. Approval and merge

## Release Process

1. Version bump in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release tag
4. Build and publish to PyPI (if applicable)
5. Update documentation

## Questions?

- Open a discussion on GitHub
- Contact maintainers

Thank you for contributing! 🎉
