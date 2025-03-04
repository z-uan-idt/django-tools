import os
import platform
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTabWidget, QFileDialog
)

from gui.env_tab import EnvTab
from gui.structure_tab import StructureTab
from utils.file_utils import get_current_directory


class EnvSetupApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Set application title
        self.setWindowTitle("Python Django Base Setup")
        self.setGeometry(100, 100, 800, 650)
        self.setMinimumSize(800, 650)
        
        # Xác định hệ điều hành
        self.os_type = platform.system()
        
        # Lưu đường dẫn hiện tại
        self.current_dir = get_current_directory()
        
        # Khởi tạo file_data
        self.file_data = {}
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Tạo giao diện
        self.create_widgets()
    
    def create_widgets(self):
        """Create and arrange UI widgets"""
        # Frame chọn đường dẫn dự án
        project_frame = QWidget()
        project_layout = QHBoxLayout(project_frame)
        project_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setStyleSheet("""
            * {
                line-height: 1;
            } 
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QPushButton {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px 12px;
                background-color: #f5f5f5;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        # Nhãn đường dẫn
        project_layout.addWidget(QLabel("Đường dẫn dự án:"))
        
        # Ô nhập đường dẫn
        self.project_path = QLineEdit(os.getcwd())
        project_layout.addWidget(self.project_path, 1)  # Độ giãn 1
        
        # Nút duyệt
        browse_button = QPushButton("Chọn")
        browse_button.clicked.connect(self.browse_project_path)
        project_layout.addWidget(browse_button)
        
        self.main_layout.addWidget(project_frame)
        
        # Tạo widget tab
        self.tab_widget = QTabWidget()
        
        # Tab Môi trường
        self.env_tab = EnvTab(self.tab_widget, self)
        self.tab_widget.addTab(self.env_tab, "Môi trường")
        
        # Tab Cấu trúc dự án
        self.structure_tab = StructureTab(self.tab_widget, self)
        self.tab_widget.addTab(self.structure_tab, "Cấu trúc dự án")
        
        self.main_layout.addWidget(self.tab_widget, 1)  # Độ giãn 1
    
    def browse_project_path(self):
        """Mở hộp thoại chọn thư mục dự án"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Chọn thư mục dự án",
            self.current_dir
        )
        
        if folder_path:
            self.project_path.setText(folder_path)
            # Cập nhật thư mục làm việc hiện tại
            os.chdir(folder_path)
            
            # Thông báo cho các tab biết đường dẫn đã thay đổi
            self.env_tab.log(f"Đã chọn thư mục dự án: {folder_path}", "info")
            self.structure_tab.update_tree_from_folder()