FROM m.daocloud.io/docker.io/library/python:3.12-slim

WORKDIR /app

# 安装依赖（先复制 pyproject.toml 和 README.md 安装依赖，利用 docker 层缓存）
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ .

# 复制源码
COPY src/ ./src/

# 环境变量（通过 docker run --env-file 或 docker-compose 注入）
ENV SENTINEL_API_BASE=https://priceminder.online/shopee
ENV SENTINEL_MCP_INTERNAL_KEY=sentinel-mcp-internal-2026
ENV MCP_MODE=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8082
ENV LOG_LEVEL=info

EXPOSE 8082

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8082/health')" || exit 1

CMD ["python", "-m", "sentinel_mcp.server", "--mode", "http"]
