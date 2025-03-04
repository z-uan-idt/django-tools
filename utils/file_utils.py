import os
import platform

def get_current_directory():
    """Trả về đường dẫn thư mục hiện tại"""
    return os.getcwd()

def create_directory(path):
    """Tạo thư mục nếu chưa tồn tại"""
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return False

def create_file(path, content=""):
    """Tạo file với nội dung chỉ định"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True

def read_file(path):
    """Đọc nội dung từ file"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Lỗi khi đọc file {path}: {str(e)}")
        return None

def file_exists(path):
    """Kiểm tra xem file có tồn tại không"""
    return os.path.exists(path) and os.path.isfile(path)

def get_activate_command(venv_name):
    """Trả về lệnh kích hoạt môi trường ảo dựa trên hệ điều hành"""
    os_type = platform.system()
    if os_type == "Windows":
        return f".\\{venv_name}\\Scripts\\Activate.ps1"
    else:  # macOS/Linux
        return f"source ./{venv_name}/bin/activate"