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
        gcc \
        libpq-dev \
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
COPY --chown=appuser:appgroup app/          ./app/
COPY --chown=appuser:appgroup gunicorn.conf.py ./

# Kích hoạt venv bằng PATH thay vì PYTHONPATH
ENV PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# WEB_CONCURRENCY linh hoạt theo môi trường (staging vs production)
ENV WEB_CONCURRENCY=4

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c \
        "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Dùng gunicorn.conf.py để cấu hình thay vì inline args
CMD ["gunicorn", "app.main:app", "--config", "gunicorn.conf.py"]