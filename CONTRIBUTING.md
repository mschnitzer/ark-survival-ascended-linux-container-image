# Contributing to ARK: Survival Ascended Linux Container Image

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing to the ARK: Survival Ascended Linux Container Image project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Python Development](#python-development)
- [Versioning Strategy](#versioning-strategy)
- [Commit Conventions](#commit-conventions)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Code Standards](#code-standards)
- [Documentation Updates](#documentation-updates)
- [Getting Help](#getting-help)

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (24.0 or later)
- **Docker Compose** (2.0 or later)
- **Git**
- **[Taskfile](https://taskfile.dev/installation/)** (recommended for local development)
- **Python 3** (for Python package development)
- **uv** (Python package manager) - installed automatically via Taskfile

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ark-survival-ascended-linux-container-image.git
   cd ark-survival-ascended-linux-container-image
   ```
3. Add the upstream repository as a remote:
   ```bash
   git remote add upstream https://github.com/jdogwilly/ark-survival-ascended-linux-container-image.git
   ```

### Local Development Setup

View all available development tasks:
```bash
task --list
```

Build the Docker image locally:
```bash
task build
```

Build and run a test server:
```bash
task dev
```

## Development Workflow

### Making Changes

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the [Code Standards](#code-standards)

3. **Test your changes** locally (see [Testing Requirements](#testing-requirements))

4. **Commit your changes** following the [Commit Conventions](#commit-conventions)

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** (see [Pull Request Process](#pull-request-process))

### Common Development Tasks

**Build the container image:**
```bash
task build
```

**Run a test server:**
```bash
task dev
```

**View logs:**
```bash
task logs
```

**Stop the test server:**
```bash
task stop
```

**Clean up test containers and volumes:**
```bash
task clean
```

## Python Development

The project includes a Python-based control tool (`asa-ctrl`) that uses the `uv` package manager for ultra-fast dependency management.

### Working with the Python Package

Navigate to the Python package directory:
```bash
cd root/usr/share/asa-ctrl
```

**Install dependencies:**
```bash
uv sync --extra dev
```

**Run tests:**
```bash
uv run pytest
```

**Run tests with coverage:**
```bash
uv run pytest --cov=asa_ctrl
```

**Install in development mode (for local testing):**
```bash
uv pip install -e .
```

### Python Code Standards

- **Zero runtime dependencies**: The `asa-ctrl` package uses Python stdlib only (no external runtime dependencies)
- **Development dependencies** (pytest, etc.) are defined in `pyproject.toml` under `[project.optional-dependencies]`
- **Type hints**: Use type hints where appropriate
- **Docstrings**: Include docstrings for public functions and classes
- **Testing**: All new functionality must include unit tests

## Versioning Strategy

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) with a VERSION file as the single source of truth.

### Version Format

Version numbers follow the format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes or major breaking changes
- **MINOR**: New functionality in a backwards-compatible manner
- **PATCH**: Backwards-compatible bug fixes

### VERSION File

The `VERSION` file at the repository root contains the current version (e.g., `1.5.0`). This file is read by:
- Dockerfile (via ARG instructions)
- GitHub Actions workflows
- Taskfile

## Commit Conventions

### Commit Message Format

Use clear, descriptive commit messages that explain **why** the change was made, not just **what** changed.

**Format:**
```
<type>: <subject>

<optional body>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring without changing functionality
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates, etc.
- `security`: Security-related changes
- `bump`: Version bump (see below)

**Examples:**
```
feat: Add HEALTHCHECK to Dockerfile for container monitoring

fix: Correct RCON password discovery from environment variables

docs: Update CONTRIBUTING.md with Python development guidelines

refactor: Optimize Dockerfile layer ordering for better caching
```

### Version Bumping

To bump the version, use the `bump` type in your commit message:

**Format:**
```
bump: <major|minor|patch> - <description>
```

**Examples:**
```
bump: minor - Add HEALTHCHECK support to Dockerfile

bump: patch - Fix RCON authentication error handling

bump: major - Remove support for Ruby-based asa-ctrl (breaking change)
```

**Important:** Only maintainers should create version bump commits. Contributors should focus on feature/fix commits.

## Testing Requirements

All contributions must pass the following tests before being merged:

### 1. Docker Build

The Docker image must build successfully:
```bash
task build
```

### 2. Python Unit Tests

All Python unit tests must pass with 100% success rate:
```bash
cd root/usr/share/asa-ctrl
uv run pytest
```

Expected output:
```
============================= test session starts ==============================
collected 25 items

tests/test_*.py .........................                                [100%]

============================== 25 passed in 0.50s ==============================
```

### 3. Security Scanning

The image must pass Trivy vulnerability scanning with no HIGH or CRITICAL vulnerabilities. This is automatically checked by GitHub Actions on pull requests.

### 4. Integration Testing (Optional but Recommended)

Test the image by running a test server:
```bash
task dev
task logs
```

Verify:
- Container starts without errors
- Entry points are created correctly (`asa-ctrl`, `cli-asa-mods`)
- Server files download successfully

## Pull Request Process

### Creating a Pull Request

1. **Ensure all tests pass** locally (see [Testing Requirements](#testing-requirements))

2. **Update documentation** if your changes affect user-facing functionality:
   - Update `README.md` for user-facing changes
   - Update `CLAUDE.md` for development workflow changes
   - Update `CHANGELOG.md` under the `[Unreleased]` section

3. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub:
   - Use a clear, descriptive title
   - Reference any related issues (e.g., "Fixes #123")
   - Provide a detailed description of your changes
   - Explain **why** the changes are needed
   - Include any testing you performed

### PR Checklist

Before submitting your PR, ensure:

- [ ] Code follows project [Code Standards](#code-standards)
- [ ] All tests pass locally
- [ ] Python unit tests pass (if applicable)
- [ ] Documentation is updated (README.md, CHANGELOG.md, etc.)
- [ ] Commit messages follow [Commit Conventions](#commit-conventions)
- [ ] No merge conflicts with `main` branch
- [ ] Docker image builds successfully

### Automated Checks

When you create a PR, GitHub Actions will automatically:
- Build the Docker image
- Run Trivy security scanning
- Upload vulnerability reports to GitHub Security tab
- Report build status

### Code Review

- A maintainer will review your PR
- Address any feedback or requested changes
- Once approved, a maintainer will merge your PR

## Code Standards

### Dockerfile Best Practices

- **Multi-stage builds**: Use multi-stage builds to minimize final image size
- **Layer ordering**: Place rarely-changing layers first (system packages, user creation) and frequently-changing layers last (application code)
- **Cleanup in same layer**: Clean up package manager caches in the same RUN layer:
  ```dockerfile
  RUN apt-get update && \
      apt-get install -y package && \
      rm -rf /var/lib/apt/lists/*
  ```
- **ARG for build-time variables**: Use ARG instructions for version, build date, etc.
- **OCI labels**: Include comprehensive OCI standard labels

### Python Code Standards

- **Stdlib only**: Runtime code must use Python standard library only (zero external dependencies)
- **Package manager**: Use `uv` for package management (defined in `pyproject.toml`)
- **Entry points**: Define command-line tools as entry points in `pyproject.toml`
- **Error handling**: Use custom exception classes defined in `errors.py`
- **Exit codes**: Use constants from `exit_codes.py`

### Bash Scripts

- **ShellCheck compatible**: Scripts should pass ShellCheck linting
- **Error handling**: Use `set -e` and check exit codes
- **Quoting**: Quote variables to prevent word splitting
- **Logging**: Output clear, user-friendly messages

### General Guidelines

- **No secrets**: Never commit secrets, passwords, or API keys
- **No generated files**: Don't commit compiled files or build artifacts
- **.dockerignore**: Update `.dockerignore` for new files that shouldn't be in the build context
- **Comments**: Add comments for complex logic or non-obvious decisions

## Documentation Updates

### When to Update Documentation

Update documentation when your changes:
- Add new features
- Change existing behavior
- Modify configuration options
- Update dependencies
- Change the development workflow

### Which Files to Update

**README.md**: User-facing changes
- Installation instructions
- Configuration options
- Server administration commands
- Troubleshooting guides

**CLAUDE.md**: Development workflow changes
- Architecture changes
- Development tool updates
- Testing procedures
- Build process modifications

**CHANGELOG.md**: All changes (required)
- Add your changes under `[Unreleased]`
- Use categories: Added, Changed, Fixed, Security, Deprecated, Removed
- Follow [Keep a Changelog](https://keepachangelog.com/) format

**TO-DO.md**: Roadmap updates
- Mark completed items with ✅
- Add new planned improvements
- Update phase completion status

## Getting Help

### Resources

- **README.md**: User documentation and installation guide
- **CLAUDE.md**: Developer documentation and architecture overview
- **TO-DO.md**: Project roadmap and planned improvements
- **CHANGELOG.md**: Version history and release notes

### Asking Questions

- **GitHub Discussions**: For general questions and discussions
- **GitHub Issues**: For bug reports and feature requests
- **Pull Request Comments**: For questions about specific code changes

### Reporting Bugs

When reporting a bug, please include:
1. Container image version or tag (e.g., `latest`, `1.5.0`)
2. Host OS and version (e.g., Ubuntu 24.04)
3. Docker version (`docker --version`)
4. Relevant configuration (redact sensitive information)
5. Steps to reproduce the issue
6. Expected behavior vs. actual behavior
7. Relevant logs (from `docker logs asa-server`)

### Suggesting Features

When suggesting a feature:
1. Check existing issues and TO-DO.md to avoid duplicates
2. Describe the problem you're trying to solve
3. Explain your proposed solution
4. Discuss any potential drawbacks or alternatives
5. Consider backward compatibility

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

## Thank You!

Thank you for contributing to make this project better for the ARK: Survival Ascended community!
