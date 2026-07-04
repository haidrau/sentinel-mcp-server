# Priceminder MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-purple)](https://modelcontextprotocol.io)
[![Website](https://img.shields.io/badge/Web-priceminder.online-green)](https://priceminder.online)

[**中文**](README.zh-CN.md) | [English](README.md)

> **Priceminder** — Real-time Shopee competitor price monitoring, powered by AI agents through the Model Context Protocol (MCP).

🌐 **Sign up free**: [priceminder.online](https://priceminder.online)

Monitor competitor prices across Shopee Southeast Asia (SG, MY, TH, VN). Let your AI agent track, analyze, and alert on price movements — all through natural language.

---

## 🌟 Features

| # | Tool | Description | Tier |
|---|------|-------------|------|
| 1 | `get_monitor_list` | List all products you're tracking | 🔍 Query |
| 2 | `get_price_summary` | Price summary across all tracked products (batch mode) | 🔍 Query |
| 3 | `get_price_history` | Time-series price data for a specific product | 🔍 Query |
| 4 | `get_alerts` | List price drop alerts | 🔍 Query |
| 5 | `add_monitor` | Add a new product to track | ⚡ Action |
| 6 | `update_monitor_status` | Pause or resume monitoring | ⚡ Action |
| 7 | `mark_alert_read` | Mark an alert as read | ⚡ Action |
| 8 | `get_crawl_health` | Check crawler engine health & stats | 📊 Insight |
| 9 | `get_monitor_overview` | Dashboard overview of all monitors | 📊 Insight |
| 10 | `search_my_products` | Search your tracked products by keyword | 📊 Insight |

---

## 🚀 Quick Start

### Option A: Hosted HTTP (Recommended — No Setup)

Just add this URL to any MCP-compatible client:

```
https://priceminder.online/mcp_server?key=YOUR_MCP_KEY
```

**Step 1: Get your MCP Key**
- Visit [priceminder.online](https://priceminder.online) to sign up
- Or call the API directly (see [API Reference](#-api-reference))

**Step 2: Configure your AI client**

For **Claude Desktop / Cursor / Cherry Studio**:

```json
{
  "mcpServers": {
    "priceminder": {
      "type": "http",
      "url": "https://priceminder.online/mcp_server?key=YOUR_MCP_KEY"
    }
  }
}
```

For **Claude Code**:

```bash
claude mcp add priceminder --type http --url "https://priceminder.online/mcp_server?key=YOUR_MCP_KEY"
```

### Option B: Self-Hosted (Docker)

```bash
docker run -d \
  --name priceminder-mcp \
  -p 8082:8082 \
  -e SENTINEL_API_BASE=https://priceminder.online/shopee \
  -e SENTINEL_TOKEN=YOUR_SENTINEL_TOKEN \
  -e SENTINEL_API_KEY=sentinel-mvp-2026 \
  ghcr.io/haidrau/sentinel-mcp-server:latest
```

### Option C: Self-Hosted (pip)

```bash
pip install sentinel-mcp-server

# Run in stdio mode (for Claude Desktop, Cursor, etc.)
export SENTINEL_TOKEN=YOUR_SENTINEL_TOKEN
sentinel-mcp-server

# Or run in HTTP mode
export SENTINEL_TOKEN=YOUR_SENTINEL_TOKEN
sentinel-mcp-server --mode http
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  AI Client                          │
│  (Claude Desktop / Cursor / Claude Code / Codex)    │
└──────────────┬──────────────────────────────────────┘
               │  MCP Protocol (stdio or HTTP/SSE)
               ▼
┌──────────────────────────────────────┐
│     Priceminder MCP Server           │
│  ┌────────────────────────────────┐  │
│  │  Tool Registry (10 tools)     │  │
│  │  - get_monitor_list           │  │
│  │  - get_price_summary          │  │
│  │  - get_price_history          │  │
│  │  - get_alerts                 │  │
│  │  - add_monitor                │  │
│  │  - ...                        │  │
│  └──────────────┬─────────────────┘  │
│                 │ HTTP + Token Auth
│  ┌──────────────▼─────────────────┐  │
│  │  API Client (httpx)           │  │
│  └──────────────┬─────────────────┘  │
└─────────────────┼────────────────────┘
                  │ HTTPS
┌─────────────────▼────────────────────┐
│     Priceminder REST API             │
│  (User Mgmt / Monitor / Price / Alert)│
└─────────────────┬────────────────────┘
                  │
┌─────────────────▼────────────────────┐
│     PostgreSQL 16                    │
│  (Price History / Users / Alerts)    │
└──────────────────────────────────────┘
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SENTINEL_API_BASE` | Backend API base URL | `https://priceminder.online/shopee` |
| `SENTINEL_TOKEN` | Your authentication token | **(required)** |
| `SENTINEL_API_KEY` | API key for backend auth | `sentinel-mvp-2026` |
| `SENTINEL_TIMEOUT` | HTTP request timeout (s) | `30` |
| `MCP_MODE` | Run mode: `stdio` or `http` | `stdio` |
| `MCP_HOST` | HTTP server bind address | `127.0.0.1` |
| `MCP_PORT` | HTTP server port | `8082` |
| `LOG_LEVEL` | Log level | `INFO` |

---

## 💬 Usage Examples

Once configured, you can ask your AI agent things like:

**Price monitoring:**
- "Show me my tracked products on Shopee SG"
- "What's the price trend for the iPhone 14 I'm monitoring?"
- "Has any competitor dropped prices in the last 3 days?"

**Adding products:**
- "Track this product: https://shopee.sg/product-123"
- "Add this Samsung TV to my watchlist"

**Alerts & insights:**
- "Any new price drop alerts?"
- "How's the crawler system running today?"
- "Give me a dashboard overview"

---

## 📡 API Reference

### Authentication

All API calls require these headers:

```bash
X-Api-Key: sentinel-mvp-2026
X-Sentinel-Token: YOUR_TOKEN
```

### Generate MCP Key

```bash
curl -X POST https://priceminder.online/shopee/mcp/generate-key \
  -H "X-Api-Key: sentinel-mvp-2026" \
  -H "X-Sentinel-Token: YOUR_TOKEN"
```

### Verify MCP Key (MCP Server Internal)

```bash
curl https://priceminder.online/shopee/mcp/verify-key?key=YOUR_MCP_KEY \
  -H "X-MCP-Internal-Key: sentinel-mcp-internal-2026"
```

---

## 🆓 Free vs Pro

| Feature | Free | Pro |
|---------|------|-----|
| Active monitors | 5 max | Unlimited |
| Price history | 3 days | 90 days |
| Price summary | 3 days | 90 days |
| Call rate | 60/hour | Unlimited |
| Real-time alerts | — | ✅ |
| Priority support | — | ✅ |

---

## 🛠️ Development

```bash
git clone https://github.com/haidrau/sentinel-mcp-server.git
cd sentinel-mcp-server

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Start in dev mode
export SENTINEL_TOKEN=your-test-token
python -m sentinel_mcp.server
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Open issues for bugs or feature requests
- Submit PRs for new tools or improvements
- Ask questions in the discussions

---

## 🌐 Links

- **Website**: [priceminder.online](https://priceminder.online)
- **GitHub**: [github.com/haidrau/sentinel-mcp-server](https://github.com/haidrau/sentinel-mcp-server)
- **Gitee**: [gitee.com/haidrau/sentinel-mcp-server](https://gitee.com/haidrau/sentinel-mcp-server)
- **MCP Directory**: [mcp.so/server/sentinel-mcp-server](https://mcp.so)