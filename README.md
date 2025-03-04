# Python Environment Setup

Ứng dụng này giúp tạo và quản lý môi trường Python cũng như cấu trúc dự án Django.

## Tính năng

- Tạo môi trường ảo Python
- Cài đặt các gói từ file requirements.txt
- Tạo cấu trúc dự án Django tự động
- Thêm ứng dụng mới vào dự án Django
- Tự động cập nhật file settings.py

## Cách sử dụng

```bash
python main.py
```

## Cấu trúc dự án

```
project/
├── main.py                  # Điểm vào chính của ứng dụng
├── gui/                     # Thư mục chứa các module giao diện
│   ├── __init__.py
│   ├── app.py               # Class EnvSetupApp chính
│   ├── env_tab.py           # Tab môi trường
│   └── structure_tab.py     # Tab cấu trúc dự án
└── utils/                   # Thư mục chứa các tiện ích
    ├── __init__.py
    ├── file_utils.py        # Các hàm làm việc với file
    └── project_utils.py     # Các hàm làm việc với dự án Django
```

## Yêu cầu

- Python 3.6 trở lên
- tkinter (thường đã được cài đặt sẵn với Python)

## Ghi chú

- Để thêm ứng dụng mới, hãy nhập tên ứng dụng và nhấn nút "Thêm"
- Các file sẽ được tạo tự động trong thư mục apps của dự án
- Ứng dụng cũng sẽ tự động cập nhật INSTALLED_APPS trong settings.py
