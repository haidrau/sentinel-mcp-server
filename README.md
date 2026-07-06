# Priceminder MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-purple)](https://modelcontextprotocol.io)
[![Website](https://img.shields.io/badge/Web-priceminder.online-green)](https://priceminder.online)

[**中文**](README.zh-CN.md) | [English](README.md)

> **Priceminder** — Real-time Shopee competitor price monitoring, powered by AI agents through the Model Context Protocol (MCP).

🌐 **Sign up free**: [priceminder.online](https://priceminder.online)

Monitor competitor prices across Shopee Southeast Asia (SG, MY, TH, VN, ID, PH). Let your AI agent track, analyze, and alert on price movements — all through natural language.

---

## 📊 Why Priceminder?

**Real-time, not yesterday.** Most price monitoring tools — including alternative MCP servers — return T-1 (yesterday's cached) data. Priceminder crawls prices **3 times daily**, giving you near-real-time visibility.

| Capability | Other MCP Servers | Priceminder |
|---|---|---|
| **Data freshness** | T-1 (yesterday) | **T-0 (same-day, 3× daily)** |
| **Price change detection** | Next day | **Within 4–8 hours** |
| **Flash sale / 9.9 / 11.11** | Misses intra-day moves | **Catches hourly adjustments** |
| **Push notifications** | ❌ Query-only | ✅ Feishu/DingTalk/Telegram |
| **Self-hosted** | ✅ Supported | ✅ Supported |

**In short:** If you're using other tools, you're making decisions on yesterday's data. Priceminder tells you what's happening **right now** — and pushes alerts when competitors move.

---

## 🌟 Features

| # | Tool | Description | Tier |
|---|---|---|---|
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
https://priceminder.online/mcp_server?key=***
```

**Step 1: Get your MCP Key**
- Visit [priceminder.online](https://priceminder.online) to sign up
- Or call the API directly (see [API Reference](#-api-reference))

**Step 2: Configure your AI client**

**Claude Desktop / Cursor / Cherry Studio:**

```json
{
  "mcpServers": {
    "priceminder": {
      "type": "http",
      "url": "https://priceminder.online/mcp_server?key=***"
    }
  }
}
```

**Claude Code:**

```bash
claude mcp add priceminder --type http --url "https://priceminder.online/mcp_server?key=***"
```

### Option B: Self-Hosted (Docker — One Command)

```bash
bash docker-run.sh YOUR_SENTINEL_TOKEN
```

The script handles image pull, container lifecycle, health check, and logs everything. See [`docker-run.sh`](docker-run.sh) for details.

Or run directly:

```bash
docker run -d \
  --name priceminder-mcp \
  --restart unless-stopped \
  -p 8082:8082 \
  -e SENTINEL_TOKEN=YOUR_SENTINEL_TOKEN \
  -e SENTINEL_API_KEY=sentinel-mvp-2026 \
  -e SENTINEL_API_BASE=https://priceminder.online/shopee \
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

## 💬 Prompt Scenarios

Once configured, here are **3 real-world scenarios** you can run — each demonstrating a different use case:

### 1️⃣ Store-Level Price Watch

> *"Monitor all products from Shopee store 'ABC Official Store' on Shopee SG. If any product drops more than 5% in the last 24 hours, summarize the changes."*

Your AI agent will:
1. Add each product from the store to your monitor list
2. Cross-reference prices against the latest crawl
3. Return a summary of SKUs that dropped below the 5% threshold

**Best for:** Brand competition — keep tabs on a specific competitor's entire catalog.

### 2️⃣ Flash Sale / Campaign Alert

> *"Check every 4 hours during the 7.7 sale — alert me if any of my tracked products have a price change of 3% or more. Show only the products that changed."*

Your AI agent will:
1. Call `get_price_summary` to get current vs previous prices
2. Filter for products with ≥3% movement
3. Present a clean before/after comparison

**Best for:** Campaign periods — don't wake up to yesterday's data when competitors adjust prices hourly.

### 3️⃣ Price Drop Intelligence

> *"Show me all price drop alerts from the last 2 days. Which products dropped the most? Highlight any drops over 10%."*

Your AI agent will:
1. Call `get_alerts` for recent notifications
2. Call `get_price_history` on the biggest movers for deeper context
3. Rank by drop percentage and highlight critical moves

**Best for:** Buying decisions — spot the deepest discounts and cheapest time to restock.

---

## 🔗 n8n Integration

Priceminder ships with a ready-to-import n8n workflow template.

**File:** [`priceminder-mcp-n8n.json`](priceminder-mcp-n8n.json)

### What it does

The template sets up an automated price watchdog on a 4-hour cron:

```
Schedule ─► Get Price Summary ─► Parse Drops ─► Has Drops? ─┬► Telegram Alert
(4h cron)                                                     ├► Email Alert
                                                              └► Log (no drops)
```

### Import

1. Open n8n → **Workflows** → **Import from File**
2. Select `priceminder-mcp-n8n.json`
3. Configure your credentials:
   - `SENTINEL_TOKEN` (set as env var on the n8n host)
   - Telegram bot token + chat ID (if using Telegram output)
   - SMTP credentials (if using Email output)
4. **Activate** the workflow

> 💡 The MCP HTTP node connects to `http://localhost:8082/mcp` — make sure your Docker container is running on the same machine as n8n, or update the URL accordingly.

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
|---|---|---|
| `SENTINEL_API_BASE` | Backend API base URL | `https://priceminder.online/shopee` |
| `SENTINEL_TOKEN` | Your authentication token | **(required)** |
| `SENTINEL_API_KEY` | API key for backend auth | `sentinel-mvp-2026` |
| `SENTINEL_TIMEOUT` | HTTP request timeout (s) | `30` |
| `MCP_MODE` | Run mode: `stdio` or `http` | `stdio` |
| `MCP_HOST` | HTTP server bind address | `127.0.0.1` |
| `MCP_PORT` | HTTP server port | `8082` |
| `LOG_LEVEL` | Log level | `INFO` |

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
curl https://priceminder.online/shopee/mcp/verify-key?key=*** \
  -H "X-MCP-Internal-Key: sentinel-mcp-internal-2026"
```

---

## 🆓 Free vs Pro

| Feature | Free | Pro |
|---|---|---|
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