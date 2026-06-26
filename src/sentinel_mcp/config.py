"""环境变量配置"""

import os

# Sentinel REST API base URL (不含 /api/v1 后缀)
API_BASE: str = os.environ.get(
    "SENTINEL_API_BASE",
    "https://priceminder.online/api/v1",
)

# 用户认证 Token
TOKEN: str = os.environ.get("SENTINEL_TOKEN", "")

# HTTP 请求超时 (秒)
TIMEOUT: int = int(os.environ.get("SENTINEL_TIMEOUT", "30"))
