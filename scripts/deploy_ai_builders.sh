#!/bin/bash
# Deploy to ai-builders.space via the Experimental Deployment API.
# See: deployment-prompt.md and https://www.ai-builders.com/resources/students-backend/openapi.json
#
# Deployment API = https://space.ai-builders.com/backend/v1/deployments (from platform docs).
# DEPLOY_BASE_URL defaults to https://space.ai-builders.com/backend; override if needed.
# Your app URL after deploy = https://ai-yoga-coach.ai-builders.space (per deployment prompt).
#
# Required: AI_BUILDER_TOKEN.
# Optional: DEPLOY_BASE_URL, REPO_URL, SERVICE_NAME, BRANCH, PORT (see defaults below).
# Optional: deploy-config.json in project root for repo_url, service_name, branch, env_vars.
#
# Usage:
#   export AI_BUILDER_TOKEN="your-platform-api-key"
#   ./scripts/deploy_ai_builders.sh

set -e

# Deployment API base (platform docs: https://space.ai-builders.com/backend/v1/deployments)
DEPLOY_BASE_URL="${DEPLOY_BASE_URL:-https://space.ai-builders.com/backend}"
BASE="$DEPLOY_BASE_URL"
URL="${BASE}/v1/deployments"

if [ -z "$AI_BUILDER_TOKEN" ]; then
  echo "Error: AI_BUILDER_TOKEN is not set."
  echo "  Use your existing platform API key (the same one you use for other Space features)."
  echo "  export AI_BUILDER_TOKEN=\"your-key\""
  echo "  ./scripts/deploy_ai_builders.sh"
  exit 1
fi

# Defaults for this project (override with env vars if needed)
REPO_URL="${REPO_URL:-https://github.com/ypiao2/AI_Yoga_Coach.git}"
SERVICE_NAME="${SERVICE_NAME:-ai-yoga-coach}"
BRANCH="${BRANCH:-main}"
PORT="${PORT:-8000}"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "${ROOT_DIR}/deploy-config.json" ] && command -v jq >/dev/null 2>&1; then
  if jq -e '.repo_url and .service_name and .branch' "${ROOT_DIR}/deploy-config.json" >/dev/null 2>&1; then
    echo "Using deploy-config.json for deployment parameters."
    PAYLOAD=$(jq -c '{repo_url, service_name, branch, port: (.port // 8000)} + (if .env_vars then {env_vars} else {} end)' "${ROOT_DIR}/deploy-config.json")
    REPO_URL=$(jq -r '.repo_url' "${ROOT_DIR}/deploy-config.json")
    SERVICE_NAME=$(jq -r '.service_name' "${ROOT_DIR}/deploy-config.json")
    BRANCH=$(jq -r '.branch' "${ROOT_DIR}/deploy-config.json")
    PORT=$(jq -r '.port // 8000' "${ROOT_DIR}/deploy-config.json")
  fi
fi
if [ -z "${PAYLOAD:-}" ]; then
  if command -v jq >/dev/null 2>&1; then
    PAYLOAD=$(jq -n \
      --arg repo "$REPO_URL" \
      --arg svc "$SERVICE_NAME" \
      --arg branch "$BRANCH" \
      --argjson port "$PORT" \
      '{repo_url: $repo, service_name: $svc, branch: $branch, port: $port}')
  else
    PAYLOAD="{\"repo_url\":\"$REPO_URL\",\"service_name\":\"$SERVICE_NAME\",\"branch\":\"$BRANCH\",\"port\":$PORT}"
  fi
fi

echo "Deploying to ${URL} ..."
echo "  repo: $REPO_URL  service: $SERVICE_NAME  branch: $BRANCH  port: $PORT"
echo "  Ensure all changes are committed and pushed to GitHub before deploying."
echo "  Provisioning typically takes 5–10 minutes. Use the Deployment Portal or GET /v1/deployments/$SERVICE_NAME to check status."
echo ""

# -L follow redirects; --post301 keep POST (and body) when following 301
RESP=$(curl -sS -L --post301 -w "\n%{http_code}" -X POST "$URL" \
  -H "Authorization: Bearer $AI_BUILDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Split body and status code (macOS head doesn't support -n -1)
HTTP_CODE=$(echo "$RESP" | tail -n 1)
HTTP_BODY=$(echo "$RESP" | sed '$d')

echo "$HTTP_BODY" | jq -r '.' 2>/dev/null || echo "$HTTP_BODY"

if [ "$HTTP_CODE" = "202" ]; then
  echo ""
  echo "Deployment queued (202 Accepted). Poll GET ${BASE}/v1/deployments/${SERVICE_NAME} until status is HEALTHY/UNHEALTHY (usually 5–10 min)."
elif [ "$HTTP_CODE" != "200" ]; then
  echo ""
  echo "Request returned HTTP $HTTP_CODE. Check repo URL, branch, service name, and token."
  exit 1
fi
