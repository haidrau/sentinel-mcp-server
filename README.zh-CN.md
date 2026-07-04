# 盯价哨兵 MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-purple)](https://modelcontextprotocol.io)
[![Website](https://img.shields.io/badge/Web-priceminder.online-green)](https://priceminder.online)

[**English**](README.md) | [中文](README.zh-CN.md)

> **盯价哨兵** — 基于 MCP（Model Context Protocol）协议的 Shopee 竞品价格实时监控 AI 工具。让 AI 助手帮你盯住东南亚电商对手的一举一动。

官网：[**priceminder.online**](https://priceminder.online) → 免费注册，立即开始监控

---

## 🌟 功能一览

| # | 工具 | 说明 | 类型 |
|---|------|------|------|
| 1 | `get_monitor_list` | 查看所有正在监控的商品 | 🔍 查询 |
| 2 | `get_price_summary` | 所有监控商品的批量价格汇总 | 🔍 查询 |
| 3 | `get_price_history` | 指定商品的价格变动时间线 | 🔍 查询 |
| 4 | `get_alerts` | 查看降价提醒列表 | 🔍 查询 |
| 5 | `add_monitor` | 添加新品到监控列表 | ⚡ 操作 |
| 6 | `update_monitor_status` | 暂停/恢复监控 | ⚡ 操作 |
| 7 | `mark_alert_read` | 标记提醒为已读 | ⚡ 操作 |
| 8 | `get_crawl_health` | 爬虫引擎运行状态 | 📊 洞察 |
| 9 | `get_monitor_overview` | 全局监控看板 | 📊 洞察 |
| 10 | `search_my_products` | 按关键词搜索已监控商品 | 📊 洞察 |

---

## 🚀 快速开始

### 方案 A：托管 HTTP（推荐 — 零配置）

任何支持 MCP 的 AI 客户端，添加以下 URL 即可：

```
https://priceminder.online/mcp_server?key=***
```

**第一步：获取 MCP Key**
- 前往 [priceminder.online](https://priceminder.online) 注册
- 或直接调用 API 生成（见下方 [API 参考](#-api-参考)）

**第二步：配置 AI 客户端**

**Claude Desktop / Cursor / Cherry Studio：**

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

**Claude Code：**

```bash
claude mcp add priceminder --type http --url "https://priceminder.online/mcp_server?key=***"
```

### 方案 B：Docker 自建

```bash
docker run -d \
  --name priceminder-mcp \
  -p 8082:8082 \
  -e SENTINEL_API_BASE=https://priceminder.online/shopee \
  -e SENTINEL_TOKEN=YOUR_SENTINEL_TOKEN \
  -e SENTINEL_API_KEY=sentinel-mvp-2026 \
  ghcr.io/haidrau/sentinel-mcp-server:latest
```

### 方案 C：pip 安装

```bash
pip install sentinel-mcp-server

# stdio 模式（适用于 Claude Desktop、Cursor 等）
export SENTINEL_TOKEN=YOUR_SENTINEL_TOKEN
sentinel-mcp-server

# HTTP 模式
export SENTINEL_TOKEN=YOUR_SENTINEL_TOKEN
sentinel-mcp-server --mode http
```

---

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────┐
│                  AI 客户端                            │
│  (Claude Desktop / Cursor / Claude Code / Codex)     │
└──────────────┬──────────────────────────────────────┘
               │  MCP 协议 (stdio 或 HTTP/SSE)
               ▼
┌──────────────────────────────────────┐
│     盯价哨兵 MCP Server              │
│  ┌────────────────────────────────┐  │
│  │  工具注册（10 个工具）         │  │
│  │  - get_monitor_list           │  │
│  │  - get_price_summary          │  │
│  │  - get_price_history          │  │
│  │  - get_alerts                 │  │
│  │  - add_monitor                │  │
│  │  - ...                        │  │
│  └──────────────┬─────────────────┘  │
│                 │ HTTP + Token 认证  │
│  ┌──────────────▼─────────────────┐  │
│  │  API 客户端 (httpx)           │  │
│  └──────────────┬─────────────────┘  │
└─────────────────┼────────────────────┘
                  │ HTTPS
┌─────────────────▼────────────────────┐
│     盯价哨兵 REST API                 │
│  (用户管理 / 监控 / 价格 / 预警)     │
└─────────────────┬────────────────────┘
                  │
┌─────────────────▼────────────────────┐
│     PostgreSQL 16                    │
│  (价格历史 / 用户 / 预警)           │
└──────────────────────────────────────┘
```

---

## 🔧 配置参数

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SENTINEL_API_BASE` | 后端 API 地址 | `https://priceminder.online/shopee` |
| `SENTINEL_TOKEN` | 你的认证令牌 | **（必填）** |
| `SENTINEL_API_KEY` | 后端 API 密钥 | `sentinel-mvp-2026` |
| `SENTINEL_TIMEOUT` | HTTP 请求超时（秒） | `30` |
| `MCP_MODE` | 运行模式：`stdio` 或 `http` | `stdio` |
| `MCP_HOST` | HTTP 服务绑定地址 | `127.0.0.1` |
| `MCP_PORT` | HTTP 服务端口 | `8082` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

---

## 💬 使用示例

配置完成后，直接跟你的 AI 助手说：

**价格监控：**
- "帮我看看我在 Shopee 新加坡站监控了哪些商品"
- "iPhone 14 的最近价格走势怎么样？"
- "最近 3 天有竞品降价了吗？"

**添加商品：**
- "帮我监控这个商品：https://shopee.sg/product-123"
- "把这款三星电视加入监控列表"

**预警与洞察：**
- "有没有新的降价提醒？"
- "爬虫系统今天运行正常吗？"
- "给我看看今天的监控总览"

---

## 📡 API 参考

### 认证

所有 API 调用需要以下请求头：

```bash
X-Api-Key: sentinel-mvp-2026
X-Sentinel-Token: YOUR_TOKEN
```

### 生成 MCP Key

```bash
curl -X POST https://priceminder.online/shopee/mcp/generate-key \
  -H "X-Api-Key: sentinel-mvp-2026" \
  -H "X-Sentinel-Token: YOUR_TOKEN"
```

---

## 🆓 免费版 vs Pro 版

| 功能 | 免费版 | Pro 版 |
|------|--------|--------|
| 活跃监控数 | 最多 5 个 | 不限 |
| 价格历史 | 3 天 | 90 天 |
| 价格汇总 | 3 天 | 90 天 |
| 调用频率 | 60 次/小时 | 不限 |
| 实时告警 | — | ✅ |
| 优先支持 | — | ✅ |

立即升级 👉 [priceminder.online](https://priceminder.online)

---

## 🛠️ 开发

```bash
git clone https://github.com/haidrau/sentinel-mcp-server.git
cd sentinel-mcp-server

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
python -m pytest tests/

# 启动开发模式
export SENTINEL_TOKEN=your-test-token
python -m sentinel_mcp.server
```

---

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE)。

---

## 🤝 贡献

欢迎贡献代码！你可以：
- 提 Issue 报告 Bug 或建议新功能
- 提交 PR 增加新工具或改进
- 在 Discussions 里提问交流

---

## 🌐 链接

- **官网**：[priceminder.online](https://priceminder.online) ← 免费注册
- **GitHub**：[github.com/haidrau/sentinel-mcp-server](https://github.com/haidrau/sentinel-mcp-server)
- **Gitee**：[gitee.com/haidrau/sentinel-mcp-server](https://gitee.com/haidrau/sentinel-mcp-server)
- **MCP 目录**：[mcp.so/server/sentinel-mcp-server](https://mcp.so)