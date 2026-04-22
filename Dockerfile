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
# Stage 2 — builder: cài đặt dependencies vào virtualenv
# =============================================================================
FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libpq-dev \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Pin pip để tránh breaking change
RUN pip install --no-cache-dir "pip==24.3.1"

COPY requirements.txt .

# Dùng venv thay --target để tránh edge case với namespace packages
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir \
        uvloop \
        httptools \
        gunicorn \
        -r requirements.txt

# =============================================================================
# Stage 3 — production: image cuối cùng, nhỏ và bảo mật
# =============================================================================
FROM base AS production

# Pin version libpq5 để tránh drift giữa các lần build
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy venv từ builder (không cần PYTHONPATH hack)
COPY --from=builder /venv /venv

# Chỉ copy những thứ app cần — KHÔNG dùng COPY . .
# Đảm bảo .dockerignore đã loại trừ .env, .git, tests/, v.v.
COPY --chown=appuser:appgroup app/            ./app/
COPY --chown=appuser:appgroup alembic/        ./alembic/
COPY --chown=appuser:appgroup alembic.ini     ./
COPY --chown=appuser:appgroup gunicorn.conf.py ./
COPY --chown=appuser:appgroup entrypoint.sh   ./

# chmod phải chạy trước USER appuser (cần root để chmod)
RUN chmod +x ./entrypoint.sh

# Kích hoạt venv bằng PATH thay vì PYTHONPATH
ENV PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV WEB_CONCURRENCY=4

USER appuser

EXPOSE 8000

# Mặc định: migrate-and-start (dùng cho Docker / docker-compose)
# K8s override: init container dùng "migrate", main container dùng "start"
CMD ["./entrypoint.sh"]