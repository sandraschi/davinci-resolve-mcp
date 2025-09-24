# Contributing to DaVinci Resolve MCP

Thank you for your interest in contributing to DaVinci Resolve MCP! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:
- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## How to Contribute

### Development Setup

1. **Prerequisites**
   - Python 3.8 or later
   - DaVinci Resolve installed
   - Git

2. **Clone and Setup**
   ```bash
   git clone https://github.com/sandraschi/davinci-resolve-mcp.git
   cd davinci-resolve-mcp

   # Create virtual environment (Windows)
   .\setup_venv.ps1 -InstallPackage -TestInstallation

   # Or manually:
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -e .
   ```

3. **Verify Setup**
   ```bash
   davinci-resolve-mcp check
   ```

### Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

3. **Test Your Changes**
   ```bash
   # Run unit tests
   pytest tests/unit/

   # Run integration tests (requires DaVinci Resolve)
   pytest tests/integration/

   # Run all tests with coverage
   pytest --cov=davinci_resolve_mcp --cov-report=html
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style Guidelines

#### Python Code
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Use docstrings for all modules, classes, and functions
- Maximum line length: 100 characters
- Use meaningful variable and function names

#### Tool Implementation
- All MCP tools must use the `@app.tool()` decorator
- Include comprehensive docstrings with parameter descriptions
- Implement proper error handling with try/catch blocks
- Use structured logging instead of print statements
- Validate all input parameters

#### Error Handling
- Use custom exception classes from `utils.exceptions`
- Implement graceful degradation when possible
- Provide user-friendly error messages
- Log detailed error information for debugging

### Testing

#### Unit Tests
- Place unit tests in `tests/unit/`
- Test individual functions and methods
- Mock external dependencies (DaVinci Resolve API)
- Aim for >80% code coverage

#### Integration Tests
- Place integration tests in `tests/integration/`
- Test with real DaVinci Resolve installation
- Test complete workflows end-to-end
- May be skipped in CI if DaVinci Resolve not available

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=davinci_resolve_mcp

# Run specific test file
pytest tests/unit/test_connection_manager.py

# Run tests matching pattern
pytest -k "test_create_project"
```

### Documentation

#### Code Documentation
- All functions and classes must have docstrings
- Use Google-style docstrings
- Document parameters, return values, and exceptions
- Include usage examples where appropriate

#### User Documentation
- Update README.md for user-facing changes
- Add examples to `prompts/` directory
- Update CHANGELOG.md following Keep a Changelog format
- Update API documentation in `docs/`

### Pull Request Process

1. **Ensure CI Passes**
   - All tests must pass
   - Code coverage requirements met
   - Linting passes
   - Type checking passes

2. **Update Documentation**
   - README.md updated if needed
   - CHANGELOG.md updated
   - Docstrings added/updated

3. **PR Description**
   - Clearly describe the changes
   - Reference any related issues
   - Include screenshots for UI changes
   - List any breaking changes

4. **Review Process**
   - At least one maintainer review required
   - Address review feedback
   - May require additional testing

### Commit Message Format

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Examples:
```
feat: add support for custom LUTs
fix: resolve connection timeout issue
docs: update installation instructions
test: add integration tests for rendering
```

### Issue Reporting

When reporting bugs or requesting features:

1. **Check Existing Issues**
   - Search for similar issues before creating new ones
   - Add to existing discussions if appropriate

2. **Bug Reports**
   - Use the bug report template
   - Include DaVinci Resolve version
   - Include Python version and OS
   - Provide steps to reproduce
   - Include error messages and logs

3. **Feature Requests**
   - Use the feature request template
   - Clearly describe the problem and solution
   - Include use cases and examples
   - Consider implementation complexity

### Release Process

Releases are automated through GitHub Actions:
- Version numbers follow semantic versioning
- CHANGELOG.md is updated automatically
- Git tags are created for releases
- PyPI packages are published automatically

### Getting Help

- **Documentation**: Check the `docs/` directory and README.md
- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub discussions for questions and general discussion
- **Code Examples**: Check the `examples/` and `prompts/` directories

Thank you for contributing to DaVinci Resolve MCP!
