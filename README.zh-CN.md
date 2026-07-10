# 盯价哨兵 MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-purple)](https://modelcontextprotocol.io)
[![Website](https://img.shields.io/badge/Web-priceminder.online-green)](https://priceminder.online)

[**English**](README.md) | [中文](README.zh-CN.md)

> **盯价哨兵** — 基于 MCP（Model Context Protocol）协议的 Shopee 竞品价格实时监控 AI 工具。让 AI 助手帮你盯住东南亚电商对手的一举一动。

🌐 官网：[**priceminder.online**](https://priceminder.online) → 免费注册，立即开始监控

---

## 📌 重要说明：先理解产品数据链路

盯价哨兵的 MCP 服务**不是独立运行的**，它依赖于浏览器扩展采集的真实竞品数据。请在使用前理解以下**三层数据链路**：

```
安装扩展 → 浏览 Shopee 并点击「监测」→ 数据入库 → AI 对话查询
```

详细的产品架构请参考官网文档：[**产品架构总览 →**](https://priceminder.online/docs/quick-start)

### ⚠️ 使用前提

| 步骤 | 操作 | 说明 |
|------|------|------|
| **必须** | ① 安装浏览器扩展 | Chrome / Edge / 360 浏览器 — 参见[扩展安装指南](https://priceminder.online/docs/extensions/) |
| **必须** | ② 浏览 Shopee 商品页，点击「立即监测」 | 只有被你手动加入监控的商品，MCP 才能查到数据 |
| **必须** | ③ 在扩展设置页获取 **MCP Key** | 详见下方[快速开始](#-快速开始) |
| **可选** | ④ 配置 AI 客户端 MCP | 接入后才能用自然语言对话查价 |

> 🔑 **MCP Key 从哪里获取？**
> MCP Key 在浏览器**扩展设置页**中展示。没有安装扩展 → 没有 Key → 无法使用 MCP 服务。登录官网不能获取 Key，Key 是扩展生成的。
>
> 官网的注册用于管理账号和 Pro 升级，MCP 的接入凭证在扩展内。

### 🤖 AI 对话的能力边界

盯价哨兵的 MCP 工具**只能查询你已经手动添加到监控列表的商品数据**，不能任意搜索 Shopee 全站商品。

| AI 能做的事 ✅ | AI 做不到的事 ❌ |
|---|---|
| 查看我的监控列表和价格 | 搜索 Shopee 上我没监控过的商品 |
| 查看已监控商品的价格历史和趋势 | 获取任意 ASIN/商品 ID 的价格 |
| 查看降价预警和推送记录 | 分析我没监控的竞品店铺 |
| 添加新商品到监控（需先在扩展扫码） | 自动发现新竞品 |
| 获取采集引擎运行状态 | 修改我的账号密码或设置 |

**简单说：插件帮你「录入」竞品，MCP 让 AI 帮你「分析和管理」已录入的竞品。**

能力边界详情请参阅 [**MCP 工具总览 →**](https://priceminder.online/docs/tools/overview)，完整工具列表和功能说明见下文。

---

## 📊 为什么选盯价哨兵？

**准实时，不是昨天数据。** 市面上同类 MCP 工具（如 Sorftime）返回的是 T-1（昨日缓存）数据。盯价哨兵每天爬取价格 **3 次**，让你在大促期间看到的是小时级的变动，而不是隔夜的老黄历。

| 能力 | 其他 MCP 工具 | 盯价哨兵 |
|---|---|---|
| **数据时效** | T-1（昨日数据） | **T-0（当天，每天 3 次）** |
| **价格变动检测** | 次日才能看到 | **4~8 小时内通知** |
| **大促期间（7.7/9.9/11.11）** | 错过当日多次调价 | **捕捉小时级变化** |
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
| 7 | `get_crawl_health` | 爬虫引擎运行状态 | 📊 洞察 |
| 8 | `get_monitor_overview` | 全局监控看板 | 📊 洞察 |

工具完整能力说明请参考：[**MCP 工具总览 →**](https://priceminder.online/docs/tools/overview)

---

## 🚀 快速开始

> **先装扩展 → 添加监控 → 获取 Key → 配置 AI 客户端**
>
> 完整的三步配置指南请参考官网：[**快速开始**](https://priceminder.online/docs/quick-start)（含产品架构图、配置截图和对话示例）

### 第 1 步：安装浏览器扩展

从以下渠道安装盯价哨兵扩展：

| 浏览器 | 安装方式 |
|---|---|
| **Chrome** | [Chrome 应用商店](https://chromewebstore.google.com) 搜索「Priceminder」 |
| **Edge** | [Edge 加载项](https://microsoftedge.microsoft.com/addons) 搜索「Priceminder」 |
| **360 浏览器** | 官网下载离线安装包 |
| **Opera** | Opera 加载项商店 |

安装步骤截图请参考：[**扩展安装指南 →**](https://priceminder.online/docs/extensions/)

### 第 2 步：添加商品到监控

打开任意 Shopee 商品详情页（支持 SG/MY/TH/ID/TW/PH/VN 站点），页面右上角会出现「**立即监测**」按钮：

1. 点击「立即监测」→ 商品加入监控列表
2. 系统自动开始按设定间隔采集价格
3. 可同时在扩展设置页配置采集频率和降价预警阈值

> 💡 **需要先有监控数据，AI 对话才能查到东西。** 建议一开始至少添加 5~10 个竞品商品，积累数据后再使用 MCP 对话。

### 第 3 步：获取 MCP Key

打开浏览器扩展的**设置页**，在「MCP 服务配置」区域查看你的 MCP Key。

> ⚠️ **注意：MCP Key 仅可在扩展设置页查看。** 登录官网无法获取，请确保扩展已安装。

### 第 4 步：配置 AI 客户端

**支持 HTTP 模式的客户端（推荐）：**

| 客户端 | 配置方式 | 文档链接 |
|---|---|---|
| Cherry Studio | 设置 → MCP 服务 → 添加 HTTP URL | [教程 →](https://priceminder.online/docs/clients/cherry-studio) |
| OpenClaw | config.yaml → mcp_servers → url | [教程 →](https://priceminder.online/docs/clients/openclaw) |
| Claude Desktop | claude_desktop_config.json → mcpServers | [教程 →](https://priceminder.online/docs/clients/claude-desktop) |
| Cursor | Cursor 设置 → MCP → 添加 HTTP URL | [教程 →](https://priceminder.online/docs/clients/cursor) |
| Cline | Cline MCP 配置 → 添加 | [教程 →](https://priceminder.online/docs/clients/cline) |
| Hermes Agent | config.yaml → mcp_servers | [教程 →](https://priceminder.online/docs/clients/hermes-agent) |

统一添加以下 URL（将 `***` 替换为你的 MCP Key）：

```json
{
  "mcpServers": {
    "sentinel": {
      "url": "https://priceminder.online/mcp_server?key=***"
    }
  }
}
```

各客户端详细配置步骤（含截图）请参考：[**客户端接入教程 →**](https://priceminder.online/docs/clients/)

### 第 5 步：验证连接

配置完成后，在 AI 客户端中问以下问题测试：

| 你的提问 | AI 调用的工具 | 预期结果 |
|---|---|---|
| 「我的监控列表」 | `get_monitor_list` | 返回你已监控的商品列表 |
| 「竞品最近价格怎么样」 | `get_price_summary` | 价格摘要（当前/基准/最高/最低/均价） |
| 「有没有新的降价预警」 | `get_alerts` | 未读的降价预警记录 |
| 「采集系统运行正常吗」 | `get_crawl_health` | 采集引擎运行状态 |

> ✅ 如果 AI 正确返回了你的监控数据，说明接入成功。
>
> ❌ 如果返回空数据，请确认你已在扩展中添加了至少一个监控商品。

更多对话示例请参考：[**场景与最佳实践 →**](https://priceminder.online/docs/scenarios)

---

## 💬 实战场景 Prompt

以下 **3 个场景** 展示盯价哨兵在真实运营中的威力——每条指令都可以直接对 Claude 说：

### 📍 场景一：盯死竞品店铺

> *"监控 Shopee 新加坡站 'ABC Official Store' 的所有商品。如果任何商品在最近 24 小时内降价超过 5%，给我汇总所有变动。"*

AI 助手将：
1. 检查当前监控列表中该店铺的商品
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

---

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────┐
│                  AI 客户端                            │
│  (Claude Desktop / Cursor / Cherry Studio / Hermes)  │
└──────────────┬──────────────────────────────────────┘
               │  MCP 协议 (stdio 或 HTTP/SSE)
               ▼
┌──────────────────────────────────────┐
│     盯价哨兵 MCP Server              │
│  ┌────────────────────────────────┐  │
│  │  工具注册（8 个工具）          │  │
│  │  - get_monitor_list           │  │
│  │  - get_price_summary          │  │
│  │  - get_price_history          │  │
│  │  - get_alerts                 │  │
│  │  - add_monitor                │  │
│  │  - get_crawl_health           │  │
│  │  - get_monitor_overview       │  │
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

产品架构流程图和详细说明请参考官网：[**产品架构总览 →**](https://priceminder.online/docs/quick-start)

### 数据流说明

```
① 浏览器扩展采集数据
      │
      ▼
② 后端 API 存储 → PostgreSQL
      │
      ▼
③ MCP Server 通过 API 读取
      │
      ▼
④ AI 客户端通过 MCP 协议查询
```

**关键点：** 数据流向是单向的——扩展采集 → 后端存储 → MCP 读取。AI 客户端不能绕过扩展直接写入数据。

---

## 🔧 配置参数

### 环境变量

| 变量 | 说明 | 默认值 |
|---|---|---|
| `SENTINEL_API_BASE` | 后端 API 地址 | `https://priceminder.online/shopee` |
| `SENTINEL_TOKEN` | 你的认证令牌 | **（必填）** |
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
- **官方文档**：[priceminder.online/docs](https://priceminder.online/docs/)
- **快速开始**：[priceminder.online/docs/quick-start](https://priceminder.online/docs/quick-start)
- **MCP 工具总览**：[priceminder.online/docs/tools/overview](https://priceminder.online/docs/tools/overview)
- **GitHub**：[github.com/haidrau/sentinel-mcp-server](https://github.com/haidrau/sentinel-mcp-server)
- **Gitee**：[gitee.com/haidrau/sentinel-mcp-server](https://gitee.com/haidrau/sentinel-mcp-server)