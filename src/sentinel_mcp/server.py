"""
Shopee 运营哨兵 MCP Server

将 Sentinel REST API 封装为 MCP (Model Context Protocol) Tools，
让 AI Agent 通过自然语言调用价格监控能力。

支持两种运行模式：
  - stdio 模式：本地安装，通过标准输入/输出与 AI 客户端通信
  - http  模式：托管部署，暴露 Streamable HTTP 端点，用户通过 URL+Key 接入

10 个 Tool:
  Tier 1 (查询): get_monitor_list, get_price_summary, get_price_history, get_alerts
  Tier 2 (操作): add_monitor, update_monitor_status, mark_alert_read
  Tier 3 (洞察): get_crawl_health, get_monitor_overview, search_my_products
"""

from __future__ import annotations

import argparse
import asyncio
import contextvars
import logging
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from sentinel_mcp import config
from sentinel_mcp.tools import monitors, prices, alerts, insights

# ── 日志 ──────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("sentinel-mcp")

# ── 请求级上下文：当前正在执行的 Tool 名称（供 api_client 上报日志） ──
_current_tool_name: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_tool_name", default=""
)

app = Server("sentinel-mcp-server")


# ──────────────────────────────────────────────────────────
# Tool 注册表
# ──────────────────────────────────────────────────────────

