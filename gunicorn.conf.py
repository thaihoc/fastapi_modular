import os

# Worker
worker_class = "uvicorn.workers.UvicornWorker"
workers = int(os.environ.get("WEB_CONCURRENCY", 4))
worker_connections = 1000

# Binding
bind = "0.0.0.0:8000"

# Timeouts
# Tăng lên 120s nếu có endpoint export/report chạy lâu
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 60))
graceful_timeout = 30
keepalive = 5

# Performance
preload_app = True

# Logging — stdout/stderr để container runtime thu thập
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'