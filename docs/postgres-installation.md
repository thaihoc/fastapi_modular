# Hướng dẫn cài đặt Postgres

Cài đặt Postgres bằng Podman phục vụ môi trường dev.

# Hướng dẫn cài đặt

Tạo network nếu chưa có:

```bash
podman network create dns
```

Tạo volumn:

```bash
podman volume create pgdata
```

Run postgres:

```bash
podman run -d
    --name postgres
    --network dns
    -e POSTGRES_USER=admin
    -e POSTGRES_PASSWORD=dns123
    -e POSTGRES_DB=dns
    -p 5432:5432
    -v pgdata:/var/lib/postgresql
    postgres:18.3
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

# Hướng dẫn tạo user và database cho ứng dụng

Mặc định, chúng ta không nên dùng user admin cho ứng dụng. Hãy tạo user và database riêng cho ứng dụng như sau:

```sql
-- Đăng nhập bằng tài khoản admin phía trên và thực hiện các lệnh bên dưới
CREATE USER lx360u WITH PASSWORD 'lx360p';

CREATE DATABASE lx360db OWNER lx360u;

GRANT CONNECT ON DATABASE lx360db TO lx360u;
GRANT USAGE ON SCHEMA public TO lx360u;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO lx360u;

-- Cho phép quyền trên table tạo mới sau này
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO lx360u;
```

Chuỗi kết nối cập nhật vào ứng dụng theo định dạng sau:

```
DB_URL=postgresql://lx360u:lx360p@localhost:5432/lx360db

podman exec -it postgres psql -U lx360u -d lx360db
```