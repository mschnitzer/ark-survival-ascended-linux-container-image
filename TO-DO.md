# ARK: Survival Ascended Container - Improvement Roadmap

This document tracks planned improvements and best practices to be implemented for this project. Items are organized by priority and implementation phase.

## Legend
- ✅ Completed
- 🚧 In Progress
- 📋 Planned
- 🔮 Future Consideration

---

## Phase 1: Documentation & Foundation (High Priority) ✅ COMPLETED

### Versioning Strategy
- ✅ **Create VERSION file** at repo root for single source of truth
  - Format: `1.5.0` (semantic versioning)
  - CI/CD will read this file for automated tagging

- ✅ **Update Dockerfile with dynamic versioning**
  - Remove hardcoded version from line 7
  - Use ARG instructions for build-time version injection
  - Add comprehensive OCI labels (created, revision, source, documentation)

- ✅ **Enhance GitHub Actions workflow**
  - Read version from VERSION file
  - Tag releases with: full version (1.5.0), minor (1.5), major (1)
  - Implement commit message-based version bumping (e.g., `bump: minor`)

### Documentation
- ✅ **Create CHANGELOG.md**
  - Follow "Keep a Changelog" format
  - Categories: Added, Changed, Fixed, Security, Deprecated, Removed
  - Document all releases starting from 1.5.0

- ✅ **Create CONTRIBUTING.md**
  - Contribution guidelines for external contributors
  - Explain versioning strategy and commit conventions
  - Testing procedures for local development
  - Pull request template requirements

- ✅ **Update CLAUDE.md**
  - Add references to new TO-DO.md, CHANGELOG.md, and CONTRIBUTING.md
  - Document new versioning approach
  - Update development workflow section

---

## Phase 2: Security & Hardening (High Priority)

### Container Security Scanning
- ✅ **Add Trivy vulnerability scanning**
  - Add scan step to `.github/workflows/docker-publish.yml`
  - Scan on: PRs, pushes to main, and version tags
  - Fail builds on HIGH/CRITICAL vulnerabilities
  - Upload results to GitHub Security tab (SARIF format)

- ✅ **Create .dockerignore file**
  - Exclude: `.git/`, `.github/`, `*.md`, `README.md`, `TO-DO.md`, `CLAUDE.md`
  - Reduces build context and prevents leaking unnecessary files

- 📋 **Pin package versions in Dockerfile**
  - Currently: `apt-get install -y lib32gcc-s1 python3 wget...`
  - Pin specific versions for reproducibility
  - Document why specific versions are chosen

### Secret Scanning
- 📋 **Add secret scanning to CI/CD**
  - Use GitHub's built-in secret scanning
  - Consider adding Gitleaks or TruffleHog to workflow
  - Scan before allowing image builds

---

## Phase 3: Container Optimization (Medium Priority) ✅ COMPLETED

### Multi-Stage Dockerfile
- ✅ **Convert to multi-stage build** ✅
  - **Stage 1 (builder)**: Install Python3 and uv, build asa-ctrl package
  - **Stage 2 (runtime)**: Copy only installed package and entry points
  - **Achieved**: 60MB reduction from single-stage Python build
  - **Combined with Ruby removal**: Total 400MB reduction (74.9% smaller than original)

- ✅ **Optimize layer ordering** ✅
  - Rarely-changing layers first: System packages, user creation
  - Frequently-changing layers last: Application scripts (start_server)
  - Python package installation in middle tier
  - Maximizes Docker layer cache effectiveness

### Image Size Reduction
- ✅ **Clean up apt cache in same layer** ✅
  - All apt operations use `rm -rf /var/lib/apt/lists/*` in single RUN layer
  - Applied to both builder and runtime stages

- 📋 **Consider distroless final stage**
  - Research if game server can run in distroless/minimal base
  - May conflict with debug mode requirements (requires bash, user tools)
  - Evaluate trade-offs before implementing
  - **Note**: Current Ubuntu 24.04 base provides good balance of size vs functionality

---

## Phase 4: Ruby to Python Migration (Medium Priority) ✅ COMPLETED

### Overview
~~Current Ruby codebase: ~230 lines across 17 files~~
**Completed:** All Ruby code migrated to Python using uv package manager
- RCON protocol implementation (69 lines)
- Mod database management (66 lines)
- INI config parsing (17 lines)
- CLI interfaces and helpers (~80 lines)

