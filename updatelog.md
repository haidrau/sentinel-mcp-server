# 更新日志

## 2026-07-04 — Free/Pro Tier 透传

### 改动概述

MCP Server 从后端 `/mcp/verify-key` 响应中读取 `tier` 字段并缓存，透传给后续 API 调用。
具体的限流逻辑在后端 API 层执行（监控上限、天数上限），MCP Server 仅做字段透传。

### 涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/sentinel_mcp/auth.py` | ✏️ 修改 | `verify_key()` 缓存的 info 增加 `tier` 字段 |