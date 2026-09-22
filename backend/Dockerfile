# The Paperglass backend: the library plus the FastAPI app, one non-root process.
# Build context is the repository root (the backend is a uv workspace member):
#   docker build -f backend/Dockerfile -t paperglass-backend .

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS build
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
# Dependencies first so a source change does not re-resolve them.
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY backend/pyproject.toml backend/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-workspace --package paperglass-backend --extra ocr
COPY src src
COPY backend backend
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package paperglass-backend --extra ocr

FROM python:3.12-slim-bookworm
ARG PAPERGLASS_VERSION=dev
LABEL org.opencontainers.image.source="https://github.com/SuhaasNv/paperglass" \
      org.opencontainers.image.description="Paperglass backend: scans an upload in memory, keeps the report 7 days" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.version="${PAPERGLASS_VERSION}"
RUN groupadd --system paperglass && useradd --system --gid paperglass --home /app paperglass
WORKDIR /app
COPY --from=build --chown=paperglass:paperglass /app /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    PORT=8000
USER paperglass
WORKDIR /app/backend
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request,sys; sys.exit(0 if urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8000\")}/healthz', timeout=4).status == 200 else 1)"
# Migrate, then serve. PORT comes from the platform (Railway) or defaults to 8000.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
