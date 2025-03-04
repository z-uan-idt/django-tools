# Python Environment and Django Project Setup (PyQt6 Version)

Ứng dụng này giúp tạo và quản lý môi trường Python cũng như cấu trúc dự án Django với giao diện người dùng sử dụng PyQt6.

## Tính năng

- Tạo môi trường ảo Python
- Cài đặt các gói từ file requirements.txt
- Tạo cấu trúc dự án Django tự động
- Thêm ứng dụng mới vào dự án Django
- Tự động cập nhật file settings.py
- Giao diện người dùng hiện đại với PyQt6

## Cài đặt

### Yêu cầu:
- Python 3.6 trở lên
- PyQt6

```bash
pip install pyqt6
```

### Chạy từ mã nguồn:

```bash
python main.py
```

### Cách tạo tệp thực thi:

#### Windows:
```bash
build.bat
```

#### macOS/Linux:
```bash
chmod +x build.sh
./build.sh
```

## Cấu trúc dự án

```
project/
├── main.py                      # Điểm vào chính của ứng dụng
│
├── gui/                         # Thư mục chứa các module giao diện 
│   ├── __init__.py
│   ├── app.py                   # Class EnvSetupApp chính
│   ├── env_tab.py               # Tab môi trường
│   └── structure_tab.py         # Tab cấu trúc dự án
│
└── utils/                       # Thư mục chứa các tiện ích
    ├── __init__.py
    ├── file_utils.py            # Các hàm làm việc với file
    └── project_utils.py         # Các hàm làm việc với dự án Django
```

## Sử dụng

1. Chọn đường dẫn dự án bằng nút "Browse"
2. Sử dụng tab "Environment" để tạo và quản lý môi trường ảo Python
3. Sử dụng tab "Project Structure" để tạo và quản lý cấu trúc dự án Django

### Tab Environment

- Nhập tên môi trường (mặc định là `.pyenv`)
- Nhấn "Create Environment" để tạo môi trường ảo mới
- Nhấn "Install requirements.txt" để cài đặt các gói từ file requirements.txt

### Tab Project Structure

- Nhập tên ứng dụng và tên hiển thị 
- Nhấn "Add" để tạo ứng dụng mới
- Cấu trúc thư mục sẽ được tạo tự động và cập nhật trong cây thư mục
- Chọn các file trong cây thư mục để xem nội dung

## Ghi chú

- Ứng dụng này sử dụng PyQt6 thay vì Tkinter để cung cấp giao diện người dùng hiện đại hơn
- Các file sẽ được tạo tự động trong thư mục apps của dự án
- Ứng dụng cũng sẽ tự động cập nhật INSTALLED_APPS trong settings.py

## Những thay đổi từ phiên bản Tkinter

- Giao diện người dùng hiện đại hơn với PyQt6
- Tăng khả năng phản hồi với việc thực hiện tác vụ nặng trong luồng riêng biệt
- Cải thiện xử lý lỗi và thông báo
- Giao diện nhất quán hơn trên các hệ điều hành khác nhau