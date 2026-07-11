FROM m.daocloud.io/docker.io/library/python:3.12-slim

WORKDIR /app

# 复制全部源码（pip install 需要 src/ 目录）
COPY pyproject.toml README.md ./
COPY src/ ./src/

# 安装依赖
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ .

# 环境变量（通过 docker run --env-file 或 docker-compose 注入）
ENV SENTINEL_API_BASE=https://priceminder.online/shopee
ENV SENTINEL_MCP_INTERNAL_KEY=sentinel-mcp-internal-2026
ENV SENTINEL_API_KEY=sentinel-mvp-2026
ENV MCP_MODE=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8082
ENV LOG_LEVEL=INFO

# MCP Registry ownership verification label
LABEL io.modelcontextprotocol.server.name="io.github.haidrau/sentinel-mcp-server"

EXPOSE 8082

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8082/health')" || exit 1

CMD ["python", "-m", "sentinel_mcp.server", "--mode", "http"]