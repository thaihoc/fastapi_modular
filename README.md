# Cấu trúc source code FastAPI

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
│   │   ├── products/        # Module Quản lý sản phẩm
│   │   │   ├── api.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
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

Cài đặt python 3.14 (pip 25.3)

Tạo môi trường ảo:

```bash
python -m venv .venv              # .venv --> Tên của môi trường ảo
source venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows
```

Cài đặt các thư viện python:

```bash
pip install -r requirements.txt
```

Cài đặt postgres bằng podman (nếu chưa có) --> xem hướng dẫn chi tiết tại thư mục docs.

## Hướng dẫn migrate database

Mỗi khi có thay đổi models thực hiện chạy migrate database để update lại CSDL:

```bash
alembic revision --autogenerate -m "init"

alembic upgrade head
```

## Lưu ý

Mỗi lần cài thêm thư viện cần chạy lại lệnh

```bash

```




