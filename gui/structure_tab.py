import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTreeWidget, QTreeWidgetItem, QTextEdit,
    QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt

from utils.project_utils import update_settings_file, create_django_app_files


class StructureTab(QWidget):
    """Tab for managing Django project structure"""
    
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        
        # Định nghĩa cấu trúc ứng dụng tiêu chuẩn
        self.app_structure = {
            "__init__.py": "",
            "admin.py": "",
            "apps.py": "",
            "urls.py": "",
            "dirs": ["docs", "migrations", "models", "serializers", "services", "views"]
        }
        
        self.build_ui()
        self.initialize_tree_structure()
    
    def build_ui(self):
        # Layout chính
        layout = QVBoxLayout(self)
        
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
        
        # Frame nhập liệu ứng dụng
        app_input_layout = QHBoxLayout()
        
        # Nhập tên ứng dụng
        app_input_layout.addWidget(QLabel("Tên ứng dụng:"))
        self.new_app_name = QLineEdit()
        app_input_layout.addWidget(self.new_app_name)
        
        # Nhập tên hiển thị
        app_input_layout.addWidget(QLabel("Tên hiển thị:"))
        self.verbose_name = QLineEdit()
        app_input_layout.addWidget(self.verbose_name)
        
        # Nút thêm
        add_app_button = QPushButton("Thêm")
        add_app_button.clicked.connect(self.add_new_app)
        app_input_layout.addWidget(add_app_button)
        
        layout.addLayout(app_input_layout)
        
        # Splitter cho cây và nội dung
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Bên trái - cấu trúc cây
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        
        tree_layout.addWidget(QLabel("Cấu trúc dự án:"))
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)  # Ẩn tiêu đề
        self.tree.itemSelectionChanged.connect(self.on_tree_select)
        tree_layout.addWidget(self.tree)
        
        # Bên phải - nội dung file
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        content_layout.addWidget(QLabel("Nội dung file:"))
        
        self.file_content = QTextEdit()
        self.file_content.setReadOnly(True)  # Chỉ đọc
        content_layout.addWidget(self.file_content)
        
        # Thêm widget vào splitter
        splitter.addWidget(tree_widget)
        splitter.addWidget(content_widget)
        splitter.setSizes([200, 400])  # Thiết lập kích thước ban đầu
        
        layout.addWidget(splitter, 1)  # Làm cho splitter chiếm không gian có sẵn
        
        # Nút làm mới
        refresh_frame = QHBoxLayout()
        refresh_button = QPushButton("Làm mới")
        refresh_button.clicked.connect(self.update_tree_from_folder)
        refresh_frame.addStretch()
        refresh_frame.addWidget(refresh_button)
        
        layout.addLayout(refresh_frame)
    
    def initialize_tree_structure(self):
        """Khởi tạo cấu trúc cây với 'apps' làm gốc"""
        # Xóa tất cả các nút hiện tại
        self.tree.clear()
        
        # Tạo nút gốc 'apps'
        self.apps_item = QTreeWidgetItem(self.tree, ["apps"])
        self.apps_item.setExpanded(True)
        
        # Kiểm tra đường dẫn dự án
        project_path = self.app.project_path.text().strip()
        if os.path.exists(project_path):
            # Nếu đường dẫn tồn tại, quét thư mục apps để lấy danh sách ứng dụng
            apps_path = os.path.join(project_path, "apps")
            if os.path.exists(apps_path) and os.path.isdir(apps_path):
                self.update_tree_from_folder()
    
    def create_app_node(self, app_name):
        """Tạo nút ứng dụng trong cấu trúc cây"""
        # Tạo nút ứng dụng
        app_item = QTreeWidgetItem(self.apps_item, [app_name])
        
        # Tạo các thư mục con tiêu chuẩn cho Django
        dirs = ["docs", "migrations", "models", "serializers", "services", "views"]
        dir_nodes = {}
        
        for dir_name in dirs:
            dir_node = QTreeWidgetItem(app_item, [dir_name])
            dir_nodes[dir_name] = dir_node
            
        # Tạo các file cơ bản cho ứng dụng
        QTreeWidgetItem(app_item, ["__init__.py"])
        self.app.file_data[f"apps/{app_name}/__init__.py"] = ""
        
        QTreeWidgetItem(app_item, ["admin.py"])
        self.app.file_data[f"apps/{app_name}/admin.py"] = ""
        
        QTreeWidgetItem(app_item, ["apps.py"])
        self.app.file_data[f"apps/{app_name}/apps.py"] = ""
        
        QTreeWidgetItem(app_item, ["urls.py"])
        self.app.file_data[f"apps/{app_name}/urls.py"] = ""
        
        return app_item
    
    def add_new_app(self):
        """Thêm ứng dụng Django mới"""
        # Lấy tên ứng dụng từ input
        app_name = self.new_app_name.text().strip()
        verbose_name = self.verbose_name.text().strip()

        # Kiểm tra tên ứng dụng
        if not app_name:
            QMessageBox.critical(self, "Lỗi", "Vui lòng nhập tên ứng dụng")
            return
            
        # Kiểm tra tên ứng dụng hợp lệ
        if not app_name.isalnum() and not app_name.isidentifier():
            QMessageBox.critical(self, "Lỗi", "Tên ứng dụng không hợp lệ. Chỉ được phép sử dụng chữ cái, số và dấu gạch dưới.")
            return
            
        # Kiểm tra xem ứng dụng đã tồn tại chưa
        for i in range(self.apps_item.childCount()):
            app_item = self.apps_item.child(i)
            if app_item.text(0) == app_name:
                QMessageBox.critical(self, "Lỗi", f"Ứng dụng '{app_name}' đã tồn tại.")
                return
        
        # Sử dụng tên ứng dụng làm tên hiển thị nếu không có
        if not verbose_name:
            verbose_name = app_name.capitalize()
            
        # Tạo nút ứng dụng mới trong cây
        app_item = self.create_app_node(app_name)
        
        # Tạo thư mục và file thực sự trên đĩa nếu đường dẫn dự án đã được chọn
        project_path = self.app.project_path.text().strip()
        if os.path.exists(project_path):
            try:
                # Tạo thư mục ứng dụng và cấu trúc
                create_django_app_files(project_path, app_name, verbose_name)
                
                # Cập nhật file settings.py để thêm ứng dụng vào INSTALLED_APPS
                update_settings_file(project_path, app_name)
                
                # Xóa giá trị trong ô nhập liệu
                self.new_app_name.setText("")
                self.verbose_name.setText("")
                
                # Cập nhật lại cây từ thư mục
                self.update_tree_from_folder()
                
                QMessageBox.information(self, "Thành công", f"Đã tạo ứng dụng '{app_name}' thành công")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi tạo thư mục và file cho ứng dụng '{app_name}': {str(e)}")
    
    def on_tree_select(self):
        """Xử lý khi chọn item trên cây"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
            
        selected_item = selected_items[0]
        
        # Xây dựng đường dẫn từ item đã chọn đến root
        path = []
        item = selected_item
        
        # Duyệt từ item được chọn lên các nút cha
        while item is not None:
            path.insert(0, item.text(0))
            item = item.parent()
        
        # Tạo đường dẫn file
        file_path = "/".join(path)
        
        # Xóa nội dung hiện tại
        self.file_content.clear()
        
        # Hiển thị đường dẫn tới file
        self.file_content.append(f"Đường dẫn: {file_path}\n")
        
        # Kiểm tra xem đây có phải là file không
        project_path = self.app.project_path.text()
        full_path = os.path.join(project_path, file_path)
        
        if os.path.isfile(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if content.strip():  # Nếu file có nội dung
                    self.file_content.append(content)
                else:  # Nếu file rỗng
                    self.file_content.append("File rỗng")
            except Exception as e:
                self.file_content.append(f"Không thể đọc file: {str(e)}")
        elif file_path in self.app.file_data:  # Fallback nếu không đọc được từ đĩa
            self.file_content.append("File rỗng")
        else:  # Nếu là thư mục
            self.file_content.append("Đây là thư mục")
    
    def update_tree_from_folder(self):
        """Cập nhật cấu trúc cây dựa trên thư mục thực tế"""
        project_path = self.app.project_path.text()
        apps_path = os.path.join(project_path, "apps")
        
        # Nếu thư mục apps không tồn tại, giữ nguyên cấu trúc mẫu
        if not os.path.exists(apps_path) or not os.path.isdir(apps_path):
            return
            
        # Xóa tất cả nút hiện tại
        self.tree.clear()
            
        # Khởi tạo lại file_data
        self.app.file_data = {}
            
        # Tạo nút gốc apps
        self.apps_item = QTreeWidgetItem(self.tree, ["apps"])
        self.apps_item.setExpanded(True)
        
        # Lấy danh sách các thư mục ứng dụng
        apps = []
        for item in os.listdir(apps_path):
            item_path = os.path.join(apps_path, item)
            if os.path.isdir(item_path) and not item.startswith('__') and not item.startswith('.'):
                apps.append(item)
                
        # Tạo nút cho mỗi ứng dụng
        for app_name in sorted(apps):
            app_path = os.path.join(apps_path, app_name)
            app_item = QTreeWidgetItem(self.apps_item, [app_name])
            
            # Quét đệ quy thư mục ứng dụng
            self.scan_directory(app_path, app_item, f"apps/{app_name}")
    
    def scan_directory(self, directory_path, parent_node, relative_path):
        """Quét đệ quy một thư mục và thêm các nút vào cây"""
        
        # Đầu tiên thêm tất cả các file
        files = []
        subdirs = []
        
        # Lấy danh sách các file và thư mục con
        try:
            for item in os.listdir(directory_path):
                if item.startswith('__pycache__') or item.startswith('.'):
                    continue
                    
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    files.append(item)
                elif os.path.isdir(item_path):
                    subdirs.append(item)
        except Exception:
            return
        
        # Thêm các file Python trước
        for file_name in sorted(files):
            if file_name.endswith('.py'):
                QTreeWidgetItem(parent_node, [file_name])
                self.app.file_data[f"{relative_path}/{file_name}"] = ""
        
        # Sau đó thêm các file không phải Python
        for file_name in sorted(files):
            if not file_name.endswith('.py'):
                QTreeWidgetItem(parent_node, [file_name])
                self.app.file_data[f"{relative_path}/{file_name}"] = ""
        
        # Cuối cùng thêm các thư mục con và quét đệ quy
        for subdir in sorted(subdirs):
            subdir_path = os.path.join(directory_path, subdir)
            subdir_node = QTreeWidgetItem(parent_node, [subdir])
            self.scan_directory(subdir_path, subdir_node, f"{relative_path}/{subdir}")