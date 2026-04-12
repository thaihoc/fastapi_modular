# Hướng dẫn cài đặt Redis

Hướng dẫn cài đặt Redis cho môi trường dev.

Tạo network nếu chưa có:

```bash
podman network create dns
```

Tạo volumne lưu data:

```bash
podman volume create redis-data
```

Run Redis:

```bash
podman run -d
  --name redis
  --network dns
  -p 6379:6379
  -v redis-data:/data
  docker.io/redis:alpine
```

Kiểm tra Redis đã cài thành công:

```bash
# Kết nối vào redis-cli
podman exec -it redis redis-cli

# Test ping
127.0.0.1:6379> PING
# → PONG
```