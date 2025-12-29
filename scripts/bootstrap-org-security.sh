#!/usr/bin/env bash
set -euo pipefail

echo "[+] Initializing org-wide security baseline"

mkdir -p .github/workflows
mkdir -p profile
mkdir -p scripts

# SECURITY.md
cat > SECURITY.md <<'EOF'
# Organization Security Policy

Applies to all repositories.

## Reporting
Private disclosure only.

## Prohibited
- Tokens
- Authorization headers
- Secrets
- Internal logs

CI enforces secret scanning.
EOF

# Profile README
cat > profile/README.md <<'EOF'
## Security & Disclosure

All public artifacts are sanitized.
This organization enforces automated secret scanning.
EOF

# CI baseline
cat > .github/workflows/secret-scan.yml <<'EOF'
name: Secret Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: gitleaks/gitleaks-action@v2
EOF

# Pre-commit
cat > .pre-commit-config.yaml <<'EOF'
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.1
    hooks:
      - id: gitleaks
EOF

echo "[+] Done. Commit and push this repo."
