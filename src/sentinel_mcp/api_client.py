"""HTTP 客户端 — 封装对 Sentinel REST API 的调用"""

from __future__ import annotations

import httpx

from sentinel_mcp import config


class SentinelAPIError(Exception):
    """Sentinel API 返回业务错误"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


def _headers() -> dict[str, str]:
    return {
        "X-Sentinel-Token": config.TOKEN,
        "Content-Type": "application/json",
    }


def _base() -> str:
    return config.API_BASE.rstrip("/")


async def get(path: str, params: dict | None = None) -> dict:
    """发送 GET 请求并返回 data 字段"""
    async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
        resp = await client.get(f"{_base()}{path}", headers=_headers(), params=params)
        resp.raise_for_status()
        body = resp.json()
    if body.get("code") and body["code"] != 0:
        raise SentinelAPIError(body["code"], body.get("message", "unknown"))
    return body.get("data", body)


async def post(path: str, json_body: dict | None = None) -> dict:
    """发送 POST 请求并返回 data 字段"""
    async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
        resp = await client.post(
            f"{_base()}{path}", headers=_headers(), json=json_body or {}
        )
        resp.raise_for_status()
        body = resp.json()
    if body.get("code") and body["code"] != 0:
        raise SentinelAPIError(body["code"], body.get("message", "unknown"))
    return body.get("data", body)


async def put(path: str, json_body: dict | None = None) -> dict:
    """发送 PUT 请求并返回 data 字段"""
    async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
        resp = await client.put(
            f"{_base()}{path}", headers=_headers(), json=json_body or {}
        )
        resp.raise_for_status()
        body = resp.json()
    if body.get("code") and body["code"] != 0:
        raise SentinelAPIError(body["code"], body.get("message", "unknown"))
    return body.get("data", body)


async def patch(path: str, json_body: dict | None = None) -> dict:
    """发送 PATCH 请求并返回 data 字段"""
    async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
        resp = await client.patch(
            f"{_base()}{path}", headers=_headers(), json=json_body or {}
        )
        resp.raise_for_status()
        body = resp.json()
    if body.get("code") and body["code"] != 0:
        raise SentinelAPIError(body["code"], body.get("message", "unknown"))
    return body.get("data", body)


async def delete(path: str) -> dict:
    """发送 DELETE 请求并返回 data 字段"""
    async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
        resp = await client.delete(f"{_base()}{path}", headers=_headers())
        resp.raise_for_status()
        body = resp.json()
    if body.get("code") and body["code"] != 0:
        raise SentinelAPIError(body["code"], body.get("message", "unknown"))
    return body.get("data", body)
