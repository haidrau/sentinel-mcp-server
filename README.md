# sentinel-mcp-server

Shopee 盯价哨兵 MCP Server — 让 AI Agent 接入竞品价格监控

---

## 一、项目概述

本项目包含三部分交付物：

| 交付物 | 目录 | 说明 |
|--------|------|------|
| MCP Server | `src/sentinel_mcp/` | Python 包，用户在本地运行，通过 MCP 协议让 AI Agent 调用我们的价格监控能力 |
| 落地页 | `docs/index.html` | 静态 HTML 产品文档页，部署到 Nginx 供用户浏览 |
| 后端 API 改动 | 在 `shopee-sentinel-api` 仓库 | 4 处改动，支持 MCP Tool 需要的批量摘要、enriched alerts、keyword 搜索、user dashboard |

### 架构图

```
用户 (AI 客户端)
    │ MCP 协议 (stdio)
    ▼
sentinel-mcp-server  ← 用户本地运行（pip install）
    │ HTTP + X-Sentinel-Token
    ▼
Sentinel REST API    ← 帆帆部署的服务器 (priceminder.online)
    │
    ▼
PostgreSQL DB
```

---

## 二、部署清单（给帆帆）

### 2.1 后端 API 改动部署

`shopee-sentinel-api` 仓库有 4 个文件改动，需要拉取最新代码后重新部署：

| 文件 | 改动说明 |
|------|----------|
| `app/routers/price.py` | `GET /price/summary` — monitor_id 改为可选，新增 site/days 参数，支持批量模式（不传 ID 返回所有活跃监控摘要） |
| `app/routers/alerts.py` | `GET /alerts` — 返回补充 product_name、shop_name、site、currency、unread_count（join Monitor 表） |
| `app/routers/monitors.py` | `GET /monitors` — 新增 keyword 查询参数（ilike 模糊匹配商品名/店铺名） |
| `app/routers/user_settings.py` | 新增 `GET /user/dashboard` — 用户级监控大盘（从 admin/dashboard 降级，只看自己的数据） |

**部署步骤**：

```bash
# 1. 拉取最新代码
cd /path/to/shopee-sentinel-api
git pull origin master

# 2. 重启服务（根据你的部署方式）
# 如果用 systemd:
sudo systemctl restart sentinel-api
# 如果用 docker:
docker restart sentinel-api
# 如果用 supervisor:
sudo supervisorctl restart sentinel-api

# 3. 验证新端点
# 批量摘要（不传 monitor_id）
curl -s -H "X-Sentinel-Token: 你的token" \
  "https://priceminder.online/api/v1/price/summary?days=3" | python -m json.tool

# alerts enriched 字段
curl -s -H "X-Sentinel-Token: 你的token" \
  "https://priceminder.online/api/v1/alerts?size=3" | python -m json.tool

# keyword 搜索
curl -s -H "X-Sentinel-Token: 你的token" \
  "https://priceminder.online/api/v1/monitors?keyword=iPhone" | python -m json.tool

# user dashboard
curl -s -H "X-Sentinel-Token: 你的token" \
  "https://priceminder.online/api/v1/user/dashboard" | python -m json.tool
```

### 2.2 落地页部署

`docs/index.html` 是一个纯静态 HTML 文件（无构建步骤），直接放到 Nginx 即可。

**部署步骤**：

```bash
# 1. 拉取本仓库最新代码
cd /path/to/sentinel-mcp-server
git pull origin master

# 2. 将 docs/ 目录复制到 Nginx 静态文件目录
# 假设 Panel 已经在 Nginx 的 /panel/ 下
# MCP 落地页建议放在 /priceminder/mcp/ 路径下

sudo cp docs/index.html /usr/share/nginx/html/priceminder/mcp/index.html
# 或者根据你的 Nginx 配置调整路径

# 3. 验证
# 浏览器访问: https://priceminder.online/priceminder/mcp/
```

**Nginx 配置参考**（如果需要新增 location）：

```nginx
# 在现有的 server 块中添加
location /priceminder/mcp/ {
    alias /usr/share/nginx/html/priceminder/mcp/;
    index index.html;
    try_files $uri $uri/ /priceminder/mcp/index.html;
}
```

### 2.3 MCP Server 本身

MCP Server 是用户在本地运行的 Python 包，**不需要服务端部署**。用户通过 `pip install sentinel-mcp-server` 安装后，在 AI 客户端中配置即可。

后续如果需要"托管模式"（用户只配 URL 不装包），再考虑服务端部署，当前 MVP 不需要。

---

## 三、项目文件结构

