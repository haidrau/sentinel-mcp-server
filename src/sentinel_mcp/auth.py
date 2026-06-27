"""MCP Server 认证中间件 — 从 query param 提取 key，验证后注入 sentinel_token"""

from __future__ import annotations

import logging
from contextvars import ContextVar
from urllib.parse import parse_qs

import httpx

from sentinel_mcp import config

logger = logging.getLogger("sentinel-mcp.auth")

# ── 请求级上下文变量 ────────────────────────────────────
# 每个 HTTP 请求独立持有自己的 token / user_id，支持多用户并发
_auth_token_var: ContextVar[str] = ContextVar("auth_token", default="")
_user_id_var: ContextVar[str] = ContextVar("user_id", default="")
_mcp_key_var: ContextVar[str] = ContextVar("mcp_key", default="")


def get_auth_token() -> str:
    """获取当前请求的 Sentinel Token"""
    return _auth_token_var.get()


def get_user_id() -> str:
    """获取当前请求的 User ID"""
    return _user_id_var.get()


def get_mcp_key() -> str:
    """获取当前请求的 MCP Key"""
    return _mcp_key_var.get()


# ── Key 缓存（避免每次 Tool 调用都请求后端验证）─────────
_key_cache: dict[str, dict] = {}  # key -> {"token": str, "user_id": str, "client_type": str}
_CACHE_MAX_SIZE = 1000


async def verify_key(key: str) -> dict | None:
    """
    向后端 API 验证 MCP Key，返回用户信息。
    成功返回 {"token": str, "user_id": str, "client_type": str}，失败返回 None。
    带简单内存缓存，避免重复验证。
    """
    # 检查缓存
    if key in _key_cache:
        return _key_cache[key]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{config.API_BASE}/mcp/verify-key",
                params={"key": key},
                headers={
                    "X-MCP-Internal-Key": config.MCP_INTERNAL_KEY,
                },
            )
            resp.raise_for_status()
            body = resp.json()
    except Exception as e:
        logger.error("verify-key 请求失败: %s", e)
        return None

    data = body.get("data", {})
    if not data.get("valid"):
        return None

    info = {
        "token": data["sentinel_token"],
        "user_id": data["user_id"],
        "client_type": data.get("client_type", "seller"),
    }

    # 写入缓存（限制大小）
    if len(_key_cache) >= _CACHE_MAX_SIZE:
        # 简单策略：清除一半缓存
        keys_to_remove = list(_key_cache.keys())[:_CACHE_MAX_SIZE // 2]
        for k in keys_to_remove:
            del _key_cache[k]
    _key_cache[key] = info

    return info


# ── ASGI 中间件 ────────────────────────────────────────

class AuthMiddleware:
    """
    ASGI 中间件：从 query string 提取 ?key=xxx，验证后注入 ContextVar。

    工作流程：
    1. 解析 URL query string 获取 key 参数
    2. 调用后端 /mcp/verify-key 验证 key
    3. 验证通过 → 设置 ContextVar (token, user_id) → 继续处理请求
    4. 验证失败 → 返回 401 JSON 响应
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 健康检查端点：跳过认证
            path = scope.get("path", "")
            if path == "/health":
                await self._send_health(send)
                return

            # 解析 query string 获取 key
            query_string = scope.get("query_string", b"").decode("utf-8")
            params = parse_qs(query_string)
            key = params.get("key", [""])[0]

            if not key:
                await self._send_error(send, 401, "缺少 MCP Key，请在 URL 中添加 ?key=YOUR_KEY")
                return

            # 验证 key
            info = await verify_key(key)
            if info is None:
                await self._send_error(send, 401, "MCP Key 无效或已过期，请重新获取")
                return

            # 注入上下文
            _auth_token_var.set(info["token"])
            _user_id_var.set(info["user_id"])
            _mcp_key_var.set(key[:8])  # 仅保留前缀用于日志

        await self.app(scope, receive, send)

    @staticmethod
    async def _send_error(send, status_code: int, message: str):
        """发送 JSON 错误响应"""
        import json
        body = json.dumps({"error": message}).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": status_code,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })

    @staticmethod
    async def _send_health(send):
        """健康检查响应"""
        import json
        body = json.dumps({"status": "ok", "service": "sentinel-mcp"}).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })
