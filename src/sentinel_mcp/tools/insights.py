"""Insight Tools (2)

- get_crawl_health
- get_monitor_overview
"""

from __future__ import annotations

from sentinel_mcp import api_client


# ──────────────────────────────────────────────
# Tool 8: get_crawl_health
# ──────────────────────────────────────────────

CRAWL_HEALTH_DESCRIPTION = """\
Check the crawler engine status — total crawls, success rate, per-site stats.

Example user queries:
- "Is the crawler system running normally?"
- "How many crawls today?"
- "What's the success rate for each site?"

No parameters required. Returns a health report.
No parameters required. Returns a health report.


async def get_crawl_health() -> str:
    """Get crawler health stats (from PriceHistory, per-user isolation)"""
    import asyncio

    async def fetch_dashboard():
        try:
            return await api_client.get("/user/dashboard")
        except Exception:
            return {}

    async def fetch_price_summary():
        try:
            return await api_client.get("/price/summary", params={"days": 7})
        except Exception:
            return {}

    dashboard, price_data = await asyncio.gather(fetch_dashboard(), fetch_price_summary())

    # 从 /user/dashboard 获取用户级采集统计（按 user_id 隔离）
    today_crawls = dashboard.get("today_crawl_count", 0)
    week_crawls = dashboard.get("week_crawl_count", 0)
    today_alerts = dashboard.get("today_alert_count", 0)
    total_monitors = dashboard.get("total_monitors", 0)
    active_monitors = dashboard.get("active_monitors", 0)

    lines = [
        "采集系统健康报告：\n",
        "📊 采集统计（近 7 天）：",
        f"  - 今日采集: {today_crawls} 次",
        f"  - 近 7 天采集: {week_crawls} 次",
        "",
        f"📦 监控状态：",
        f"  - 总监控: {total_monitors}（活跃 {active_monitors}）",
        "",
        f"🔔 预警统计：",
        f"  - 今日预警: {today_alerts} 条",
    ]

    # 各站点采集详情（从 /price/summary 聚合，按用户隔离）
    items = price_data.get("items", [])
    if items:
        site_stats: dict[str, dict] = {}
        stale_monitors: list[str] = []

        for s in items:
            site = (s.get("site") or "unknown").upper()
            crawls = s.get("total_crawls", 0)

            if site not in site_stats:
                site_stats[site] = {"crawls": 0, "monitors": 0, "stale": 0}
            site_stats[site]["crawls"] += crawls
            site_stats[site]["monitors"] += 1

            if crawls == 0:
                site_stats[site]["stale"] += 1
                stale_monitors.append(s.get("product_name", f"#{s.get('monitor_id', '?')}"))

        lines.append("\n🌏 各站点采集情况（近 7 天）：")
        for site, stats in sorted(site_stats.items()):
            stale_hint = f"，{stats['stale']} 个无数据" if stats["stale"] > 0 else ""
            lines.append(f"  - {site}: {stats['crawls']} 次采集，{stats['monitors']} 个监控{stale_hint}")

        # 过期监控告警
        if stale_monitors:
            lines.append(f"\n⚠️ 近 7 天无采集数据的监控（{len(stale_monitors)} 个）：")
            for name in stale_monitors[:5]:
                lines.append(f"  - {name}")
            if len(stale_monitors) > 5:
                lines.append(f"  ...等共 {len(stale_monitors)} 个")

    # 总体健康判断
    if today_crawls == 0 and active_monitors > 0:
        lines.append("\n⚠️ 今日暂无采集记录，采集引擎可能未运行，请检查 Crawler 扩展。")
    elif week_crawls == 0 and active_monitors > 0:
        lines.append("\n⚠️ 近 7 天无采集记录，采集引擎可能已停止运行。")
    else:
        lines.append("\n✅ 采集系统运行正常。")

    return "\n".join(lines)


# ──────────────────────────────────────────────
# Tool 9: get_monitor_overview
# ──────────────────────────────────────────────

MONITOR_OVERVIEW_DESCRIPTION = """\
Get a dashboard overview of all monitors — active count, today's crawls/alerts, per-site distribution.

Example user queries:
- "Give me a monitor overview"
- "How are all my monitors doing?"
- "Show me the dashboard"

No parameters required. Returns a dashboard summary.
"""


async def get_monitor_overview() -> str:
    """获取监控大盘"""
    # 优先使用 /user/dashboard 端点（用户级汇总）
    try:
        dashboard = await api_client.get("/user/dashboard")
        total = dashboard.get("total_monitors", 0)
        active = dashboard.get("active_monitors", 0)
        paused = dashboard.get("paused_monitors", 0)
        today_crawls = dashboard.get("today_crawl_count", 0)
        today_alerts = dashboard.get("today_alert_count", 0)
        price_drop = dashboard.get("price_drop_count", 0)
        site_list = dashboard.get("site_summary", [])

        site_summary = " | ".join(
            f"{s['site']}: {s.get('active', 0)} 活跃"
            for s in site_list
        ) if site_list else "暂无"

        lines = [
            "监控大盘总览：\n",
            f"📦 监控总数: {total}（活跃 {active} / 暂停 {paused}）",
            f"🌏 站点分布: {site_summary}",
            f"📊 今日采集: {today_crawls} 次",
            f"🔔 今日预警: {today_alerts} 条",
        ]

        if price_drop > 0 and active > 0:
            lines.append(f"📉 降价商品: {price_drop}/{active}（{price_drop/active*100:.0f}%）")

        return "\n".join(lines)
    except Exception:
        pass  # 降级到 monitors 接口

    # 降级方案：从 monitors 接口聚合
    monitors_data = await api_client.get("/monitors", params={"size": 100})
    items = monitors_data.get("items", [])
    total = monitors_data.get("total", len(items))

    active_count = sum(1 for m in items if m.get("status") == "active")
    paused_count = sum(1 for m in items if m.get("status") == "paused")

    site_counts: dict[str, int] = {}
    price_drop_count = 0
    for m in items:
        s = (m.get("site") or "unknown").upper()
        site_counts[s] = site_counts.get(s, 0) + 1
        if m.get("change_pct") is not None and m["change_pct"] < 0:
            price_drop_count += 1

    site_summary = " | ".join(f"{s}: {c}" for s, c in sorted(site_counts.items()))

    lines = [
        "监控大盘总览：\n",
        f"📦 监控总数: {total}（活跃 {active_count} / 暂停 {paused_count}）",
        f"🌏 站点分布: {site_summary}" if site_summary else "🌏 站点分布: 暂无",
    ]

    if price_drop_count > 0:
        lines.append(f"📉 降价商品: {price_drop_count}/{total}（{price_drop_count/total*100:.0f}%）")

    return "\n".join(lines)
