"""环境变量配置 — 支持 stdio 和 HTTP 两种运行模式"""

import os

# Sentinel REST API base URL（nginx 将 /shopee 代理到后端 /api/v1）
API_BASE: str = os.environ.get(
    "SENTINEL_API_BASE",
    "https://priceminder.online/shopee",
)

# 用户认证 Token（stdio 模式下从环境变量获取；HTTP 模式下由 auth 中间件注入）
TOKEN: str = os.environ.get("SENTINEL_TOKEN", "")

# HTTP 请求超时 (秒)
TIMEOUT: int = int(os.environ.get("SENTINEL_TIMEOUT", "30"))

# ── HTTP 模式专用配置 ──────────────────────────────────
# 运行模式: "stdio" | "http"
MODE: str = os.environ.get("MCP_MODE", "stdio")

# HTTP 服务监听地址和端口
HOST: str = os.environ.get("MCP_HOST", "127.0.0.1")
PORT: int = int(os.environ.get("MCP_PORT", "8020"))

# MCP Server 与后端 API 通信的内部密钥（用于调用 /mcp/verify-key 和 /mcp/log-usage）
MCP_INTERNAL_KEY: str = os.environ.get(
    "SENTINEL_MCP_INTERNAL_KEY",
    "sentinel-mcp-internal-2026",
)

# 后端 API Key（验证 X-Api-Key，与 settings.api_key 对应）
API_KEY: str = os.environ.get("SENTINEL_API_KEY", "sentinel-mvp-2026")

# 日志级别
LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
