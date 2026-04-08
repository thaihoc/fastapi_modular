# Cấu trúc source code FastAPI

Các tính năng chính:

* [x] Cấu trúc thư mục theo hướng modular (module-based)
* [x] Logger hỗ trợ debug/trace (sử dụng logging của Python)
* [x] Tự động sinh ra API docs (/docs)
* [x] Database migration với Postgres (sử dụng Alembic)
* [x] Tự động register routers
* [x] Xác thực REST APIs bằng JWT
* [x] Cache với Redis (mặc định dùng InMemory)
* [ ] Kiểm tra quyền với nhiều giải pháp RBAC, ABAC và ACL (sử dụng Casbin)
* [x] Hướng dẫn cài đặt chuẩn production


Cấu trúc thư mục:

```plaintext
.
├── app/
│   ├── main.py              # Entry point: Khởi tạo FastAPI & kết nối các module
│   ├── core/                # Các thiết lập dùng chung cho toàn bộ App
│   │   ├── config.py        # Quản lý biến môi trường (pydantic-settings)
│   │   ├── security.py      # Hashing password, JWT logic
│   │   └── exceptions.py    # Custom Exception handlers
│   ├── db/                  # Các thiết lập dùng chung cho toàn bộ App
│   │   ├── base.py          # Quản lý các models trong database
│   │   └── session.py       # Tạo kết nối database
│   │
│   ├── modules/             # <--- Danh sách các Module nghiệp vụ
│   │   ├── users/           # Module Quản lý người dùng
│   │   │   ├── api.py       # Các route: /users/me, /users/{id}
│   │   │   ├── models.py    # Bảng User trong Database --> giống Entity
│   │   │   ├── schemas.py   # Pydantic (UserCreate, UserRead) --> giống DTO
│   │   │   ├── service.py   # Logic: register_user, get_user_by_email
│   │   │   ├── repo.py      # Truy vấn database (Repository)
│   │   │   └── deps.py      # Dependencies riêng (ví dụ: get_current_user)
│   │   │
│   │   ├── clients/        # Module Quản lý sản phẩm
│   │   │   ├── api.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py   
│   │   │   ├── repo.py      
│   │   │   └── deps.py      
│   │
│   └── shared/              # Utils, Helpers dùng chung (gửi mail, upload file)
│       └── utils.py
│
├── alembic/                 # Thư mục quản lý phiên bản DB (Alembic)
├── tests/                   # Thư mục chứa các bài kiểm tra (Pytest)
├── .env                     # Lưu SECRET_KEY, DATABASE_URL...
├── Dockerfile               # Cấu hình đóng gói ứng dụng
└── requirements.txt         # Danh sách thư viện
```

## Hướng dẫn setup project lần đầu

Bước 1: Cài đặt python 3.14+ (pip 25+).

Bước 2: Tạo môi trường ảo python cho project:

```bash
python -m venv .venv              # .venv --> Tên của môi trường ảo
```

Chuyển đến môi trường ảo:

```bash
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows
```

Bước 3: Cài đặt các thư viện python:

```bash
pip install -r requirements.txt
```

Bước 4: Tạo file cấu hình .env với nội dung sau:

```bash
APP_NAME=FastAPI Modular Tempate
DEBUG=True

DB_URL=postgresql://lx360u:lx360p@localhost:5432/lx360db
REDIS_URL=redis://localhost:6379/0
```

Bước 5: Thực hiện migrate database

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

Ghi chú: Tham khảo cài đặt postgres bằng podman (nếu chưa có) chi tiết tại thư mục docs.

## Hướng dẫn làm việc với project

Luôn luôn sử dụng môi trường ảo của python khi làm việc.

Mỗi khi có thay đổi models thực hiện chạy migrate database để update lại CSDL:

```bash
alembic revision --autogenerate -m "them bang luu danh muc chuc vu"
alembic upgrade head
```

Mỗi khi có thêm mới, nâng cấp hoặc xoá thư viện hãy update lại file requirements.txt bằng lệnh:

```bash
pip freeze > requirements.txt
```

Chạy ứng dụng:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000

# tự động reload lại ứng dụng khi code thay đổi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Hướng dẫn build và cài đặt với Podman

Build image:

```bash
podman build -t fastapi-template:v1 .
```

Run ứng dụng:

```bash
podman run -d --network dns 
    --name fastapi-template 
    -p 8000:8000
    -e PROJECT_NAME="FastAPI Modular Tempate"
    -e DEBUG=True
    -e LOG_LEVEL=DEBUG
    -e DB_URL=postgresql://lx360u:lx360p@postgres:5432/lx360db
    -e REDIS_CACHE_URL=redis://redis:6379
    -e AUTH_JWKS=http://keycloak:8080/realms/master/protocol/openid-connect/certs
    fastapi-template:v1
```

Truy cập vào URL sau để kiểm tra ứng dụng đã run thành công: http://localhost:8000