# Hermes Agent 实测 Sentinel MCP 指南

> 日期：2026-06-22 | 目标：在 Hermes Agent 中跑通 Sentinel MCP 的 10 个 Tool

---

## 一、前置条件

| 项目 | 要求 |
|------|------|
| Python | ≥ 3.11（推荐 3.12） |
| pip / uv | 已安装 |
| Sentinel API | 帆帆已部署最新 API 改动 |
| Token | 有效的 `X-Sentinel-Token`（如 `9df2b0b5-f720-40f5-9f44-618dc68e093f`） |

---

## 二、安装 Hermes Agent

### Windows（推荐 pip）

```bash
pip install hermes-agent
hermes postinstall
```

`hermes postinstall` 会引导你配置模型 API Key。选一个国内可用的模型即可，比如：

- Kimi (Moonshot): `moonshot/kimi-latest`, base_url `https://api.moonshot.cn/v1`
- 通义千问: `dashscope/qwen-max`, base_url `https://dashscope.aliyuncs.com/compatible-mode/v1`
- DeepSeek: `deepseek/deepseek-chat`, base_url `https://api.deepseek.com/v1`

### 验证安装

```bash
hermes doctor        # 检查环境是否 OK
hermes -i            # 进入交互模式，确认能正常对话
```

---

## 三、安装 Sentinel MCP Server

```bash
# 方式 1: 从 Gitee 源码安装（推荐开发阶段）
cd E:\99--Code\0-QoderWork\sentinel-mcp-server
pip install -e .

# 方式 2: 如果已发布到 PyPI
pip install sentinel-mcp-server
```

验证安装：

```bash
python -c "from sentinel_mcp.server import TOOLS; print(f'{len(TOOLS)} tools loaded')"
# 应输出: 10 tools loaded
```

---

## 四、配置 Hermes 接入 Sentinel MCP

### 4.1 编辑 Hermes 配置文件

配置文件路径：`~/.hermes/config.yaml`（Windows 上是 `C:\Users\{你的用户名}\.hermes\config.yaml`）

在 `mcp_servers` 节点下添加 Sentinel MCP Server：

```yaml
# ~/.hermes/config.yaml

# ... 其他配置 ...

mcp_servers:
  # 已有的 MCP servers...

  # 新增：Shopee 盯价哨兵
  sentinel:
    command: python
    args: ["-m", "sentinel_mcp.server"]
    env:
      SENTINEL_API_BASE: "https://priceminder.online/api/v1"
      SENTINEL_TOKEN: "你的token"
    enabled: true
```

**关键说明**：

| 字段 | 说明 |
|------|------|
| `command` | 用 `python` 而不是 `uvx`，因为我们是用 pip install -e 安装的 |
| `args` | `["-m", "sentinel_mcp.server"]` — 以模块方式启动 |
| `SENTINEL_API_BASE` | 帆帆部署的 API 地址 |
| `SENTINEL_TOKEN` | 你的用户 Token |
| `enabled` | 设为 `true` 启用 |

### 4.2 如果使用 uvx 方式（不需要 pip install）

```yaml
mcp_servers:
  sentinel:
    command: uvx
    args: ["sentinel-mcp-server"]
    env:
      SENTINEL_API_BASE: "https://priceminder.online/api/v1"
      SENTINEL_TOKEN: "你的token"
    enabled: true
```

这种方式需要先安装 uv：`pip install uv`

### 4.3 重载配置

在 Hermes 交互界面中输入：

```
/reload-mcp
```

或者直接重启 Hermes：

```bash
hermes -i
```

---

## 五、验证 MCP 加载

### 5.1 检查工具列表

在 Hermes 交互界面中输入：

```
/tools
```

你应该能看到 10 个 `mcp__sentinel__` 前缀的工具：

```
mcp__sentinel__get_monitor_list
mcp__sentinel__get_price_summary
mcp__sentinel__get_price_history
mcp__sentinel__get_alerts
mcp__sentinel__add_monitor
mcp__sentinel__update_monitor_status
mcp__sentinel__mark_alert_read
mcp__sentinel__get_crawl_health
mcp__sentinel__get_monitor_overview
mcp__sentinel__search_my_products
```

