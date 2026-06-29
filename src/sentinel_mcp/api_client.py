"""HTTP 客户端 — 封装对 Sentinel REST API 的调用

支持两种 token 来源：
- stdio 模式：从 config.TOKEN 环境变量获取
- HTTP 托管模式：从 auth 中间件注入的 ContextVar 获取（每请求独立）
"""

from __future__ import annotations

import logging
import time

import httpx

from sentinel_mcp import config

logger = logging.getLogger("sentinel-mcp.api_client")


class SentinelAPIError(Exception):
    """Sentinel API 返回业务错误"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


def _resolve_token() -> str:
    """
    获取当前请求的 Sentinel Token。
    优先使用 auth 中间件注入的 ContextVar（HTTP 模式），
    回退到 config.TOKEN（stdio 模式）。
    """
    try:
        from sentinel_mcp.auth import get_auth_token
        ctx_token = get_auth_token()
        if ctx_token:
            return ctx_token
    except ImportError:
        pass
    return config.TOKEN


def _resolve_tool_name(explicit: str) -> str:
    """
    获取当前 Tool 名称（用于日志上报）。
    优先使用显式传入的名称，回退到 server.py 设置的 ContextVar。
    """
    if explicit:
        return explicit
    try:
        from sentinel_mcp.server import _current_tool_name
        return _current_tool_name.get()
    except ImportError:
        return ""


def _headers() -> dict[str, str]:
    return {
        "X-Sentinel-Token": _resolve_token(),
        "X-Api-Key": config.API_KEY,
        "Content-Type": "application/json",
    }


def _base() -> str:
    return config.API_BASE.rstrip("/")


async def _log_usage(tool_name: str, status: str, start_time: float,
                     error_message: str | None = None):
    """异步上报 Tool 调用日志到后端（fire-and-forget，不影响主流程）"""
    try:
        from sentinel_mcp.auth import get_user_id, get_mcp_key
        user_id = get_user_id()
        mcp_key_prefix = get_mcp_key()
    except ImportError:
        user_id = ""
        mcp_key_prefix = ""

    if not user_id:
        return  # stdio 模式不上报

    duration_ms = int((time.time() - start_time) * 1000)
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(
                f"{_base()}/mcp/log-usage",
                headers={
                    "X-MCP-Internal-Key": config.MCP_INTERNAL_KEY,
                    "X-MCP-User-Id": user_id,
                    "X-MCP-Key-Prefix": mcp_key_prefix,
                    "Content-Type": "application/json",
                },
                json={
                    "tool_name": tool_name,
                    "status": status,
                    "error_message": error_message,
                    "duration_ms": duration_ms,
                    "client_info": "sentinel-mcp-hosted",
                },
            )
    except Exception as e:
        logger.debug("Usage log failed (non-critical): %s", e)


def _log_req(method: str, path: str, params: dict | None = None):
    """记录 API 请求"""
    extra = f" params={params}" if params else ""
    logger.info("→ [API] %s %s%s", method, path, extra)


def _log_resp(method: str, path: str, dur_ms: int, code, data_preview: str = ""):
    """记录 API 响应"""
    preview = f" | {data_preview}" if data_preview else ""
    logger.info("← [API] %s %s (%dms, code=%s)%s", method, path, dur_ms, code, preview)


def _log_err(method: str, path: str, dur_ms: int, err: Exception):
    """记录 API 错误"""
    logger.warning("✕ [API] %s %s (%dms) → %s", method, path, dur_ms, err)


async def get(path: str, params: dict | None = None, *, _tool_name: str = "") -> dict:
    """发送 GET 请求并返回 data 字段"""
    start = time.time()
    tool = _resolve_tool_name(_tool_name)
    _log_req("GET", path, params)
    try:
        async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
            resp = await client.get(f"{_base()}{path}", headers=_headers(), params=params)
            resp.raise_for_status()
            body = resp.json()
        if body.get("code") and body["code"] != 0:
            raise SentinelAPIError(body["code"], body.get("message", "unknown"))
        result = body.get("data", body)
        dur = int((time.time() - start) * 1000)
        data_preview = str(result)[:120] if isinstance(result, dict) else ""
        _log_resp("GET", path, dur, body.get("code", "N/A"), data_preview)
        if tool:
            await _log_usage(tool, "success", start)
        return result
    except Exception as e:
        dur = int((time.time() - start) * 1000)
        _log_err("GET", path, dur, e)
        if tool:
            await _log_usage(tool, "error", start, str(e)[:200])
        raise


async def post(path: str, json_body: dict | None = None, *, _tool_name: str = "") -> dict:
    """发送 POST 请求并返回 data 字段"""
    start = time.time()
    tool = _resolve_tool_name(_tool_name)
    _log_req("POST", path)
    try:
        async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
            resp = await client.post(
                f"{_base()}{path}", headers=_headers(), json=json_body or {}
            )
            resp.raise_for_status()
            body = resp.json()
        if body.get("code") and body["code"] != 0:
            raise SentinelAPIError(body["code"], body.get("message", "unknown"))
        result = body.get("data", body)
        dur = int((time.time() - start) * 1000)
        data_preview = str(result)[:120] if isinstance(result, dict) else ""
        _log_resp("POST", path, dur, body.get("code", "N/A"), data_preview)
        if tool:
            await _log_usage(tool, "success", start)
        return result
    except Exception as e:
        dur = int((time.time() - start) * 1000)
        _log_err("POST", path, dur, e)
        if tool:
            await _log_usage(tool, "error", start, str(e)[:200])
        raise


async def put(path: str, json_body: dict | None = None, *, _tool_name: str = "") -> dict:
    """发送 PUT 请求并返回 data 字段"""
    start = time.time()
    tool = _resolve_tool_name(_tool_name)
    _log_req("PUT", path)
    try:
        async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
            resp = await client.put(
                f"{_base()}{path}", headers=_headers(), json=json_body or {}
            )
            resp.raise_for_status()
            body = resp.json()
        if body.get("code") and body["code"] != 0:
            raise SentinelAPIError(body["code"], body.get("message", "unknown"))
        result = body.get("data", body)
        dur = int((time.time() - start) * 1000)
        data_preview = str(result)[:120] if isinstance(result, dict) else ""
        _log_resp("PUT", path, dur, body.get("code", "N/A"), data_preview)
        if tool:
            await _log_usage(tool, "success", start)
        return result
    except Exception as e:
        dur = int((time.time() - start) * 1000)
        _log_err("PUT", path, dur, e)
        if tool:
            await _log_usage(tool, "error", start, str(e)[:200])
        raise


async def patch(path: str, json_body: dict | None = None, *, _tool_name: str = "") -> dict:
    """发送 PATCH 请求并返回 data 字段"""
    start = time.time()
    tool = _resolve_tool_name(_tool_name)
    _log_req("PATCH", path)
    try:
        async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
            resp = await client.patch(
                f"{_base()}{path}", headers=_headers(), json=json_body or {}
            )
            resp.raise_for_status()
            body = resp.json()
        if body.get("code") and body["code"] != 0:
            raise SentinelAPIError(body["code"], body.get("message", "unknown"))
        result = body.get("data", body)
        dur = int((time.time() - start) * 1000)
        data_preview = str(result)[:120] if isinstance(result, dict) else ""
        _log_resp("PATCH", path, dur, body.get("code", "N/A"), data_preview)
        if tool:
            await _log_usage(tool, "success", start)
        return result
    except Exception as e:
        dur = int((time.time() - start) * 1000)
        _log_err("PATCH", path, dur, e)
        if tool:
            await _log_usage(tool, "error", start, str(e)[:200])
        raise


async def delete(path: str, *, _tool_name: str = "") -> dict:
    """发送 DELETE 请求并返回 data 字段"""
    start = time.time()
    tool = _resolve_tool_name(_tool_name)
    _log_req("DELETE", path)
    try:
        async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
            resp = await client.delete(f"{_base()}{path}", headers=_headers())
            resp.raise_for_status()
            body = resp.json()
        if body.get("code") and body["code"] != 0:
            raise SentinelAPIError(body["code"], body.get("message", "unknown"))
        result = body.get("data", body)
        dur = int((time.time() - start) * 1000)
        data_preview = str(result)[:120] if isinstance(result, dict) else ""
        _log_resp("DELETE", path, dur, body.get("code", "N/A"), data_preview)
        if tool:
            await _log_usage(tool, "success", start)
        return result
    except Exception as e:
        dur = int((time.time() - start) * 1000)
        _log_err("DELETE", path, dur, e)
        if tool:
            await _log_usage(tool, "error", start, str(e)[:200])
        raise
