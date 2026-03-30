# Hướng dẫn cài đặt Postgres

Cài đặt Postgres bằng Podman.

Tạo volumn:

```bash
podman volume create pgdata
```

Run postgres:

```bash
podman run -d --name postgres -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=dns123 -e POSTGRES_DB=dns -p 5432:5432 -v pgdata:/var/lib/postgresql postgres:18.3
```

Kiểm tra postgres có đang hoạt động:

```bash
podman exec -it postgres psql -U admin -d dns

# thử dụng các lệnh sau để kiểm tra
SELECT version();
SELECT current_database();

\l              # liệt kê danh sách các database
\dt             # liệt kê danh sách các table trong database hiện tại
```