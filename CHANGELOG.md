# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- TO-DO.md roadmap documenting planned improvements and best practices
- .dockerignore file to reduce build context size and improve build performance
- VERSION file as single source of truth for semantic versioning
- CHANGELOG.md for tracking project changes following Keep a Changelog format
- Comprehensive OCI standard labels in Dockerfile (created, revision, documentation, licenses, vendor)
- Trivy security vulnerability scanning in GitHub Actions workflow
- SARIF report upload to GitHub Security tab for vulnerability tracking
- Dynamic build arguments (VERSION, BUILD_DATE, VCS_REF) for reproducible builds
- CONTRIBUTING.md with comprehensive contribution guidelines, versioning strategy, commit conventions, and testing procedures
- Automated Proton-GE version tracking and updates via Renovate
- GitHub Action workflow to automatically calculate and commit SHA512 checksums for new Proton releases
- Full automation of Proton version updates (version bump + checksum generation)
- Docker HEALTHCHECK directive for automatic container health monitoring
- `/usr/bin/healthcheck-liveness` script for process-based liveness checks (Docker HEALTHCHECK, Kubernetes liveness probes)
- `/usr/bin/healthcheck-readiness` script for RCON-based readiness checks (Kubernetes readiness probes)
- `procps` package installation for health check utilities (provides `pgrep` command)
- Comprehensive health check documentation in README.md and CLAUDE.md with Docker and Kubernetes examples

### Changed
- Dockerfile now uses ARG-based versioning instead of hardcoded version string
- GitHub Actions workflow now reads version from VERSION file
- Taskfile.yml now reads version from VERSION file and passes build arguments
- GitHub Actions permissions updated to include security-events for SARIF uploads
- CLAUDE.md now includes references to all important documentation files (CONTRIBUTING.md, TO-DO.md, CHANGELOG.md)

### Security
- Added automated vulnerability scanning with Trivy on every build
- Added .dockerignore to prevent leaking unnecessary files in build context

## [1.5.0] - 2025-10-20

### Changed
- Converted from script-based setup to Dockerfile-based container image
- Base OS updated to Ubuntu 24.04 (Noble Numbat)
- Added environment variable interpolation in ASA_START_PARAMS for secrets management

### Added
- Ruby-based `asa-ctrl` CLI tool for server management
- RCON interface with auto-discovery of password and port
- Mod management system with JSON database
- Custom RCON protocol implementation
- GitHub Actions workflow for automated builds and publishing
- Support for ASA Server API plugin loader

### Fixed
- Required file size for ASA server installation
- Added Ragnarok to map list

## [1.4.0] - Earlier

### Changed
- Various improvements to installation process
- Documentation updates

## Earlier Versions

See git history for changes prior to 1.4.0. Detailed changelog tracking began with version 1.5.0.

---

## Versioning Guidelines

- **MAJOR** version when making incompatible API changes or major breaking changes
- **MINOR** version when adding functionality in a backwards compatible manner
- **PATCH** version when making backwards compatible bug fixes

## Release Process

1. Update VERSION file with new version number
2. Update CHANGELOG.md with changes under new version heading
3. Commit changes: `git commit -m "bump: <major|minor|patch> - <description>"`
4. Tag the release: `git tag v<version>`
5. Push: `git push origin main --tags`
6. GitHub Actions will automatically build and publish the image

[Unreleased]: https://github.com/jdogwilly/ark-survival-ascended-linux-container-image/compare/v1.5.0...HEAD
[1.5.0]: https://github.com/jdogwilly/ark-survival-ascended-linux-container-image/releases/tag/v1.5.0