### 5.2 命令行检查

```bash
hermes mcp list
```

如果 Sentinel MCP Server 没有出现在列表中，排查：

1. 检查 Python 路径是否在 PATH 中：`where python`
2. 检查包是否安装成功：`pip show sentinel-mcp-server`
3. 手动启动测试：`set SENTINEL_TOKEN=xxx && python -m sentinel_mcp.server`
4. 查看 Hermes 日志：`~/.hermes/logs/` 目录

---

## 六、实测对话（按顺序执行）

确认工具加载成功后，按以下顺序在 Hermes 中发起对话：

### 测试 1：查看监控列表

```
你：我在盯哪些商品
```

**预期**：Hermes 调用 `get_monitor_list`，返回你的监控商品列表。

---

### 测试 2：价格摘要

```
你：竞品最近价格怎么样
```

**预期**：Hermes 调用 `get_price_summary`（批量模式），返回所有活跃监控的价格摘要。

---

### 测试 3：价格历史

```
你：给我看看最近的价格走势
```

**预期**：Hermes 先调用 `get_monitor_list` 获取 ID，再调用 `get_price_history`，返回 Markdown 表格。

---

### 测试 4：预警查询

```
你：有没有新的降价预警
```

**预期**：Hermes 调用 `get_alerts(unread_only=true)`，返回未读预警列表。

---

### 测试 5：添加监控

```
你：帮我监控这个 Shopee 商品 https://shopee.sg/product/12345
```

**预期**：Hermes 调用 `add_monitor`，返回确认信息（ID、站点、阈值）。

---

### 测试 6：暂停/恢复

```
你：先暂停第一个监控
```

**预期**：Hermes 调用 `update_monitor_status(status="paused")`，返回确认。

---

### 测试 7：标记已读

```
你：把第一条预警标记已读
```

**预期**：Hermes 调用 `mark_alert_read`，返回确认。

---

### 测试 8：采集健康度

```
你：采集系统运行正常吗
```

**预期**：Hermes 调用 `get_crawl_health`，返回健康报告。

---

### 测试 9：监控大盘

```
你：给我一个监控总览
```

**预期**：Hermes 调用 `get_monitor_overview`，返回大盘数据。

---

### 测试 10：搜索

```
你：搜一下我监控里有没有 iPhone
```

**预期**：Hermes 调用 `search_my_products(keyword="iPhone")`，返回匹配结果。

---

## 七、排错速查

| 问题 | 原因 | 解决 |
|------|------|------|
| `/tools` 看不到 sentinel 工具 | MCP Server 未加载 | 检查 config.yaml 的 `mcp_servers` 配置，执行 `/reload-mcp` |
| 工具返回 "SENTINEL_TOKEN 未设置" | env 没传进去 | 确认 `env.SENTINEL_TOKEN` 写对了，不带引号空格 |
| 工具返回 401 Unauthorized | Token 无效 | 换一个有效的 Token |
| 工具返回 500 | API 端未部署 | 确认帆帆已部署最新 API 改动 |
| `command not found: python` | Python 不在 PATH | 用完整路径如 `C:\Python313\python.exe` |
| `ModuleNotFoundError: sentinel_mcp` | 包没装 | 重新 `pip install -e .` |
| Hermes 启动卡住 | MCP Server 启动超时 | 手动 `python -m sentinel_mcp.server` 测试能否启动 |

---

## 八、进阶：工具过滤

如果 10 个工具太多，可以在 config.yaml 中只启用部分：

```yaml
mcp_servers:
  sentinel:
    command: python
    args: ["-m", "sentinel_mcp.server"]
    env:
      SENTINEL_API_BASE: "https://priceminder.online/api/v1"
      SENTINEL_TOKEN: "你的token"
    enabled: true
    # 只暴露查询类工具，隐藏操作类
    allow:
      - get_monitor_list
      - get_price_summary
      - get_price_history
      - get_alerts
      - get_monitor_overview
```
