#!/usr/bin/env bash
set -euo pipefail

for repo in */; do
  cd "$repo"
  if [ -d .git ]; then
    cp ../.pre-commit-config.yaml .
    pre-commit install || true
    git add .pre-commit-config.yaml
    git commit -m "chore(security): enforce secret scanning" || true
    git push || true
  fi
  cd ..
done
gitleaks detect --source . --redact --report-path gitleaks-report.json

gitleaks detect --source . --log-opts="--all"