**Dependencies to remove after migration:**
- ruby, ruby-dev, bundler, gcc, g++, make
- Gems: slop (4.10.1), iniparse (1.5.0)
- **Estimated image size savings**: 150-200MB

### Migration Tasks

#### 1. RCON Module Migration
- ✅ **Create `/usr/share/asa-ctrl/rcon.py`** ✅
  - Implement Valve RCON protocol using `socket` and `struct` stdlib modules
  - Functions:
    - `exec_command(server_ip, rcon_port, rcon_command, password)` → execute RCON command
    - `authenticate(socket, password)` → authenticate with server
    - `send_packet(socket, data, packet_id)` → send RCON packet
    - `identify_password()` → auto-discover from ASA_START_PARAMS or GameUserSettings.ini
    - `identify_port()` → auto-discover RCON port
  - Reference current implementation: `root/usr/share/asa-ctrl/rcon/rcon.rb:1-70`

#### 2. Config Helpers Migration
- ✅ **Create `/usr/share/asa-ctrl/config.py`** ✅
  - Use Python's `configparser` stdlib for INI parsing
  - Functions:
    - `parse_game_user_settings()` → parse GameUserSettings.ini
    - `parse_start_params(params_string)` → parse ASA_START_PARAMS
    - `get_value(params, key)` → extract value from start parameters
  - Replace: `ini_config_helper.rb` and `start_params_helper.rb`

#### 3. Mod Management Migration
- ✅ **Rewrite `/usr/bin/cli-asa-mods` in Python** ✅
  - Use `json` stdlib module (no external deps needed)
  - Maintain exact same output format for backward compatibility
  - Keep error handling (write to /tmp/mod-read-error on failures)
  - Current script: `root/usr/bin/cli-asa-mods:1-35`

#### 4. Main CLI Migration
- ✅ **Create `/usr/share/asa-ctrl/asa_ctrl/__main__.py`** ✅
  - Use `argparse` stdlib for CLI parsing (replaces slop gem)
  - Subcommands: `rcon --exec "command"`
  - Future: `mods add/remove/list` (when implemented)
  - Error codes: Match current exit codes from `exit_codes.rb`

#### 5. Error Handling Migration
- ✅ **Create custom exception classes in Python** ✅
  - `RconAuthenticationError`
  - `RconPasswordNotFoundError`
  - `RconPortNotFoundError`
  - `ModAlreadyEnabledError` (for future mod interface)

#### 6. Update Dockerfile for Python + uv
- ✅ **Remove Ruby packages from Dockerfile** ✅
  - Delete: `ruby`, `ruby-dev`, `bundler`, `gcc`, `g++`, `make`
  - Keep: `python3` (already present)
  - Remove: Bundler installation and Gemfile steps (lines 40-42)

- 📋 **Update symlinks and permissions**
  - Change `/usr/bin/asa-ctrl` symlink target to `.py` file
  - Ensure Python scripts are executable (`chmod 0755`)
  - Update WORKDIR if needed

#### 7. Testing & Validation
- ✅ **Test RCON functionality** ✅ (via unit tests)
  - Verify `docker exec asa-server asa-ctrl rcon --exec 'saveworld'` works
  - Test password auto-discovery from both sources
  - Test port auto-discovery
  - Validate error handling (missing password, wrong port, auth failures)

- ✅ **Test mod management** ✅ (via unit tests)
  - Verify `/usr/bin/cli-asa-mods` outputs correct `-mods=` format
  - Test with empty mods.json
  - Test with corrupted JSON (error handling)
  - Test with enabled/disabled mods

- ✅ **Integration testing** ✅
  - Build new image locally
  - Verify CLI commands work (asa-ctrl, cli-asa-mods)
  - Confirmed 25/25 unit tests passing
  - All entry points created correctly via uv

---

## Phase 5: CI/CD Enhancements (Medium Priority)

### GitHub Actions Improvements
- ✅ **Add PR testing workflow**
  - Build image on PRs but don't push
  - Run basic validation tests
  - Report image size changes in PR comments

- 📋 **Add image size reporting**
  - Use `dive` or similar tool to analyze layers
  - Comment on PRs with size comparison vs main branch
  - Alert if image grows unexpectedly

- 📋 **Implement dependency caching**
  - Already using `cache-from: type=gha` ✅
  - Optimize cache hit rate
  - Document cache behavior

