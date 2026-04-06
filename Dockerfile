# syntax=docker/dockerfile:1.7
# =============================================================================
# Stage 1 — base: hệ điều hành + runtime chung cho tất cả các stage
# =============================================================================
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

# =============================================================================
# Stage 2 — builder: cài đặt tất cả dependencies (layer này bị loại bỏ sau)
# =============================================================================
FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        --target /build/packages \
        uvloop \
        httptools \
        gunicorn \
        -r requirements.txt

# =============================================================================
# Stage 3 — production: image cuối cùng, nhỏ và bảo mật
# =============================================================================
FROM base AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /build/packages /app/packages
COPY --chown=appuser:appgroup . .

ENV PYTHONPATH="/app/packages:/app" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

# Gunicorn + UvicornWorker: production-grade process management
# - workers: (2 × CPU) + 1  → đổi theo số CPU của server
# - timeout: phù hợp cho request có DB/Redis call
# - preload: khởi tạo app 1 lần, fork ra các workers (tiết kiệm RAM)
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "60", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--preload", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]