TOOLS: list[Tool] = [
    # Tier 1 — 查询
    Tool(
        name="get_monitor_list",
        description=monitors.MONITOR_LIST_DESCRIPTION,
        inputSchema={
            "type": "object",
            "properties": {
                "site": {
                    "type": "string",
                    "description": "站点筛选，可选值：sg, my, th, vn。不传则返回全部站点",
                    "enum": ["sg", "my", "th", "vn"],
                },
                "status": {
                    "type": "string",
                    "description": "状态筛选，默认 active",
                    "enum": ["active", "paused"],
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="get_price_summary",
        description=prices.PRICE_SUMMARY_DESCRIPTION,
        inputSchema={
            "type": "object",
            "properties": {
                "monitor_id": {
                    "type": "integer",
                    "description": "监控项 ID。不传则返回所有活跃监控的摘要",
                },
                "site": {
                    "type": "string",
                    "description": "站点筛选（当 monitor_id 不传时生效）",
                    "enum": ["sg", "my", "th", "vn"],
                },
                "days": {
                    "type": "integer",
                    "description": "查询最近 N 天的数据",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 30,
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="get_price_history",
        description=prices.PRICE_HISTORY_DESCRIPTION,
        inputSchema={
            "type": "object",
            "properties": {
                "monitor_id": {
                    "type": "integer",
                    "description": "监控项 ID（必填）",
                },
                "days": {
                    "type": "integer",
                    "description": "查询最近 N 天的数据",
                    "default": 7,
                    "minimum": 1,
                    "maximum": 90,
                },
            },
            "required": ["monitor_id"],
        },
    ),
    Tool(
        name="get_alerts",
        description=alerts.GET_ALERTS_DESCRIPTION,
        inputSchema={
            "type": "object",
            "properties": {
                "unread_only": {
                    "type": "boolean",
                    "description": "只返回未读预警",
                    "default": False,
                },
                "site": {
                    "type": "string",
                    "description": "站点筛选",
                    "enum": ["sg", "my", "th", "vn"],
                },
                "limit": {
                    "type": "integer",
                    "description": "返回条数上限",
                    "default": 10,
                    "maximum": 50,
                },
            },
            "required": [],
        },
    ),

    # Tier 2 — 操作
    Tool(
        name="add_monitor",
        description=monitors.ADD_MONITOR_DESCRIPTION,
        inputSchema={
            "type": "object",
            "properties": {
                "product_url": {
                    "type": "string",
                    "description": "Shopee 商品页面 URL（必填）",
                },
                "alert_threshold": {
                    "type": "integer",
                    "description": "降价预警阈值（百分比），默认 5",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 50,
                },
            },
            "required": ["product_url"],
        },
    ),
    Tool(
        name="update_monitor_status",
        description=monitors.UPDATE_STATUS_DESCRIPTION,
        inputSchema={
            "type": "object",
            "properties": {
                "monitor_id": {
                    "type": "integer",
                    "description": "监控项 ID（必填）",
                },
                "status": {
                    "type": "string",
                    "description": "目标状态：'paused'（暂停）或 'active'（恢复）",
                    "enum": ["active", "paused"],
                },
            },
            "required": ["monitor_id", "status"],
        },
    ),
    Tool(
        name="mark_alert_read",
        description=alerts.MARK_READ_DESCRIPTION,
        inputSchema={
            "type": "object",
            "properties": {
                "alert_id": {
                    "type": "integer",
                    "description": "预警记录 ID（必填）",
                },
            },
            "required": ["alert_id"],
        },
    ),

    # Tier 3 — 洞察
    Tool(
        name="get_crawl_health",
        description=insights.CRAWL_HEALTH_DESCRIPTION,
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="get_monitor_overview",
        description=insights.MONITOR_OVERVIEW_DESCRIPTION,
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="search_my_products",
        description=monitors.SEARCH_PRODUCTS_DESCRIPTION,
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词，匹配商品名或店铺名（必填）",
                },
            },
            "required": ["keyword"],
        },
    ),
]

# Tool name → handler 映射
_HANDLERS = {
    "get_monitor_list": monitors.get_monitor_list,
    "get_price_summary": prices.get_price_summary,
    "get_price_history": prices.get_price_history,
    "get_alerts": alerts.get_alerts,
    "add_monitor": monitors.add_monitor,
    "update_monitor_status": monitors.update_monitor_status,
    "mark_alert_read": alerts.mark_alert_read,
    "get_crawl_health": insights.get_crawl_health,
    "get_monitor_overview": insights.get_monitor_overview,
    "search_my_products": monitors.search_my_products,
}


# ──────────────────────────────────────────────────────────
# MCP Server Handlers
# ──────────────────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = _HANDLERS.get(name)
    if not handler:
        return [TextContent(type="text", text=f"未知工具: {name}")]

    # stdio 模式下检查 TOKEN（HTTP 模式由 auth 中间件保证）
    if config.MODE == "stdio" and not config.TOKEN:
        return [TextContent(
            type="text",
            text="错误: SENTINEL_TOKEN 环境变量未设置。请在 MCP 配置中设置你的 API Token。",
        )]

    # 设置当前 tool 名称（供 api_client 上报日志）
    _current_tool_name.set(name)

    try:
        result = await handler(**arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        logger.exception(f"Tool {name} 调用失败")
        return [TextContent(type="text", text=f"调用 {name} 时出错: {e}")]


# ──────────────────────────────────────────────────────────
# 启动模式
# ──────────────────────────────────────────────────────────

def run_stdio():
    """以 stdio 模式启动 MCP Server（本地安装模式）"""
    logger.info("Sentinel MCP Server 启动 [stdio 模式] (API: %s)", config.API_BASE)
    if not config.TOKEN:
        logger.warning("SENTINEL_TOKEN 未设置，Tool 调用将返回错误提示")

    async def _run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    asyncio.run(_run())


def run_http():
    """以 Streamable HTTP 模式启动 MCP Server（托管部署模式）"""
    import uvicorn
    from sentinel_mcp.auth import AuthMiddleware

    logger.info(
        "Sentinel MCP Server 启动 [HTTP 模式] (API: %s, Listen: %s:%d)",
        config.API_BASE, config.HOST, config.PORT,
    )

    # 使用 MCP SDK 内置的 Streamable HTTP ASGI app
    mcp_asgi_app = app.streamable_http_app()

    # 包裹认证中间件
    wrapped_app = AuthMiddleware(mcp_asgi_app)

    uvicorn.run(
        wrapped_app,
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower(),
    )


def main():
    """入口函数：根据命令行参数或环境变量选择运行模式"""
    parser = argparse.ArgumentParser(description="Shopee 运营哨兵 MCP Server")
    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default=config.MODE,
        help="运行模式：stdio（本地）或 http（托管）。默认从 SENTINEL_MCP_MODE 环境变量读取。",
    )
    args = parser.parse_args()

    if args.mode == "http":
        run_http()
    else:
        run_stdio()


if __name__ == "__main__":
    main()
