"""监控管理相关 Tools (4 个)

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
获取用户正在监控的商品列表。

用户可能的问法：
- "我在盯哪些商品"
- "SG 站有几个商品在监控"
- "我的监控列表"
- "暂停中的监控有几个"

返回监控项数组，每项包含商品名、店铺、站点、基准价、当前价、变动幅度、状态等。
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
添加一个新的商品到监控列表。用户需要提供一个 Shopee 商品 URL。

用户可能的问法：
- "帮我监控这个商品 https://shopee.sg/..."
- "把这个加到监控列表"
- "我想盯一下这个竞品的价格"

需要提供 product_url（必填）。可选指定 alert_threshold（降价阈值百分比，默认 5）。
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
暂停或恢复某个监控项。

用户可能的问法：
- "先暂停 iPhone 那个监控"
- "恢复 Samsung 的监控"
- "把 AirPods 的监控停掉"

需要提供 monitor_id（监控项 ID）和 status（"paused" 暂停 / "active" 恢复）。
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
在用户的监控列表中按关键词搜索商品（匹配商品名或店铺名）。

用户可能的问法：
- "搜一下我监控里有没有 AirPods"
- "Samsung 相关的商品有几个在监控"
- "那个卖耳机的店铺叫什么来着"

需要提供 keyword（搜索关键词）。
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
