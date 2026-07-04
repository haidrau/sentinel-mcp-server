"""
Shopee 盯价哨兵 MCP Server

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


# ──────────────────────────────────────────────────────────
# MCP Server (FastMCP)
# ──────────────────────────────────────────────────────────
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import TransportSecuritySettings

# 关闭 DNS 重绑定保护：MCP Server 在 nginx 反代后面，
# Host 头为 priceminder.online，默认保护会拒绝非 localhost 请求 (421)
mcp = FastMCP(
    "sentinel-mcp-server",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


# ── Tool 注册 ─────────────────────────────────────────────


@mcp.tool(
    name="get_monitor_list",
    description=monitors.MONITOR_LIST_DESCRIPTION,
)
async def get_monitor_list(
    site: str | None = None,
    status: str = "active",
) -> str:
    """获取监控列表"""
    return await monitors.get_monitor_list(site=site, status=status)


@mcp.tool(
    name="get_price_summary",
    description=prices.PRICE_SUMMARY_DESCRIPTION,
)
async def get_price_summary(
    monitor_id: int | None = None,
    site: str | None = None,
    days: int = 3,
) -> str:
    """价格摘要（支持批量）"""
    kwargs = {"days": days}
    if monitor_id is not None:
        kwargs["monitor_id"] = monitor_id
    if site is not None:
        kwargs["site"] = site
    return await prices.get_price_summary(**kwargs)


@mcp.tool(
    name="get_price_history",
    description=prices.PRICE_HISTORY_DESCRIPTION,
)
async def get_price_history(
    monitor_id: int,
    days: int = 7,
) -> str:
    """价格时间序列"""
    return await prices.get_price_history(monitor_id=monitor_id, days=days)


@mcp.tool(
    name="get_alerts",
    description=alerts.GET_ALERTS_DESCRIPTION,
)
async def get_alerts(
    unread_only: bool = False,
    site: str | None = None,
    limit: int = 10,
) -> str:
    """预警列表"""
    kwargs = {"limit": limit, "unread_only": unread_only}
    if site is not None:
        kwargs["site"] = site
    return await alerts.get_alerts(**kwargs)


@mcp.tool(
    name="add_monitor",
    description=monitors.ADD_MONITOR_DESCRIPTION,
)
async def add_monitor(
    product_url: str,
    product_name: str = "",
    shop_name: str = "",
    site: str = "",
    currency: str = "",
    base_price: float | None = None,
    check_interval: int = 120,
    alert_threshold: int = 5,
) -> str:
    """添加监控"""
    return await monitors.add_monitor(
        product_url=product_url,
        product_name=product_name,
        shop_name=shop_name,
        site=site,
        currency=currency,
        base_price=base_price,
        check_interval=check_interval,
        alert_threshold=alert_threshold,
    )


@mcp.tool(
    name="update_monitor_status",
    description=monitors.UPDATE_STATUS_DESCRIPTION,
)
async def update_monitor_status(
    monitor_id: int,
    status: str,
) -> str:
    """暂停/恢复监控"""
    return await monitors.update_monitor_status(
        monitor_id=monitor_id, status=status
    )


@mcp.tool(
    name="mark_alert_read",
    description=alerts.MARK_READ_DESCRIPTION,
)
async def mark_alert_read(
    alert_id: int,
) -> str:
    """标记预警已读"""
    return await alerts.mark_alert_read(alert_id=alert_id)


@mcp.tool(
    name="get_crawl_health",
    description=insights.CRAWL_HEALTH_DESCRIPTION,
)
async def get_crawl_health() -> str:
    """采集健康度"""
    return await insights.get_crawl_health()


@mcp.tool(
    name="get_monitor_overview",
    description=insights.MONITOR_OVERVIEW_DESCRIPTION,
)
async def get_monitor_overview() -> str:
    """监控大盘"""
    return await insights.get_monitor_overview()


@mcp.tool(
    name="search_my_products",
    description=monitors.SEARCH_PRODUCTS_DESCRIPTION,
)
async def search_my_products(
    keyword: str,
) -> str:
    """搜索监控"""
    return await monitors.search_my_products(keyword=keyword)


# ── 上下文钩子：在每次 Tool 调用时设置当前 tool 名称 ──


@mcp.tool()
async def _tool_context_hook():
    """内部使用：运行时上下文"""
    pass


# ──────────────────────────────────────────────────────────
# 启动模式
# ──────────────────────────────────────────────────────────


def run_stdio():
    """以 stdio 模式启动 MCP Server（本地安装模式）"""
    logger.info("Sentinel MCP Server 启动 [stdio 模式] (API: %s)", config.API_BASE)
    if not config.TOKEN:
        logger.warning("SENTINEL_TOKEN 未设置，Tool 调用将返回错误提示")

    # FastMCP 的 run() 支持 stdio 传输
    mcp.run(transport="stdio")


def run_http():
    """以 Streamable HTTP 模式启动 MCP Server（托管部署模式）"""
    from sentinel_mcp.auth import AuthMiddleware

    logger.info(
        "Sentinel MCP Server 启动 [HTTP 模式] (API: %s, Listen: %s:%d)",
        config.API_BASE, config.HOST, config.PORT,
    )

    # FastMCP streamable_http_app() → ASGI Starlette app，端点默认 /mcp
    # AuthMiddleware 会将客户端请求的 / 改写为 /mcp
    mcp_asgi_app = mcp.streamable_http_app()

    # 包裹认证中间件
    wrapped_app = AuthMiddleware(mcp_asgi_app)

    import uvicorn
    uvicorn.run(
        wrapped_app,
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower(),
    )


def main():
    """入口函数：根据命令行参数或环境变量选择运行模式"""
    parser = argparse.ArgumentParser(description="Shopee 盯价哨兵 MCP Server")
    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default=config.MODE,
        help="运行模式：stdio（本地）或 http（托管）。默认从 MCP_MODE 环境变量读取。",
    )
    args = parser.parse_args()

    if args.mode == "http":
        run_http()
    else:
        run_stdio()


if __name__ == "__main__":
    main()