```
sentinel-mcp-server/
├── pyproject.toml              # Python 包定义（hatchling 构建）
├── README.md                   # 本文件
├── .gitignore
├── src/sentinel_mcp/
│   ├── __init__.py
│   ├── server.py               # MCP Server 入口，注册 10 个 Tool
│   ├── config.py               # 环境变量配置
│   ├── api_client.py           # HTTP 客户端（GET/POST/PUT/PATCH/DELETE）
│   └── tools/
│       ├── __init__.py
│       ├── monitors.py         # 4 个 Tool: list, add, update_status, search
│       ├── prices.py           # 2 个 Tool: summary, history
│       ├── alerts.py           # 2 个 Tool: get_alerts, mark_read
│       └── insights.py         # 2 个 Tool: crawl_health, monitor_overview
├── docs/
│   └── index.html              # 产品落地页（静态 HTML）
└── tests/
    └── (待补充)
```

---

## 四、MCP Tool 清单 (10 Tools)

### Tier 1 — 查询

| Tool | 说明 | 对应 API |
|------|------|----------|
| `get_monitor_list` | 获取监控列表 | `GET /monitors` |
| `get_price_summary` | 价格摘要（支持批量） | `GET /price/summary` |
| `get_price_history` | 价格时间序列 | `GET /price/history` |
| `get_alerts` | 预警列表 | `GET /alerts` |

### Tier 2 — 操作

| Tool | 说明 | 对应 API |
|------|------|----------|
| `add_monitor` | 添加监控 | `POST /monitors` |
| `update_monitor_status` | 暂停/恢复 | `PUT /monitors/{id}` |
| `mark_alert_read` | 标记预警已读 | `PUT /alerts/{id}/read` |

### Tier 3 — 洞察

| Tool | 说明 | 对应 API |
|------|------|----------|
| `get_crawl_health` | 采集健康度 | `GET /telemetry/summary` + `/telemetry/site-stats` |
| `get_monitor_overview` | 监控大盘 | `GET /user/dashboard` |
| `search_my_products` | 搜索监控 | `GET /monitors?keyword=xxx` |

---

## 五、用户配置方式

用户在 MCP 客户端中添加以下配置：

### OpenClaw / Cherry Studio / Claude Desktop

```json
{
  "mcpServers": {
    "sentinel": {
      "command": "uvx",
      "args": ["sentinel-mcp-server"],
      "env": {
        "SENTINEL_API_BASE": "https://priceminder.online/api/v1",
        "SENTINEL_TOKEN": "用户的 API Token"
      }
    }
  }
}
```

### Cursor

在 `.cursor/mcp.json` 中添加同样的配置。

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SENTINEL_API_BASE` | Sentinel REST API 地址 | `https://priceminder.online/api/v1` |
| `SENTINEL_TOKEN` | 用户认证 Token（必填） | — |
| `SENTINEL_TIMEOUT` | HTTP 请求超时（秒） | `30` |

---

## 六、本地开发

```bash
# 克隆项目
git clone https://gitee.com/haidrau/sentinel-mcp-server.git
cd sentinel-mcp-server

# 安装（开发模式）
pip install -e .

# 设置 Token 并运行
export SENTINEL_TOKEN="your-test-token"
python -m sentinel_mcp.server

# 验证 10 个 Tool 是否注册成功
python -c "from sentinel_mcp.server import TOOLS; print([t.name for t in TOOLS])"
```

---

## 七、测试验证清单

帆帆部署完 API 改动和落地页后，按以下步骤验证：

### Step 1: 验证 API 改动

```bash
# 批量摘要（关键：不传 monitor_id，应返回 items 数组）
curl -s -H "X-Sentinel-Token: 你的token" \
  "https://priceminder.online/api/v1/price/summary?days=3"

# alerts 应有 product_name 等字段
curl -s -H "X-Sentinel-Token: 你的token" \
  "https://priceminder.online/api/v1/alerts?size=2"

# keyword 搜索
curl -s -H "X-Sentinel-Token: 你的token" \
  "https://priceminder.online/api/v1/monitors?keyword=test"

# user dashboard（新端点）
curl -s -H "X-Sentinel-Token: 你的token" \
  "https://priceminder.online/api/v1/user/dashboard"
```

### Step 2: 验证落地页

浏览器访问 `https://priceminder.online/priceminder/mcp/`，确认页面正常渲染。

### Step 3: 端到端 MCP 测试

1. 在本地安装 MCP Server: `pip install -e .`（或 `pip install sentinel-mcp-server`）
2. 在 OpenClaw/Cherry Studio 中配置 MCP（见上方"用户配置方式"）
3. 对 AI 说以下测试语句：
   - "我的监控列表" → 应调用 get_monitor_list
   - "竞品最近价格怎么样" → 应调用 get_price_summary
   - "有没有新的降价预警" → 应调用 get_alerts
   - "采集系统运行正常吗" → 应调用 get_crawl_health

---

## License

MIT
