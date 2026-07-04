"""Alert Tools (2)

- get_alerts
- mark_alert_read
"""

from __future__ import annotations

from sentinel_mcp import api_client


# ──────────────────────────────────────────────
# Tool 4: get_alerts
# ──────────────────────────────────────────────

GET_ALERTS_DESCRIPTION = """\
Get price drop alerts — shows all alerts triggered by the system. Supports unread filter and site filter.

Example user queries:
- "Any new price drop alerts?"
- "Which products dropped in price recently?"
- "How many unread alerts do I have?"
- "Show me the last price drop notification"

Optional parameters:
- unread_only: return only unread alerts (default false)
- site: filter by site
- limit: max results (default 10, max 50)
"""


async def get_alerts(
    unread_only: bool = False,
    site: str | None = None,
    limit: int = 10,
) -> str:
    """获取预警列表"""
    params: dict = {"size": min(limit, 50)}
    if unread_only:
        params["is_read"] = "false"

    data = await api_client.get("/alerts", params=params)
    items = data.get("items", [])
    total = data.get("total", len(items))

    # 客户端按 site 过滤（后端 alerts 接口暂不支持 site 参数）
    if site:
        site_upper = site.upper()
        items = [
            a for a in items
            if site_upper in (a.get("site", "") or "").upper()
        ]

    if not items:
        if unread_only:
            return "没有未读的降价预警。所有预警都已处理。"
        return "暂无降价预警记录。"

    # 统计未读数
    unread_count = sum(1 for a in items if not a.get("is_read", True))
    header = f"共 {total} 条预警"
    if unread_count > 0:
        header += f"（{unread_count} 条未读）"
    header += "：\n"

    lines = [header]
    for a in items:
        read_icon = "📩" if not a.get("is_read", True) else "✓"
        product = a.get("product_name", f"Monitor #{a.get('monitor_id', '?')}")
        shop = a.get("shop_name", "")
        site_label = (a.get("site", "") or "").upper()
        currency = a.get("currency", "")
        old_p = a.get("old_price", 0)
        new_p = a.get("new_price", 0)
        pct = a.get("change_pct", 0)
        notified = a.get("notified_at", "")
        if "T" in str(notified):
            notified = str(notified).replace("T", " ")[:16]

        shop_info = f" | {shop}" if shop else ""
        lines.append(
            f"- {read_icon} [{a.get('id', '?')}] {product}{shop_info} ({site_label})\n"
            f"  {currency} {old_p} → {new_p}（↓{abs(pct):.1f}%）| {notified}"
        )

    return "\n".join(lines)


# ──────────────────────────────────────────────
# Tool 7: mark_alert_read
# ──────────────────────────────────────────────

MARK_READ_DESCRIPTION = """\
Mark an alert as read to keep the alerts list clean.

Example user queries:
- "Mark this alert as read"
- "Mark all alerts as read"
- "I've already seen that price drop notification"

Requires alert_id.
"""


async def mark_alert_read(alert_id: int) -> str:
    """标记预警已读"""
    await api_client.put(f"/alerts/{alert_id}/read")
    return f"已将预警 #{alert_id} 标记为已读。"
