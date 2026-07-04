"""Monitor management Tools (4)

- get_monitor_list
- add_monitor
- update_monitor_status
- search_my_products
"""

from __future__ import annotations

import json

from sentinel_mcp import api_client


# ──────────────────────────────────────────────
# Tool 1: get_monitor_list
# ──────────────────────────────────────────────

MONITOR_LIST_DESCRIPTION = """\
Get the list of products the user is currently monitoring.

Example user queries:
- "What products am I tracking?"
- "How many items on SG site?"
- "Show my monitor list"
- "How many paused monitors?"

Returns an array of monitor items with product name, shop, site, base price,
current price, change percentage, and status.
"""


async def get_monitor_list(site: str | None = None, status: str | None = None) -> str:
    """获取监控列表"""
    params: dict = {"size": 100}
    if site:
        params["site"] = site
    if status:
        params["status"] = status

    data = await api_client.get("/monitors", params=params)
    items = data.get("items", [])
    total = data.get("total", len(items))

    if not items:
        return f"当前没有监控项{f'（站点: {site}）' if site else ''}。"

    lines = [f"共 {total} 个监控项：\n"]
    for m in items:
        price_info = ""
        if m.get("current_price") is not None:
            price_info = f"，当前价 {m['currency']} {m['current_price']}"
            if m.get("change_pct") is not None:
                direction = "↓" if m["change_pct"] < 0 else "↑" if m["change_pct"] > 0 else "→"
                price_info += f"（{direction}{abs(m['change_pct'])}%）"
        else:
            price_info = "（尚未采集到价格）"

        status_label = "⏸ 已暂停" if m["status"] == "paused" else "🟢 监控中"
        lines.append(
            f"- [{m['id']}] {m['product_name']} | {m['shop_name']} | "
            f"{m['site'].upper()} | 基准价 {m['currency']} {m['base_price']}"
            f"{price_info} | {status_label}"
        )

    return "\n".join(lines)


# ──────────────────────────────────────────────
# Tool 5: add_monitor
# ──────────────────────────────────────────────

ADD_MONITOR_DESCRIPTION = """\
Add a new product to the monitor list. The user provides a Shopee product URL.

Example user queries:
- "Track this product https://shopee.sg/..."
- "Add this to my monitor list"
- "I want to watch this competitor's price"

Requires product_url (required). Optional alert_threshold (price drop %, default 5).
"""


async def add_monitor(product_url: str, alert_threshold: int = 5) -> str:
    """添加监控"""
    body = {
        "product_url": product_url,
        "product_name": "",  # 由爬虫首次采集时填充
        "shop_name": "",
        "product_id": "",
        "shop_url": "",
        "site": _extract_site(product_url),
        "currency": _site_currency(product_url),
        "base_price": 0,
        "alert_threshold": alert_threshold,
    }

    try:
        data = await api_client.post("/monitors", json_body=body)
    except api_client.SentinelAPIError as e:
        if e.code == 40901:
            return f"该商品已在监控列表中（monitor_id={data.get('existing_monitor_id', '?')}），无需重复添加。"
        raise

    mid = data.get("id", "?")
    return (
        f"已添加监控（ID: {mid}）。\n"
        f"- URL: {product_url}\n"
        f"- 站点: {_extract_site(product_url).upper()}\n"
        f"- 降价阈值: {alert_threshold}%\n\n"
        f"系统已开始自动采集价格。当竞品降价超过 {alert_threshold}% 时，会通过飞书推送预警。"
    )


# ──────────────────────────────────────────────
# Tool 6: update_monitor_status
# ──────────────────────────────────────────────

UPDATE_STATUS_DESCRIPTION = """\
Pause or resume a monitored product.

Example user queries:
- "Pause the iPhone monitor"
- "Resume monitoring Samsung"
- "Stop tracking AirPods"

Requires monitor_id and status ("paused" | "active").
"""


async def update_monitor_status(monitor_id: int, status: str) -> str:
    """暂停或恢复监控"""
    if status not in ("active", "paused"):
        return f"status 必须是 'active'（恢复）或 'paused'（暂停），当前值 '{status}' 无效。"

    data = await api_client.put(f"/monitors/{monitor_id}", json_body={"status": status})
    name = data.get("product_name", f"Monitor #{monitor_id}")
    if status == "paused":
        return f"已暂停监控：{name}（ID: {monitor_id}）。系统不再采集该商品的价格。如需恢复，告诉我即可。"
    else:
        return f"已恢复监控：{name}（ID: {monitor_id}）。系统将继续采集该商品的价格。"


# ──────────────────────────────────────────────
# Tool 10: search_my_products
# ──────────────────────────────────────────────

SEARCH_PRODUCTS_DESCRIPTION = """\
Search the user's monitor list by keyword (matches product name or shop name).

Example user queries:
- "Search for AirPods in my monitors"
- "How many Samsung products am I tracking?"
- "What's the name of that earphone shop?"

Requires keyword (search term).
"""


async def search_my_products(keyword: str) -> str:
    """在监控列表中搜索"""
    # 使用后端 keyword 搜索
    data = await api_client.get("/monitors", params={"keyword": keyword, "size": 100})
    items = data.get("items", [])
    total = data.get("total", len(items))

    if not items:
        return f"未找到包含 \"{keyword}\" 的监控商品。"

    lines = [f"搜索 \"{keyword}\" 找到 {len(items)} 个匹配：\n"]
    for m in items:
        price_info = ""
        if m.get("current_price") is not None:
            price_info = f"，当前价 {m['currency']} {m['current_price']}"
        status_label = "⏸ 已暂停" if m["status"] == "paused" else "🟢 监控中"
        lines.append(
            f"- [{m['id']}] {m['product_name']} | {m['shop_name']} | "
            f"{m['site'].upper()}{price_info} | {status_label}"
        )
    return "\n".join(lines)


# ── helpers ──────────────────────────────────

def _extract_site(url: str) -> str:
    """从 Shopee URL 中提取站点代码"""
    url_lower = url.lower()
    for site in ("shopee.sg", "shopee.com.my", "shopee.co.th", "shopee.vn"):
        if site in url_lower:
            mapping = {
                "shopee.sg": "sg",
                "shopee.com.my": "my",
                "shopee.co.th": "th",
                "shopee.vn": "vn",
            }
            return mapping[site]
    return "sg"  # 默认


def _site_currency(url: str) -> str:
    """根据站点返回默认货币"""
    site = _extract_site(url)
    return {"sg": "SGD", "my": "MYR", "th": "THB", "vn": "VND"}.get(site, "SGD")
