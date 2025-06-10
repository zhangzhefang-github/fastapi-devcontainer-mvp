# Contributing to FastAPI Enterprise MVP

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/your-username/fastapi-devcontainer-mvp/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/your-username/fastapi-devcontainer-mvp/issues/new); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/fastapi-devcontainer-mvp.git
   cd fastapi-devcontainer-mvp
   ```

2. **Set up development environment**
   ```bash
   # Using Docker (recommended)
   docker-compose -f docker-compose.simple.yml up -d
   
   # Or local development
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```

3. **Run tests**
   ```bash
   pytest --cov=app
   ```

4. **Code style**
   ```bash
   black .
   isort .
   flake8 .
   ```

## Code Style

- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Write meaningful commit messages using [Conventional Commits](https://www.conventionalcommits.org/)

## Testing

- Write tests for new features
- Maintain test coverage above 90%
- Use pytest for testing
- Include both unit and integration tests

## Documentation

- Update README.md for significant changes
- Add docstrings to new functions and classes
- Update API documentation if endpoints change

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

## References

This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md)
