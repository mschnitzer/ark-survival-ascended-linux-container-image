#!/usr/bin/env bash
set -euo pipefail

# This script checks if VERSION file was bumped when runtime code changes
# Used by both pre-commit hooks and GitHub Actions

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paths that REQUIRE version bump when modified
RUNTIME_PATHS=(
    "Dockerfile"
    "root/"
)

# Paths that are EXCLUDED from version bump requirement
EXCLUDED_PATHS=(
    "*.md"
    ".github/workflows/"
    "docker-compose.yml"
    "Taskfile.yml"
    "renovate.json"
    "root/usr/share/asa-ctrl/tests/"
    "root/usr/share/asa-ctrl/pyproject.toml"
    "scripts/"
    ".pre-commit-config.yaml"
    "VERSION"  # VERSION changes don't require themselves
)

# Get list of changed files
# If running in pre-commit mode (from git hook)
if [ "${PRE_COMMIT:-}" = "1" ]; then
    CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR)
# If running in GitHub Actions (comparing branches)
elif [ "${GITHUB_ACTIONS:-}" = "true" ]; then
    # Compare against base branch
    BASE_REF="${GITHUB_BASE_REF:-main}"
    CHANGED_FILES=$(git diff --name-only "origin/$BASE_REF"...HEAD)
else
    # Default: get all staged files
    CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR)
fi

# Function to check if a path should be excluded
is_excluded() {
    local file="$1"
    for pattern in "${EXCLUDED_PATHS[@]}"; do
        # Convert glob pattern to regex for matching
        if [[ "$file" == $pattern* ]] || [[ "$file" =~ ${pattern//\*/.*} ]]; then
            return 0
        fi
    done
    return 1
}

# Function to check if a path is runtime code
is_runtime_code() {
    local file="$1"
    for pattern in "${RUNTIME_PATHS[@]}"; do
        if [[ "$file" == "$pattern"* ]] || [[ "$file" == "$pattern" ]]; then
            return 0
        fi
    done
    return 1
}

# Collect runtime files that were modified
RUNTIME_FILES=()
while IFS= read -r file; do
    [ -z "$file" ] && continue

    # Skip excluded files
    if is_excluded "$file"; then
        continue
    fi

    # Check if it's runtime code
    if is_runtime_code "$file"; then
        RUNTIME_FILES+=("$file")
    fi
done <<< "$CHANGED_FILES"

# If no runtime files changed, we're good
if [ ${#RUNTIME_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No runtime code changes detected. VERSION bump not required."
    exit 0
fi

# Runtime files changed - check if VERSION was also modified
VERSION_CHANGED=false
while IFS= read -r file; do
    if [ "$file" = "VERSION" ]; then
        VERSION_CHANGED=true
        break
    fi
done <<< "$CHANGED_FILES"

# If VERSION was modified, we're good
if [ "$VERSION_CHANGED" = true ]; then
    echo -e "${GREEN}✓${NC} Runtime code changed and VERSION file was bumped. All good!"
    exit 0
fi

# VERSION was NOT modified but runtime code changed - ERROR!
echo -e "${RED}✗ ERROR: Runtime code was modified but VERSION file was not bumped!${NC}"
echo ""
echo -e "${YELLOW}The following runtime files were modified:${NC}"
for file in "${RUNTIME_FILES[@]}"; do
    echo "  - $file"
done
echo ""
echo -e "${YELLOW}Please update the VERSION file to reflect these changes.${NC}"
echo ""
echo "Current version: $(cat VERSION 2>/dev/null || echo 'VERSION file not found')"
exit 1
