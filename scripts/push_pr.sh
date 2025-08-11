#!/usr/bin/env bash
set -euo pipefail
BRANCH=${1:-feat/prod-hardening}
ZIP=${2:-sparkapp84_pr5_push_and_terraform.zip}
if [ ! -f "$ZIP" ]; then echo "Zip not found: $ZIP"; exit 1; fi
unzip -o "$ZIP" -d .
git checkout -b "$BRANCH" || git checkout "$BRANCH"
git add -A
git commit -m "feat: production hardening (Redis caching, webhook idempotency, GCS signed URLs, Terraform, VPC connector)"
git push -u origin "$BRANCH"
echo "Open a PR on GitHub for $BRANCH"
