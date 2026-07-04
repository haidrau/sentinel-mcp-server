# MCP 端到端测试用例

> 日期：2026-06-22
> 前置条件：帆帆已部署 API 改动 + 落地页
> Token：替换下方 `{TOKEN}` 为你的实际 token（如 `9df2b0b5-f720-40f5-9f44-618dc68e093f`）
> API Base：`https://priceminder.online/api/v1`

---

## Part 1: API 端点验证（4 处改动）

### E2E-01: GET /price/summary 批量模式

**目的**：验证 monitor_id 改为可选后，不传 ID 能返回所有活跃监控的摘要。

**输入**：
```bash
curl -s -H "X-Sentinel-Token: {TOKEN}" \
  "https://priceminder.online/api/v1/price/summary?days=3"
```

**预期输出**（关键字段）：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "monitor_id": 40,
        "product_name": "xxx",
        "shop_name": "xxx",
        "site": "sg",
        "currency": "SGD",
        "base_price": 6.19,
        "current_price": 5.50,
        "max_price": 6.19,
        "min_price": 5.30,
        "avg_price": 5.73,
        "total_crawls": 15,
        "trend": "down",
        "last_crawled_at": "2026-06-22T14:00:00"
      }
    ]
  }
}
```

**验证点**：
- [ ] data.items 是数组（不是单个对象）
- [ ] 每个 item 包含 shop_name、site 字段
- [ ] trend 值为 "down" / "up" / "stable" 之一

---

### E2E-02: GET /alerts enriched 字段

**目的**：验证 alerts 返回包含 product_name、shop_name、site、currency。

**输入**：
```bash
curl -s -H "X-Sentinel-Token: {TOKEN}" \
  "https://priceminder.online/api/v1/alerts?size=3"
```

**预期输出**（关键字段）：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 10,
        "monitor_id": 40,
        "product_name": "xxx",
        "shop_name": "xxx",
        "site": "sg",
        "currency": "SGD",
        "old_price": 6.19,
        "new_price": 5.50,
        "change_pct": -11.15,
        "notified_at": "2026-06-21T14:30:00",
        "is_read": false
      }
    ],
    "total": 5,
    "unread_count": 2,
    "page": 1,
    "size": 3
  }
}
```

**验证点**：
- [ ] items 中每条包含 product_name、shop_name、site、currency（之前没有这些字段）
- [ ] data 包含 unread_count 字段
- [ ] old_price / new_price / change_pct 是数字类型

---

### E2E-03: GET /monitors keyword 搜索

**目的**：验证新增的 keyword 参数能模糊匹配商品名/店铺名。

**输入**：
```bash
# 先查全量，确认有数据
curl -s -H "X-Sentinel-Token: {TOKEN}" \
  "https://priceminder.online/api/v1/monitors?size=5"

# 再用 keyword 搜索（替换为你实际的商品名关键词）
curl -s -H "X-Sentinel-Token: {TOKEN}" \
  "https://priceminder.online/api/v1/monitors?keyword=iPhone"
```

**预期输出**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 40,
        "product_name": "iPhone 15 Pro Max Case",
        "shop_name": "xxx",
        "site": "sg"
      }
    ],
    "total": 1
  }
}
```

**验证点**：
- [ ] keyword 搜索返回的子集 ≤ 全量查询的 total
- [ ] 返回的每条 item 的 product_name 或 shop_name 包含关键词（不区分大小写）
- [ ] keyword 为空时不影响原有查询逻辑

---

### E2E-04: GET /user/dashboard 新端点

**目的**：验证用户级 dashboard 端点正常工作。

**输入**：
```bash
curl -s -H "X-Sentinel-Token: {TOKEN}" \
  "https://priceminder.online/api/v1/user/dashboard"
```

**预期输出**：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total_monitors": 5,
    "active_monitors": 3,
    "paused_monitors": 2,
    "today_crawl_count": 42,
    "today_alert_count": 1,
    "week_crawl_count": 280,
    "price_drop_count": 2,
    "site_summary": [
      {"site": "SG", "total": 3, "active": 2},
      {"site": "MY", "total": 2, "active": 1}
    ]
  }
}
```

**验证点**：
- [ ] 只返回当前 token 用户的数据（不是全局数据）
- [ ] site_summary 是数组，每项含 site、total、active
- [ ] 数值字段都是整数（不是 null）

---

## Part 2: MCP Server Tool 测试（10 个 Tool）

**前置**：本地安装 MCP Server

```bash
cd E:\99--Code\0-QoderWork\sentinel-mcp-server
pip install -e .
set SENTINEL_API_BASE=https://priceminder.online/api/v1
set SENTINEL_TOKEN={TOKEN}
```

以下每个 Tool 用 Python 直接调用函数来验证（不走 MCP 协议，跳过 stdio 层）。

### E2E-05: get_monitor_list

**输入**：
```python
import asyncio
from sentinel_mcp.tools.monitors import get_monitor_list

result = asyncio.run(get_monitor_list(site="sg"))
print(result)
```

