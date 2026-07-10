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

## 📌 Important: Understand the Data Pipeline First

Priceminder's MCP service **does not work standalone**. It depends on real competitor price data collected by the browser extension. Please understand this 3-layer pipeline before using:

```
Install Extension → Browse Shopee & Click "Monitor" → Data Stored → AI Can Query
```

### ⚠️ Prerequisites

| Step | Action | Details |
|------|--------|---------|
| **Required** | ① Install the browser extension | Chrome / Edge / 360 Browser — see [Extension Installation Guide](https://priceminder.online/docs/extensions/) |
| **Required** | ② Browse Shopee product pages, click "Monitor Now" | Only products you manually add to monitoring are accessible via MCP |
| **Required** | ③ Get your **MCP Key** from extension settings | See [Quick Start](#-quick-start) below |
| **Optional** | ④ Configure MCP in your AI client | Then you can query prices via natural language |

> 🔑 **Where to get your MCP Key?**
> The MCP Key is displayed in the **browser extension settings page**. No extension → No Key → No MCP service. The website registration (priceminder.online) is for account management and Pro upgrades — the MCP access credential lives inside the extension.

### 🤖 AI Capability Boundaries

Priceminder's MCP tools can **only query products you've manually added to your monitoring list**. It cannot arbitrarily search all of Shopee.

| AI Can Do ✅ | AI Cannot Do ❌ |
|---|---|
| List my monitored products and prices | Search Shopee for products I haven't monitored |
| View price history and trends of monitored items | Get pricing for any arbitrary ASIN/product ID |
| Check price drop alerts and push records | Analyze competitor stores I'm not tracking |
| Add new products to monitor (requires extension scan first) | Auto-discover new competitors |
| Check crawler engine health status | Modify my account password or settings |

**In short: The extension collects the data, MCP lets AI analyze what you've already collected.**

For full capability details, see the [**MCP Tools Overview →**](https://priceminder.online/docs/tools/overview)

---

## 📊 Why Priceminder?

**Real-time, not yesterday.** Most price monitoring tools — including alternative MCP servers — return T-1 (yesterday's cached) data. Priceminder crawls prices **3 times daily**, giving you near-real-time visibility.

| Capability | Alternative MCP Servers | Priceminder |
|---|---|---|
| **Data freshness** | T-1 (yesterday) | **T-0 (same-day, 3× daily)** |
| **Price change detection** | Next day | **Within 4–8 hours** |
| **Flash sale / 7.7 / 9.9 / 11.11** | Misses intra-day moves | **Catches hourly adjustments** |
| **Push notifications** | ❌ Query-only | ✅ Feishu/DingTalk/Telegram |
| **Self-hosted** | ✅ Supported | ✅ Supported |

**In short:** If you're using other tools, you're making decisions on yesterday's data. Priceminder tells you what's happening **right now** — and pushes alerts when competitors move.

---

## 🌟 Features — 8 MCP Tools

| # | Tool | Description | Category |
|---|---|---|---|
| 1 | `get_monitor_list` | List all products you're tracking | 🔍 Query |
| 2 | `get_price_summary` | Batch price summary across all tracked products | 🔍 Query |
| 3 | `get_price_history` | Price history time-series for a specific product | 🔍 Query |
| 4 | `get_alerts` | List price drop alerts | 🔍 Query |
| 5 | `add_monitor` | Add a new product to your monitor list | ⚡ Action |
| 6 | `update_monitor_status` | Pause or resume monitoring | ⚡ Action |
| 7 | `get_crawl_health` | Check crawler engine health & stats | 📊 Insight |
| 8 | `get_monitor_overview` | Dashboard overview of all monitors | 📊 Insight |

See the full tool documentation here: [**MCP Tools Overview →**](https://priceminder.online/docs/tools/overview)

---

## 🚀 Quick Start

> **Install Extension → Add Products → Get MCP Key → Configure AI Client**

For visual step-by-step guide with screenshots, see the official docs: [**Quick Start Guide →**](https://priceminder.online/docs/quick-start)

### Step 1: Install the Browser Extension

| Browser | Installation |
|---|---|
| **Chrome** | Search "Priceminder" on [Chrome Web Store](https://chromewebstore.google.com) |
| **Edge** | Search "Priceminder" on [Edge Add-ons](https://microsoftedge.microsoft.com/addons) |
| **360 Browser** | Download offline installer from the official website |
| **Opera** | Opera add-ons store |

See [**Extension Installation Guide →**](https://priceminder.online/docs/extensions/) for screenshots.

### Step 2: Add Products to Monitor

Open any Shopee product page (supports SG/MY/TH/ID/TW/PH/VN). A "**Monitor Now**" button will appear at the top-right:

1. Click **"Monitor Now"** → product added to your monitor list
2. The system automatically starts collecting price data at your chosen interval
3. Configure crawl frequency and alert thresholds in the extension settings

> 💡 **You need monitored products first.** Without them, the AI will return empty results when queried. Start by adding at least 5–10 competitor products.

### Step 3: Get Your MCP Key

Open the browser **extension settings page**. Your MCP Key is displayed in the "MCP Configuration" section.

> ⚠️ **The MCP Key is only visible inside the extension settings.** It is not available from the website login.

### Step 4: Configure Your AI Client

**Supported AI Clients (HTTP mode — recommended):**

| Client | How to Configure | Tutorial |
|---|---|---|
| Cherry Studio | Settings → MCP → Add HTTP URL | [Guide →](https://priceminder.online/docs/clients/cherry-studio) |
| OpenClaw | config.yaml → mcp_servers → url | [Guide →](https://priceminder.online/docs/clients/openclaw) |
| Claude Desktop | claude_desktop_config.json → mcpServers | [Guide →](https://priceminder.online/docs/clients/claude-desktop) |
| Cursor | Cursor Settings → MCP → Add HTTP URL | [Guide →](https://priceminder.online/docs/clients/cursor) |
| Cline | Cline MCP Config → Add | [Guide →](https://priceminder.online/docs/clients/cline) |
| Hermes Agent | config.yaml → mcp_servers | [Guide →](https://priceminder.online/docs/clients/hermes-agent) |

Add this URL (replace `***` with your MCP Key):

```json
{
  "mcpServers": {
    "sentinel": {
      "url": "https://priceminder.online/mcp_server?key=***"
    }
  }
}
```

For detailed client setup guides with screenshots, see: [**Client Setup Guides →**](https://priceminder.online/docs/clients/)

### Step 5: Verify the Connection

Test your setup by asking these questions:

| Your Prompt | Tool Called | Expected Result |
|---|---|---|
| "What am I monitoring?" | `get_monitor_list` | Your current monitor list |
| "How are my competitors' prices?" | `get_price_summary` | Price summary (current/baseline/high/low/avg) |
| "Any new price drop alerts?" | `get_alerts` | Unread price drop records |
| "Is the crawler healthy?" | `get_crawl_health` | Crawler engine status |

> ✅ If the AI returns your monitoring data, setup is successful.
>
> ❌ If results are empty, make sure you've added products to monitor via the extension first.

---

## 💬 Prompt Scenarios

Here are **3 real-world scenarios** you can run — each demonstrates a different use case:

### 1️⃣ Store-Level Price Watch

> *"Monitor all products from Shopee store 'ABC Official Store' on Shopee SG. If any product drops more than 5% in the last 24 hours, summarize the changes."*

Your AI agent will:
1. Check your monitor list for this store's products
2. Compare latest crawl prices
3. Return products that dropped below the threshold

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
2. Call `get_price_history` on the biggest movers for context
3. Rank by drop percentage and highlight critical moves

**Best for:** Buying decisions — spot the deepest discounts.

More real-world prompt examples: [**Scenarios & Best Practices →**](https://priceminder.online/docs/scenarios)

---

## 🔗 n8n Integration

Priceminder ships with a ready-to-import n8n workflow template.

**File:** [`priceminder-mcp-n8n.json`](priceminder-mcp-n8n.json)

### Workflow

```
Schedule ─► Get Price Summary ─► Parse Drops ─► Has Drops? ─┬► Telegram Alert
(4h cron)                                                     ├► Email Alert
                                                              └► Log (no drops)
```

### Import

1. Open n8n → **Workflows** → **Import from File**
2. Select `priceminder-mcp-n8n.json`
3. Configure credentials:
   - `SENTINEL_TOKEN` (env var on the n8n host)
   - Telegram bot token + chat ID (optional)
   - SMTP credentials (optional)
4. **Activate** the workflow

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  AI Client                          │
│  (Claude Desktop / Cursor / Cherry Studio / Hermes) │
└──────────────┬──────────────────────────────────────┘
               │  MCP Protocol (stdio or HTTP/SSE)
               ▼
┌──────────────────────────────────────┐
│     Priceminder MCP Server           │
│  ┌────────────────────────────────┐  │
│  │  Tool Registry (8 tools)      │  │
│  │  - get_monitor_list           │  │
│  │  - get_price_summary          │  │
│  │  - get_price_history          │  │
│  │  - get_alerts                 │  │
│  │  - add_monitor                │  │
│  │  - get_crawl_health           │  │
│  │  - get_monitor_overview       │  │
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

### Data Flow

```
① Browser extension collects data
      │
      ▼
② Backend API stores → PostgreSQL
      │
      ▼
③ MCP Server reads via API
      │
      ▼
④ AI client queries via MCP protocol
```

**Key point:** Data flows one way — extension collects → backend stores → MCP reads. AI clients cannot write data without the extension.

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SENTINEL_API_BASE` | Backend API base URL | `https://priceminder.online/shopee` |
| `SENTINEL_TOKEN` | Your authentication token | **(required)** |
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

Upgrade now 👉 [priceminder.online](https://priceminder.online)

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

- **Website**: [priceminder.online](https://priceminder.online) ← Sign up free
- **Official Docs**: [priceminder.online/docs](https://priceminder.online/docs/)
- **Quick Start**: [priceminder.online/docs/quick-start](https://priceminder.online/docs/quick-start)
- **MCP Tools Overview**: [priceminder.online/docs/tools/overview](https://priceminder.online/docs/tools/overview)
- **GitHub**: [github.com/haidrau/sentinel-mcp-server](https://github.com/haidrau/sentinel-mcp-server)
- **Gitee**: [gitee.com/haidrau/sentinel-mcp-server](https://gitee.com/haidrau/sentinel-mcp-server)