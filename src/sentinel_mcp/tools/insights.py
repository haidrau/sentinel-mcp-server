"""运营洞察 Tools (2 个)

- get_crawl_health
- get_monitor_overview
"""

from __future__ import annotations

from sentinel_mcp import api_client


# ──────────────────────────────────────────────
# Tool 8: get_crawl_health
# ──────────────────────────────────────────────

CRAWL_HEALTH_DESCRIPTION = """\
检查后台采集引擎的运行状态，包括采集次数、成功率、各站点运行情况。

用户可能的问法：
- "采集系统运行正常吗"
- "今天采集了多少次"
- "各站点的采集成功率怎样"

无需参数，直接返回采集系统健康报告。
"""


async def get_crawl_health() -> str:
    """获取采集健康度"""
    # 并行调用两个端点
    summary_data, site_stats = await _fetch_health_data()

    # 从 telemetry summary 中提取关键指标
    crawl_events = summary_data.get("crawl_cycle_completed", {})
    total_crawls = crawl_events.get("total", 0)
    today_crawls = crawl_events.get("today", 0)

    alert_events = summary_data.get("alert_triggered", {})
    total_alerts = alert_events.get("total", 0)
    today_alerts = alert_events.get("today", 0)

    lines = [
        "采集系统健康报告：\n",
        f"📊 采集统计：",
        f"  - 总采集周期: {total_crawls} 次",
        f"  - 今日采集: {today_crawls} 次",
        f"",
        f"🔔 预警统计：",
        f"  - 总预警: {total_alerts} 条",
        f"  - 今日预警: {today_alerts} 条",
    ]

    # 各站点详情
    if site_stats:
        lines.append("\n🌏 各站点采集情况：")
        for site_key, stats in site_stats.items():
            site_label = site_key.upper()
            total = stats.get("total", 0)
            success = stats.get("success", 0)
            rate = stats.get("rate", 0)
            lines.append(f"  - {site_label}: {total} 次采集，成功 {success} 次，成功率 {rate}%")
    else:
        lines.append("\n⚠️ 暂无各站点采集数据。")

    # 总体健康判断
    if today_crawls == 0:
        lines.append("\n⚠️ 今日暂无采集记录，采集引擎可能未运行，请检查 Crawler 扩展。")
    else:
        lines.append("\n✅ 采集系统运行正常。")

    return "\n".join(lines)


# ──────────────────────────────────────────────
# Tool 9: get_monitor_overview
# ──────────────────────────────────────────────

MONITOR_OVERVIEW_DESCRIPTION = """\
获取所有监控的总览大盘数据，包括活跃监控数、今日采集/预警、各站点分布等。

用户可能的问法：
- "给我一个监控总览"
- "我的所有商品监控情况怎样"
- "大盘数据看看"

无需参数，返回监控大盘摘要。
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


# ── helpers ──────────────────────────────────

async def _fetch_health_data() -> tuple[dict, dict]:
    """并行获取 telemetry summary 和 site-stats"""
    import asyncio

    async def fetch_summary():
        try:
            return await api_client.get("/telemetry/summary", params={"days": 7})
        except Exception:
            return {}

    async def fetch_site_stats():
        try:
            return await api_client.get("/telemetry/site-stats", params={"days": 7})
        except Exception:
            return {}

    return await asyncio.gather(fetch_summary(), fetch_site_stats())
