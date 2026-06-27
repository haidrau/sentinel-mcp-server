FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# 复制源码
COPY src/ ./src/

# 环境变量（通过 docker run --env-file 或 docker-compose 注入）
ENV SENTINEL_API_BASE=https://priceminder.online/shopee
ENV SENTINEL_MCP_INTERNAL_KEY=sentinel-mcp-internal-2026
ENV MCP_MODE=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8020
ENV LOG_LEVEL=info

EXPOSE 8020

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8020/health')" || exit 1

CMD ["python", "-m", "sentinel_mcp.server", "--mode", "http"]
