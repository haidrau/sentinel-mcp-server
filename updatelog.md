# 更新日志

## 2026-07-06 — README 大改版 + 一键部署脚本 + n8n 模板

### 改动概述

围绕差异化定位和推广，进行了 4 项关键更新：

1. **README 重写（英文/中文同步）**
   - 新增「为什么选盯价哨兵？」对比表格，直接指出 T-1（昨日数据）vs T-0（当天 3× 爬取）的时效差异
   - 点名对标 Sorftime 等 MCP 工具（中文版明确点名，英文版隐性对比）
   - 突出推送能力（飞书/钉钉/Telegram）vs 竞品仅查询的差异

2. **一键部署脚本 `docker-run.sh`**
   - `bash docker-run.sh YOUR_TOKEN` 一行搞定：拉镜像→起容器→健康检查→输出配置
   - 支持自动重试 ghcr.io 拉取失败时本地构建

3. **3 个实战场景 Prompt**
   - 场景一：盯死竞品店铺（降价 5% 告警）
   - 场景二：大促实时盯盘（每 4 小时检查 + 3% 变动筛选）
   - 场景三：降价情报挖掘（降幅排行 + 历史深挖）

4. **n8n 工作流模板 `priceminder-mcp-n8n.json`**
   - 开箱即用：定时触发 → 获取价格 → 解析降价 → Telegram/邮件推送
   - 同步推送到 GitHub open-src branch → master

### 涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `README.md` | ✏️ 重写 | 英文版，增 60 行→增 506 行，含对比/场景/n8n |
| `README.zh-CN.md` | ✏️ 重写 | 中文版同步，直接点名 Sorftime T-1 劣势 |
| `docker-run.sh` | 🆕 新增 | 一键 Docker 部署脚本 |
| `priceminder-mcp-n8n.json` | 🆕 新增 | n8n 工作流模板，4h 自动盯价 + 推送 |

## 2026-07-04 — Free/Pro Tier 透传

### 改动概述

MCP Server 从后端 `/mcp/verify-key` 响应中读取 `tier` 字段并缓存，透传给后续 API 调用。
具体的限流逻辑在后端 API 层执行（监控上限、天数上限），MCP Server 仅做字段透传。

### 涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/sentinel_mcp/auth.py` | ✏️ 修改 | `verify_key()` 缓存的 info 增加 `tier` 字段 |