import os
import sys
from PyQt6.QtCore import Qt
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
    app.setApplicationName("Python Django Base Setup")
    app.setApplicationDisplayName("Python Django Base Setup")

    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"
    
    # Optional: If available, use screen scaling
    try:
        app.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except AttributeError:
        pass
    
    # Kiểm tra PyQt6 đã cài đặt
    try:
        from PyQt6 import QtCore
    except ImportError:
        QMessageBox.critical(None, "Lỗi", "PyQt6 chưa được cài đặt. Vui lòng cài đặt bằng lệnh: pip install pyqt6")
        sys.exit(1)
    
    # Khởi tạo và hiển thị cửa sổ chính
    window = EnvSetupApp()
    
    # Get the screen geometry
    screen = app.primaryScreen()
    screen_geometry = screen.geometry()
    
    # Scale window based on screen size
    window.resize(
        int(screen_geometry.width() * 0.8),  # 80% of screen width
        int(screen_geometry.height() * 0.8)  # 80% of screen height
    )
    
    # Center the window
    frame_geometry = window.frameGeometry()
    center_point = screen_geometry.center()
    frame_geometry.moveCenter(center_point)
    window.move(frame_geometry.topLeft())
    window.show()
    
    # Khởi chạy vòng lặp sự kiện
    sys.exit(app.exec())