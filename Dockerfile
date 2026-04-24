FROM python:3.13-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first (cache-friendly layer)
COPY pyproject.toml uv.lock README.md ./

# Install production dependencies only
RUN uv sync --no-dev --frozen --no-install-project

# Copy source code + logo assets + warmup script
COPY src/ src/
COPY scripts/ scripts/
COPY docs/assets/logo.png docs/assets/logo.png

# Install the project itself
RUN uv sync --no-dev --frozen

# Startup entrypoint: warmup datasets (if enabled), then launch server.
# Warmup is a no-op when MCP_BRASIL_DATASETS is empty or all datasets are
# already cached; otherwise it downloads and populates the cache before
# the server accepts requests.
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8061

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
