#!/bin/sh

set -eu

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

status=0

echo "Release hygiene checks"

tracked_blockers=$(git ls-files | grep -E '^(build/|data/private/|data/raw/|\.env($|\\.[^.].*)|.*\.duckdb$|.*\.api-key$)' || true)
if [ -n "$tracked_blockers" ]; then
    echo
    echo "FAIL: tracked sensitive or generated files detected"
    printf '%s\n' "$tracked_blockers"
    status=1
else
    echo
    echo "OK: no tracked build/, data/private/, data/raw/, .env, .duckdb, or .api-key files"
fi

tracked_emails=$(git grep -n -I -E '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' -- \
    README.md CHANGELOG.md CONTRIBUTING.md DISCLAIMER.md SECURITY.md pyproject.toml Makefile .github docs src tests |
    grep -Ev '(@example\.com|@example\.org|@example\.invalid|users\.noreply\.github\.com)' || true)
if [ -n "$tracked_emails" ]; then
    echo
    echo "FAIL: non-placeholder email addresses found in tracked files"
    printf '%s\n' "$tracked_emails"
    status=1
else
    echo
    echo "OK: no non-placeholder email addresses found in tracked files"
fi

history_emails=$(git log --format='%ae' --branches | sort -u)
non_noreply_history=$(printf '%s\n' "$history_emails" | grep -Ev '(^$|users\.noreply\.github\.com$)' || true)
if [ -n "$non_noreply_history" ]; then
    echo
    echo "FAIL: commit history still contains non-noreply author emails"
    printf '%s\n' "$non_noreply_history"
    echo "Rewrite or publish from a clean history before pushing to a public repository."
    status=1
else
    echo
    echo "OK: commit history author emails are noreply-only"
fi

exit "$status"
