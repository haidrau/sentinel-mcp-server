#!/bin/bash
# ============================================================================
# Priceminder MCP — One-Click Docker Launcher
# ============================================================================
# Usage:
#   # Prerequisite: get your token at https://priceminder.online
#   bash docker-run.sh YOUR_SENTINEL_TOKEN
#
#   # Or set it as an env var:
#   export SENTINEL_TOKEN=your_token
#   bash docker-run.sh
# ============================================================================

set -e

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BOLD}🚀 Priceminder MCP — Docker Launcher${NC}"
echo ""

# --- Resolve token ---
if [ -n "$1" ]; then
    TOKEN="$1"
elif [ -n "$SENTINEL_TOKEN" ]; then
    TOKEN="$SENTINEL_TOKEN"
else
    echo -e "${RED}❌ Error: No token provided.${NC}"
    echo ""
    echo "Usage:"
    echo "  bash docker-run.sh YOUR_SENTINEL_TOKEN"
    echo ""
    echo "  Or set the SENTINEL_TOKEN environment variable."
    echo ""
    echo -e "${YELLOW}💡 Get your free token at: https://priceminder.online${NC}"
    exit 1
fi

# --- Pull latest image ---
echo -e "${YELLOW}📦 Pulling latest image...${NC}"
docker pull ghcr.io/haidrau/sentinel-mcp-server:latest 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Could not pull from ghcr.io, building locally...${NC}"
    docker build -t priceminder-mcp:local .
    IMAGE_TAG="priceminder-mcp:local"
}

# --- Stop & remove old container if exists ---
docker rm -f priceminder-mcp 2>/dev/null || true

# --- Run container ---
echo -e "${YELLOW}🚢 Starting container...${NC}"

docker run -d \
  --name priceminder-mcp \
  --restart unless-stopped \
  -p 8082:8082 \
  -e SENTINEL_TOKEN="${TOKEN}" \
  -e SENTINEL_API_KEY="sentinel-mvp-2026" \
  -e SENTINEL_API_BASE="https://priceminder.online/shopee" \
  ghcr.io/haidrau/sentinel-mcp-server:latest

# --- Verify ---
sleep 2
if docker ps --filter "name=priceminder-mcp" --filter "status=running" --format '{{.Names}}' | grep -q "priceminder-mcp"; then
    echo ""
    echo -e "${GREEN}✅ Priceminder MCP is running!${NC}"
    echo ""
    echo -e "   ${BOLD}Health check:${NC}  http://localhost:8082/health"
    echo -e "   ${BOLD}MCP endpoint:${NC} http://localhost:8082/mcp"
    echo ""
    echo -e "   ${BOLD}Configure your AI client:${NC}"
    echo ""
    echo '   ```json'
    echo '   {'
    echo '     "mcpServers": {'
    echo '       "priceminder": {'
    echo '         "type": "http",'
    echo '         "url": "http://localhost:8082/mcp"'
    echo '       }'
    echo '     }'
    echo '   }'
    echo '   ```'
    echo ""
    echo -e "   ${BOLD}View logs:${NC}  docker logs -f priceminder-mcp"
    echo -e "   ${BOLD}Stop:${NC}      docker stop priceminder-mcp"
else
    echo -e "${RED}❌ Container failed to start. Check logs:${NC}"
    echo "   docker logs priceminder-mcp"
    exit 1
fi