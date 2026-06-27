# MCP Server 部署指南（给帆帆）

## 概述

MCP Server 已完成从 stdio 本地模式到 **托管 HTTP 模式** 的改造。用户只需配置一行 URL 即可接入：

```
url: "https://mcp.priceminder.online?key=xxx"
```

## 架构

```
用户 AI 客户端 (Cherry Studio / Claude / Cursor)
    ↓  HTTPS: mcp.priceminder.online?key=xxx
    ↓
Nginx (443 → 反向代理)
    ↓
MCP Server (127.0.0.1:8020)
    ↓  认证后获取 sentinel_token
    ↓
Backend API (priceminder.online/shopee)
```

## 部署步骤

### 方式一：Docker（推荐）

```bash
# 1. 构建镜像
cd sentinel-mcp-server
docker build -t sentinel-mcp .

# 2. 运行容器
docker run -d \
  --name sentinel-mcp \
  --restart always \
  -p 127.0.0.1:8020:8020 \
  -e SENTINEL_API_BASE=https://priceminder.online/shopee \
  -e SENTINEL_MCP_INTERNAL_KEY=sentinel-mcp-internal-2026 \
  -e MCP_MODE=http \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8020 \
  -e LOG_LEVEL=info \
  sentinel-mcp

# 3. 验证
curl http://127.0.0.1:8020/health
# 应返回: {"status":"ok","service":"sentinel-mcp"}
```

### 方式二：systemd 直接部署

```bash
# 1. 安装
cd /opt
git clone <repo> sentinel-mcp-server
cd sentinel-mcp-server
python3.12 -m venv venv
venv/bin/pip install .

# 2. 安装服务
cp deploy/sentinel-mcp.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable sentinel-mcp
systemctl start sentinel-mcp

# 3. 验证
systemctl status sentinel-mcp
curl http://127.0.0.1:8020/health
```

### Nginx 配置

```bash
# 1. 复制配置
cp deploy/nginx-mcp.conf /etc/nginx/sites-available/mcp.priceminder.online

# 2. 启用
ln -s /etc/nginx/sites-available/mcp.priceminder.online /etc/nginx/sites-enabled/

# 3. SSL 证书
certbot --nginx -d mcp.priceminder.online

# 4. 重载
nginx -t && systemctl reload nginx
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SENTINEL_API_BASE` | Backend API 地址 | `https://priceminder.online/shopee` |
| `SENTINEL_MCP_INTERNAL_KEY` | 内部通信密钥 | `sentinel-mcp-internal-2026` |
| `SENTINEL_TOKEN` | 仅 stdio 模式需要 | — |
| `MCP_MODE` | 运行模式 | `http` |
| `MCP_HOST` | 监听地址 | `0.0.0.0` |
| `MCP_PORT` | 监听端口 | `8020` |
| `LOG_LEVEL` | 日志级别 | `info` |

## 注意事项

1. **Internal Key 必须一致**：MCP Server 的 `SENTINEL_MCP_INTERNAL_KEY` 必须和 Backend API 的 `MCP_INTERNAL_KEY` 相同，否则 key 验证会失败
2. **SSL 必须**：AI 客户端（特别是 Claude Desktop）要求 HTTPS，不能裸 HTTP
3. **proxy_buffering off**：Nginx 必须关闭缓冲，否则 SSE/Streamable HTTP 会卡住
4. **数据库迁移**：User 表新增了 `mcp_key`、`mcp_key_created_at`、`mcp_key_last_used_at` 字段，`id` 字段类型从 UUID 变为 VARCHAR(32)。建议清空数据库重新部署（开发阶段）
5. **新表 mcp_usage_logs**：会自动创建，记录每次 MCP 工具调用

## 监控

```bash
# 查看日志
docker logs -f sentinel-mcp
# 或
journalctl -u sentinel-mcp -f

# 健康检查
curl https://mcp.priceminder.online/health
```