**预期输出**（示例）：
```
共 3 个监控项：

- [40] iPhone 15 Pro Max Case | Anker Store | SG | 基准价 SGD 6.19，当前价 SGD 5.50（↓11.15%）| 🟢 监控中
- [41] AirPods Pro 2 | Apple Store | SG | 基准价 SGD 349（尚未采集到价格）| 🟢 监控中
- [42] Samsung Case | Samsung Store | SG | 基准价 SGD 29.90，当前价 SGD 29.90（→0%）| ⏸ 已暂停
```

**验证点**：
- [ ] 输出是格式化的文本（不是 JSON）
- [ ] 包含商品名、店铺名、站点、价格信息、状态标签
- [ ] site 过滤生效

---

### E2E-06: get_price_summary (批量)

**输入**：
```python
from sentinel_mcp.tools.prices import get_price_summary

result = asyncio.run(get_price_summary(days=3))
print(result)
```

**预期输出**（示例）：
```
近 3 天价格摘要（共 3 个商品）：

- [40] iPhone 15 Pro Max Case (SG)
  当前 SGD 5.50 | 基准 SGD 6.19 | 最高 6.19 | 最低 5.30 | 均价 5.73 | 趋势 📉 下降 | 采集 15 次
- [41] AirPods Pro 2 (SG)
  当前 SGD 349 | 基准 SGD 349 | 最高 349 | 最低 349 | 均价 349 | 趋势 ➡️ 稳定 | 采集 10 次
```

**验证点**：
- [ ] 不传 monitor_id 返回所有活跃监控
- [ ] 包含 trend 趋势图标（📉/📈/➡️）

---

### E2E-07: get_price_summary (单个)

**输入**：
```python
result = asyncio.run(get_price_summary(monitor_id=40))
print(result)
```

**预期输出**（示例）：
```
iPhone 15 Pro Max Case (SGD)
  当前价: 5.50 | 基准价: 6.19
  最高: 6.19 | 最低: 5.30 | 均价: 5.73
  趋势: 📉 下降 | 采集次数: 15
```

**验证点**：
- [ ] 传 monitor_id 返回单个商品摘要
- [ ] 数据与 E2E-06 中对应 item 一致

---

### E2E-08: get_price_history

**输入**：
```python
from sentinel_mcp.tools.prices import get_price_history

result = asyncio.run(get_price_history(monitor_id=40, days=3))
print(result)
```

**预期输出**（示例）：
```
iPhone 15 Pro Max Case 近 3 天价格历史（SGD，共 8 条记录）：

| 采集时间 | 价格 | 原价 | 折扣率 |
|----------|------|------|--------|
| 2026-06-20 08:00 | 6.19 | 6.99 | 11.4% |
| 2026-06-20 14:00 | 6.19 | 6.99 | 11.4% |
| 2026-06-21 08:00 | 5.50 | 6.99 | 21.3% |
| 2026-06-21 14:00 | 5.50 | 6.99 | 21.3% |

趋势分析：从 SGD 6.19 降至 SGD 5.50（↓11.1%），竞品可能有降价活动。
```

**验证点**：
- [ ] 输出是 Markdown 表格格式
- [ ] 包含趋势分析文本
- [ ] 数据点数量与 days 参数匹配

---

### E2E-09: get_alerts

**输入**：
```python
from sentinel_mcp.tools.alerts import get_alerts

result = asyncio.run(get_alerts(unread_only=True, limit=5))
print(result)
```

**预期输出**（示例）：
```
共 5 条预警（2 条未读）：

- 📩 [10] iPhone 15 Pro Max Case | Anker Store (SG)
  SGD 6.19 → 5.50（↓11.2%）| 2026-06-21 14:30
- 📩 [11] Samsung Case | Samsung Store (SG)
  SGD 29.90 → 25.90（↓13.4%）| 2026-06-20 18:00
- ✓ [9] AirPods Pro 2 | Apple Store (SG)
  SGD 349 → 329（↓5.7%）| 2026-06-19 22:15
```

**验证点**：
- [ ] 📩 表示未读，✓ 表示已读
- [ ] 包含 product_name、shop_name、site
- [ ] unread_only=True 时只返回未读

---

### E2E-10: add_monitor

**输入**：
```python
from sentinel_mcp.tools.monitors import add_monitor

result = asyncio.run(add_monitor(
    product_url="https://shopee.sg/product/99999",
    alert_threshold=10
))
print(result)
```

**预期输出**（示例）：
```
已添加监控（ID: 43）。
- URL: https://shopee.sg/product/99999
- 站点: SG
- 降价阈值: 10%

系统已开始自动采集价格。当竞品降价超过 10% 时，会通过飞书推送预警。
```

**验证点**：
- [ ] 返回新创建的 monitor ID
- [ ] 自动从 URL 提取站点（shopee.sg → SG）
- [ ] 重复添加时返回 "已在监控列表中" 提示

**清理**：
```python
# 测试完后删除
from sentinel_mcp.api_client import delete
asyncio.run(delete("/monitors/43"))
```

