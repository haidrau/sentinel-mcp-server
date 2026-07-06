# 盯价哨兵 MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-purple)](https://modelcontextprotocol.io)
[![Website](https://img.shields.io/badge/Web-priceminder.online-green)](https://priceminder.online)

[**English**](README.md) | [中文](README.zh-CN.md)

> **盯价哨兵** — 基于 MCP（Model Context Protocol）协议的 Shopee 竞品价格实时监控 AI 工具。让 AI 助手帮你盯住东南亚电商对手的一举一动。

官网：[**priceminder.online**](https://priceminder.online) → 免费注册，立即开始监控

---

## 📊 为什么选盯价哨兵？

**准实时，不是昨天数据。** 市面上同类 MCP 工具（如 Sorftime）返回的是 T-1（昨日缓存）数据。盯价哨兵每天爬取价格 **3 次**，让你在大促期间看到的是小时级的变动，而不是隔夜的老黄历。

| 能力 | 其他 MCP 工具 | 盯价哨兵 |
|---|---|---|
| **数据时效** | T-1（昨日数据） | **T-0（当天，每天 3 次）** |
| **价格变动检测** | 次日才能看到 | **4~8 小时内通知** |
| **大促期间（9.9/11.11）** | 错过当日多次调价 | **捕捉小时级变化** |
| **推送通知** | ❌ 只能查询 | ✅ 飞书/钉钉/Telegram |
| **自建部署** | ✅ 支持 | ✅ 支持（一键脚本） |

**一句话：** 用其他工具，你在拿昨天的数据做今天的决策。盯价哨兵告诉你**现在**发生了什么——竞品一调价，你第一个知道。

---

## 🌟 功能一览

| # | 工具 | 说明 | 类型 |
|---|---|---|---|
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

### 方案 B：Docker 自建（一键脚本）

```bash
bash docker-run.sh 你的_SENTINEL_TOKEN
```

脚本自动处理：拉取镜像、启动容器、健康检查、输出配置信息。详见 [`docker-run.sh`](docker-run.sh)。

或直接运行：

```bash
docker run -d \
  --name priceminder-mcp \
  --restart unless-stopped \
  -p 8082:8082 \
  -e SENTINEL_TOKEN=你的_SENTINEL_TOKEN \
  -e SENTINEL_API_KEY=sentinel-mvp-2026 \
  -e SENTINEL_API_BASE=https://priceminder.online/shopee \
  ghcr.io/haidrau/sentinel-mcp-server:latest
```

### 方案 C：pip 安装

```bash
pip install sentinel-mcp-server

# stdio 模式（适用于 Claude Desktop、Cursor 等）
export SENTINEL_TOKEN=你的_SENTINEL_TOKEN
sentinel-mcp-server

# HTTP 模式
export SENTINEL_TOKEN=你的_SENTINEL_TOKEN
sentinel-mcp-server --mode http
```

---

## 💬 实战场景 Prompt

以下 **3 个场景** 展示盯价哨兵在真实运营中的威力——每条指令都可以直接对 Claude 说：

### 📍 场景一：盯死竞品店铺

> *"监控 Shopee 新加坡站 'ABC Official Store' 的所有商品。如果任何商品在最近 24 小时内降价超过 5%，给我汇总所有变动。"*

AI 助手将：
1. 将店铺的所有 SKU 添加到监控列表
2. 对比最新爬取的价格数据
3. 汇总降价幅度超过 5% 的商品

**适合人群：** 品牌竞争——死死盯住某个竞品店铺的整盘货。

### 🔥 场景二：大促实时盯盘

> *"7.7 大促期间，每 4 小时检查一次我的监控商品。如果有任何商品价格变动超过 3%，立刻推送给我，只显示变动的商品。"*

AI 助手将：
1. 调用 `get_price_summary` 获取当前 vs 上次价格
2. 筛选出变动 ≥3% 的商品
3. 输出简洁的前后对比清单

**适合人群：** 大促运营——竞品在 7.7 当天可能每小时调价一次，你不能等到明天才看到。

### 📉 场景三：降价情报挖掘

> *"看下最近 2 天有哪些降价提醒。哪些商品降得最多？把降幅超过 10% 的标红显示。"*

AI 助手将：
1. 调用 `get_alerts` 获取所有提醒
2. 对降幅最大的商品调用 `get_price_history` 深挖走势
3. 按降幅排序，高亮关键变动

**适合人群：** 采购/补货决策——发现最低入手时机。

---

## 🔗 n8n 自动化工坊

盯价哨兵自带一个开箱即用的 n8n 工作流模板。

**文件：** [`priceminder-mcp-n8n.json`](priceminder-mcp-n8n.json)

### 工作流程

定时触发器（每 4 小时）→ 获取价格汇总 → 解析降价 → 判断是否有降价 → 推送告警（Telegram/邮件）→ 无事则记录日志

```
定时触发 ─► 获取汇总 ─► 解析降价 ─► 有降价？ ─┬► Telegram 通知
(每4小时)                                       ├► 邮件通知
                                                └► 无事记录（稳定运行）
```

### 导入方法

1. 打开 n8n → **工作流** → **从文件导入**
2. 选择 `priceminder-mcp-n8n.json`
3. 配置凭证：
   - `SENTINEL_TOKEN`（在 n8n 所在服务器设为环境变量）
   - Telegram Bot Token + Chat ID（如果用 Telegram 推送）
   - SMTP 凭证（如果用邮件推送）
4. **激活**工作流即可开始自动盯价

> 💡 MCP HTTP 节点访问的是 `http://localhost:8082/mcp`——确保 Docker 容器和 n8n 在同一台机器上，否则需要修改 URL。

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
|---|---|---|
| `SENTINEL_API_BASE` | 后端 API 地址 | `https://priceminder.online/shopee` |
| `SENTINEL_TOKEN` | 你的认证令牌 | **（必填）** |
| `SENTINEL_API_KEY` | 后端 API 密钥 | `sentinel-mvp-2026` |
| `SENTINEL_TIMEOUT` | HTTP 请求超时（秒） | `30` |
| `MCP_MODE` | 运行模式：`stdio` 或 `http` | `stdio` |
| `MCP_HOST` | HTTP 服务绑定地址 | `127.0.0.1` |
| `MCP_PORT` | HTTP 服务端口 | `8082` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

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
|---|---|---|
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