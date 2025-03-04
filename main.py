import os
import sys
import platform
from PyQt6.QtWidgets import QApplication, QMessageBox

# Import các module tự tạo
from gui.app import EnvSetupApp

if __name__ == "__main__":
    # Kiểm tra phiên bản Python
    if sys.version_info < (3, 6):
        print("Lỗi: Ứng dụng yêu cầu Python 3.6 trở lên")
        sys.exit(1)

    # Khởi tạo ứng dụng QApplication
    app = QApplication(sys.argv)
    
    # Kiểm tra PyQt6 đã cài đặt
    try:
        from PyQt6 import QtCore
    except ImportError:
        QMessageBox.critical(None, "Lỗi", "PyQt6 chưa được cài đặt. Vui lòng cài đặt bằng lệnh: pip install pyqt6")
        sys.exit(1)
    
    # Khởi tạo và hiển thị cửa sổ chính
    window = EnvSetupApp()
    window.show()
    
    # Khởi chạy vòng lặp sự kiện
    sys.exit(app.exec())