### Automated Updates
- 📋 **Add Dependabot configuration**
  - Monitor Dockerfile base image updates
  - Monitor GitHub Actions version updates
  - Create PRs for security updates

- 📋 **Add workflow for Proton version updates**
  - Check GloriousEggroll releases for new Proton versions
  - Semi-automated PR creation when new stable release available
  - Include SHA512 checksum verification

---

## Phase 6: Additional Best Practices (Low Priority)

### Health Checks
- 📋 **Add HEALTHCHECK to Dockerfile**
  - Check if ArkAscendedServer.exe process is running
  - Alternative: Check if game port responds
  - Useful for orchestration (Docker Swarm, Kubernetes)
  - Example: `HEALTHCHECK CMD pgrep -f ArkAscendedServer.exe || exit 1`

### Logging Improvements
- 📋 **Add structured logging**
  - Currently: Bash script outputs to stdout ✅
  - Consider: Adding log levels (INFO, WARN, ERROR)
  - Consider: Timestamps on all log lines
  - Keep stdout/stderr for Docker logs compatibility

### Testing Infrastructure
- 📋 **Add automated testing framework**
  - Unit tests for Python utilities (when migrated)
  - Integration tests for server startup
  - Smoke tests for RCON connectivity
  - Consider: GitHub Actions test runner

---

## Phase 7: Future Considerations 🔮

### Multi-Platform Support
- 🔮 **ARM64 support**
  - Currently: `linux/amd64` only
  - Investigate: Proton compatibility with ARM64
  - May require: Box64/Wine emulation layer
  - Benefit: Support for ARM-based servers (cost savings)

### Alternative Runtime Approaches
- 🔮 **Investigate native Linux server**
  - Monitor: Epic Games for native Linux ASA server
  - If released: Would eliminate Proton dependency
  - Massive benefit: Smaller image, better performance

### Advanced Features
- 🔮 **Backup automation**
  - Built-in scheduled backup script
  - Save game upload to S3/B2/cloud storage
  - Restore functionality

- 🔮 **Web-based admin panel**
  - Alternative to RCON CLI
  - Mod management UI
  - Server stats and monitoring

- 🔮 **Prometheus metrics exporter**
  - Expose server metrics (player count, CPU, memory)
  - Integration with Grafana dashboards
  - Community monitoring templates

### Community Contributions
- 🔮 **Example configurations**
  - TrueCharts Helm chart
  - Kubernetes manifests
  - Docker Swarm stack examples
  - Nomad job specifications

- 🔮 **Plugin ecosystem**
  - Document ASA API plugin installation process
  - Example plugins and configurations
  - Plugin management via asa-ctrl CLI

---

## Implementation Notes

### Priority Ranking
1. **Critical**: Security, Versioning, Documentation
2. **High**: Python migration, Multi-stage builds
3. **Medium**: CI/CD enhancements, Health checks
4. **Low**: Nice-to-have features
5. **Future**: Experimental or blocked on external factors

### Estimated Effort
- **Phase 1**: 2-3 hours
- **Phase 2**: 2-3 hours
- **Phase 3**: 2-3 hours
- **Phase 4**: 4-6 hours (largest effort - migration)
- **Phase 5**: 2-3 hours
- **Phase 6**: 2-3 hours
- **Total**: ~15-20 hours for complete implementation

### Dependencies
- **Phase 1** can be done independently
- **Phase 2** can be done independently
- **Phase 3** should be done after Phase 4 (to measure size savings accurately)
- **Phase 4** is independent but should be tested thoroughly
- **Phase 5** can be done after Phase 1 (versioning)

### Success Metrics
- ✅ Image size reduced by >150MB (Ruby → Python + multi-stage) - **EXCEEDED: 400MB reduction (74.9%)**
- ✅ Zero HIGH/CRITICAL vulnerabilities in Trivy scans
- ✅ Semantic versioning fully automated via VERSION file
- ✅ All RCON functionality preserved after Python migration
- ✅ CI/CD builds remain under 10 minutes
- ✅ Documentation complete and up-to-date
- ✅ Multi-stage build eliminates uv, source code, and build artifacts from final image

---

## Maintenance

This TO-DO.md file should be updated as items are completed:
- Move completed items to CHANGELOG.md with version/date
- Mark items with ✅ when completed
- Add new items as they're discovered
- Review quarterly for priority adjustments

**Last Updated**: 2025-10-22 (Phase 1: Documentation & Foundation completed)
**Next Review**: 2026-01-20
