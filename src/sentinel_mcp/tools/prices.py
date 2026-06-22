"""价格数据相关 Tools (2 个)

- get_price_summary
- get_price_history
"""

from __future__ import annotations

from sentinel_mcp import api_client


# ──────────────────────────────────────────────
# Tool 2: get_price_summary
# ──────────────────────────────────────────────

PRICE_SUMMARY_DESCRIPTION = """\
获取指定商品或所有活跃监控商品的价格摘要，包括当前价、基准价、最高/最低/均价、趋势方向。

用户可能的问法：
- "竞品最近价格怎么样"
- "SG 站上盯的几个商品近 2 天价格怎样"
- "有没有降价的竞品"

如果不指定 monitor_id，返回所有活跃监控的摘要。可选指定 site（站点）和 days（天数，默认 3）。
"""


async def get_price_summary(
    monitor_id: int | None = None,
    site: str | None = None,
    days: int = 3,
) -> str:
    """获取价格摘要"""
    if monitor_id:
        # 单商品模式
        data = await api_client.get(
            "/price/summary",
            params={"monitor_id": monitor_id, "days": days},
        )
        return _format_single_summary(data)

    # 批量模式：获取所有活跃监控的摘要
    data = await api_client.get(
        "/price/summary",
        params={"days": days, **({"site": site} if site else {})},
    )

    items = data.get("items", [])
    if not items:
        scope = f"（站点: {site.upper()}）" if site else ""
        return f"当前没有活跃监控{scope}，无法生成价格摘要。"

    lines = [f"近 {days} 天价格摘要（共 {len(items)} 个商品）：\n"]
    for s in items:
        trend_icon = {"down": "📉", "up": "📈", "stable": "➡️"}.get(s.get("trend", "stable"), "➡️")
        trend_label = {"down": "下降", "up": "上涨", "stable": "稳定"}.get(s.get("trend", "stable"), "稳定")

        lines.append(
            f"- [{s['monitor_id']}] {s['product_name']} ({s['site'].upper()})\n"
            f"  当前 {s['currency']} {s.get('current_price', '—')} | "
            f"基准 {s['currency']} {s['base_price']} | "
            f"最高 {s.get('max_price', '—')} | 最低 {s.get('min_price', '—')} | "
            f"均价 {s.get('avg_price', '—')} | "
            f"趋势 {trend_icon} {trend_label} | "
            f"采集 {s.get('total_crawls', 0)} 次"
        )

    return "\n".join(lines)


# ──────────────────────────────────────────────
# Tool 3: get_price_history
# ──────────────────────────────────────────────

PRICE_HISTORY_DESCRIPTION = """\
获取指定商品的时间序列价格数据，可用于绘制价格趋势图或分析价格变化。

用户可能的问法：
- "给我看看这个商品近 7 天的价格走势"
- "iPhone 那个商品的价格变化记录"
- "帮我画个价格折线图"
- "MY 站上几个我关注的竞品今天是什么价格，给我看看趋势"

需要提供 monitor_id（必填）。可选 days（默认 7 天，最大 90 天）。
"""


async def get_price_history(monitor_id: int, days: int = 7) -> str:
    """获取价格历史"""
    data = await api_client.get(
        "/price/history",
        params={"monitor_id": monitor_id, "days": days},
    )

    points = data.get("points", [])
    name = data.get("product_name", f"Monitor #{monitor_id}")
    currency = data.get("currency", "")

    if not points:
        return f"{name} 近 {days} 天暂无价格采集数据。"

    lines = [
        f"{name} 近 {days} 天价格历史（{currency}，共 {len(points)} 条记录）：\n",
        "| 采集时间 | 价格 | 原价 | 折扣率 |",
        "|----------|------|------|--------|",
    ]

    for p in points:
        crawled = p.get("crawled_at", "")
        # 截取日期部分让表格更简洁
        if "T" in crawled:
            crawled = crawled.replace("T", " ")[:16]
        discount = f"{p.get('discount_rate', 0):.1f}%" if p.get("discount_rate") else "—"
        lines.append(f"| {crawled} | {p['price']} | {p.get('original_price', 0)} | {discount} |")

    # 简单趋势分析
    first_price = points[0]["price"]
    last_price = points[-1]["price"]
    if first_price > 0:
        change = (last_price - first_price) / first_price * 100
        if change < -2:
            trend_text = f"\n趋势分析：从 {currency} {first_price} 降至 {currency} {last_price}（↓{abs(change):.1f}%），竞品可能有降价活动。"
        elif change > 2:
            trend_text = f"\n趋势分析：从 {currency} {first_price} 涨至 {currency} {last_price}（↑{change:.1f}%），竞品可能在调价。"
        else:
            trend_text = f"\n趋势分析：价格基本稳定在 {currency} {last_price} 附近。"
    else:
        trend_text = ""

    return "\n".join(lines) + trend_text


# ── helpers ──────────────────────────────────

def _format_single_summary(s: dict) -> str:
    """格式化单个商品的价格摘要"""
    trend_icon = {"down": "📉", "up": "📈", "stable": "➡️"}.get(s.get("trend", "stable"), "➡️")
    trend_label = {"down": "下降", "up": "上涨", "stable": "稳定"}.get(s.get("trend", "stable"), "稳定")
    currency = s.get("currency", "")

    return (
        f"{s.get('product_name', '商品')} ({currency})\n"
        f"  当前价: {s.get('current_price', '—')} | 基准价: {s.get('base_price', '—')}\n"
        f"  最高: {s.get('max_price', '—')} | 最低: {s.get('min_price', '—')} | 均价: {s.get('avg_price', '—')}\n"
        f"  趋势: {trend_icon} {trend_label} | 采集次数: {s.get('total_crawls', 0)}"
    )