---

### E2E-11: update_monitor_status

**输入**：
```python
from sentinel_mcp.tools.monitors import update_monitor_status

# 暂停
result = asyncio.run(update_monitor_status(monitor_id=40, status="paused"))
print(result)

# 恢复
result = asyncio.run(update_monitor_status(monitor_id=40, status="active"))
print(result)
```

**预期输出**：
```
已暂停监控：iPhone 15 Pro Max Case（ID: 40）。系统不再采集该商品的价格。如需恢复，告诉我即可。

已恢复监控：iPhone 15 Pro Max Case（ID: 40）。系统将继续采集该商品的价格。
```

**验证点**：
- [ ] 暂停和恢复都返回确认文本
- [ ] 无效 status 值返回错误提示

---

### E2E-12: mark_alert_read

**输入**：
```python
from sentinel_mcp.tools.alerts import mark_alert_read

result = asyncio.run(mark_alert_read(alert_id=10))
print(result)
```

**预期输出**：
```
已将预警 #10 标记为已读。
```

**验证点**：
- [ ] 返回确认文本
- [ ] 再次查询 alerts 时该条 is_read=True

---

### E2E-13: get_crawl_health

**输入**：
```python
from sentinel_mcp.tools.insights import get_crawl_health

result = asyncio.run(get_crawl_health())
print(result)
```

**预期输出**（示例）：
```
采集系统健康报告：

📊 采集统计：
  - 总采集周期: 1200 次
  - 今日采集: 156 次

🔔 预警统计：
  - 总预警: 15 条
  - 今日预警: 3 条

🌏 各站点采集情况：
  - SG: 800 次采集，成功 790 次，成功率 98.8%
  - MY: 400 次采集，成功 395 次，成功率 98.8%

✅ 采集系统运行正常。
```

**验证点**：
- [ ] 包含采集统计、预警统计、站点详情三个区块
- [ ] 今日采集为 0 时显示 ⚠️ 警告

---

### E2E-14: get_monitor_overview

**输入**：
```python
from sentinel_mcp.tools.insights import get_monitor_overview

result = asyncio.run(get_monitor_overview())
print(result)
```

**预期输出**（示例）：
```
监控大盘总览：

📦 监控总数: 5（活跃 3 / 暂停 2）
🌏 站点分布: SG: 2 活跃 | MY: 1 活跃
📊 今日采集: 156 次
🔔 今日预警: 3 条
📉 降价商品: 2/3（67%）
```

**验证点**：
- [ ] 使用 /user/dashboard 端点
- [ ] 包含监控总数、活跃/暂停数、站点分布、今日采集/预警

---

### E2E-15: search_my_products

**输入**：
```python
from sentinel_mcp.tools.monitors import search_my_products

result = asyncio.run(search_my_products(keyword="iPhone"))
print(result)
```

**预期输出**（示例）：
```
搜索 "iPhone" 找到 1 个匹配：

- [40] iPhone 15 Pro Max Case | Anker Store | SG，当前价 SGD 5.50 | 🟢 监控中
```

**验证点**：
- [ ] 使用后端 keyword 参数（不是客户端过滤）
- [ ] 不区分大小写
- [ ] 无匹配时返回 "未找到" 提示

---

## Part 3: 落地页验证

### E2E-16: 落地页访问

**输入**：浏览器访问 `https://priceminder.online/priceminder/mcp/`

**验证点**：
- [ ] 页面正常渲染，无白屏
- [ ] Hero 区：标题 "Shopee 盯价哨兵 MCP"、3 个卖点卡片
- [ ] 快速开始：3 步引导、JSON 配置代码块
- [ ] 10 Tool 卡片：Tab 过滤（全部/查询/操作/洞察）正常
- [ ] 5 个场景对话卡片：气泡布局正确
- [ ] 差异化对比表：✓ 和 ✕ 图标显示正确
- [ ] 配置参考：4 个客户端 Tab 切换正常
- [ ] 响应式：手机端布局正常

---

## 测试进度跟踪

| # | 用例 | 状态 | 备注 |
|---|------|------|------|
| E2E-01 | /price/summary 批量 | ⬜ | |
| E2E-02 | /alerts enriched | ⬜ | |
| E2E-03 | /monitors keyword | ⬜ | |
| E2E-04 | /user/dashboard | ⬜ | |
| E2E-05 | get_monitor_list | ⬜ | |
| E2E-06 | get_price_summary (批量) | ⬜ | |
| E2E-07 | get_price_summary (单个) | ⬜ | |
| E2E-08 | get_price_history | ⬜ | |
| E2E-09 | get_alerts | ⬜ | |
| E2E-10 | add_monitor | ⬜ | |
| E2E-11 | update_monitor_status | ⬜ | |
| E2E-12 | mark_alert_read | ⬜ | |
| E2E-13 | get_crawl_health | ⬜ | |
| E2E-14 | get_monitor_overview | ⬜ | |
| E2E-15 | search_my_products | ⬜ | |
| E2E-16 | 落地页 | ⬜ | |
