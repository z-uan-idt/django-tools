import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTreeWidget, QTreeWidgetItem, QTextEdit,
    QSplitter, QFrame, QGridLayout, QScrollArea, QComboBox
)
from PyQt6.QtCore import Qt
from utils.file_utils import create_file, read_file
from utils.highlighter import PythonCodeEditor, PythonSyntaxHighlighter
from utils.project_utils import update_settings_file, create_django_app_files


def firstupper(value: str):
    try:
        return value[0].upper() + value[1:]
    except:
        return value

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
        layout = QVBoxLayout(self)
        
        # Frame nhập liệu ứng dụng
        app_input_layout = QHBoxLayout()
        
        # Nhập tên ứng dụng
        self._new_app_name = ""
        self.new_app_name = QLineEdit()
        self.new_app_name.setPlaceholderText("App name")
        self.new_app_name.setEnabled(False)
        self.new_app_name.textChanged.connect(self.on_new_app_name_change)
        app_input_layout.addWidget(self.new_app_name)
        
        # Nhập tên hiển thị
        self._verbose_name = ""
        self.verbose_name = QLineEdit()
        self.verbose_name.setPlaceholderText("App display name")
        self.verbose_name.setEnabled(False)
        self.verbose_name.textChanged.connect(self.on_verbose_name_change)
        app_input_layout.addWidget(self.verbose_name)
        
        # Nút thêm
        self.add_app_button = QPushButton("Add")
        self.add_app_button.setMinimumWidth(140)
        self.add_app_button.setEnabled(False)
        self.add_app_button.clicked.connect(self.add_new_app)
        app_input_layout.addWidget(self.add_app_button)
        
        layout.addLayout(app_input_layout)
        
        # Splitter cho cây và nội dung
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Bên trái - cấu trúc cây
        self.tree_widget = QWidget()
        tree_layout = QVBoxLayout(self.tree_widget)
        self.tree_widget.setVisible(False)
        tree_layout.setContentsMargins(0, 0, 5, 0)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)  # Ẩn tiêu đề
        self.tree.itemSelectionChanged.connect(self.on_tree_select)
        
        # Nút làm mới
        refresh_frame = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh project structure")
        self.refresh_button.setVisible(False)
        self.refresh_button.clicked.connect(lambda x: self.update_tree_from_folder(is_reload=True))
        
        # Bên phải - chức năng
        feature_widget = QWidget()
        feature_layout = QVBoxLayout(feature_widget)
        feature_layout.setContentsMargins(0, 0, 0, 0)

        # Frame các nút chức năng
        function_frame = QFrame()
        function_layout = QGridLayout(function_frame)
        function_layout.setContentsMargins(0, 0, 0, 0)
        
        # Nút tạo model
        create_model_btn = QPushButton("Create Model")
        create_model_btn.setEnabled(False)
        create_model_btn.clicked.connect(self.toggle_model_form)
        function_layout.addWidget(create_model_btn, 0, 0)
        self.create_model_btn = create_model_btn
        
        # Nút tạo view
        create_view_btn = QPushButton("Create View")
        create_view_btn.setEnabled(False)
        create_view_btn.clicked.connect(self.show_create_view_dialog)
        function_layout.addWidget(create_view_btn, 0, 1)
        self.create_view_btn = create_view_btn
        
        # Nút tạo serializer
        create_serializer_btn = QPushButton("Create Serializer")
        create_serializer_btn.setEnabled(False)
        create_serializer_btn.clicked.connect(self.show_create_serializer_dialog)
        function_layout.addWidget(create_serializer_btn, 1, 0)
        self.create_serializer_btn = create_serializer_btn
        
        # Nút tạo URL
        create_url_btn = QPushButton("Create URL")
        create_url_btn.setEnabled(False)
        create_url_btn.clicked.connect(self.show_create_url_dialog)
        function_layout.addWidget(create_url_btn, 1, 1)
        self.create_url_btn = create_url_btn
        
        self.model_form_ui(feature_layout)
        
        self.file_content = PythonCodeEditor()
        self.file_content.setReadOnly(True)
        self.file_content.setVisible(False)

        feature_layout.addWidget(self.file_content)

        tree_layout.addWidget(function_frame)

        tree_layout.addWidget(self.tree)
        
        refresh_frame.addWidget(self.refresh_button)
    
        tree_layout.addLayout(refresh_frame)
        
        # Thêm widget vào splitter
        splitter.addWidget(self.tree_widget)
        splitter.addWidget(feature_widget)
        splitter.setSizes([120, 1580])  # Thiết lập kích thước ban đầu
        
        layout.addWidget(splitter, 1)  # Làm cho splitter chiếm không gian có sẵn
        
        # Khu vực nhật ký
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(150)
        
        layout.addWidget(self.log_text)

    def model_form_ui(self, feature_layout: QVBoxLayout):
        # Model form (initially hidden)
        self.model_form_frame = QFrame()
        model_form_layout = QVBoxLayout(self.model_form_frame)
        model_form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Model name input
        model_name_layout = QHBoxLayout()
        
        # Model name input
        self.model_abstract = QComboBox()
        self.model_abstract.setPlaceholderText("Model abstract")
        self.model_abstract.addItems(["BaseModel", "BaseModelSoftDelete", "models.Model"])
        self.model_abstract.setMinimumWidth(250)
        self.model_abstract.setCurrentIndex(0)
        model_name_layout.addWidget(self.model_abstract)

        self.model_name_input = QLineEdit()
        self.model_name_input.setPlaceholderText("Model name")
        model_name_layout.addWidget(self.model_name_input)
        
        # Model name input
        self.model_vn_name_input = QLineEdit()
        self.model_vn_name_input.setPlaceholderText("Model display name")
        model_name_layout.addWidget(self.model_vn_name_input)
        
        # Add field button
        add_field_btn = QPushButton("Add model field")
        add_field_btn.clicked.connect(self.add_field_row)
        model_name_layout.addWidget(add_field_btn)

        model_form_layout.addLayout(model_name_layout)
        
        # Create a container for the scrollable content
        scroll_container = QWidget()
        scroll_container_layout = QVBoxLayout(scroll_container)
        scroll_container_layout.setContentsMargins(0, 0, 0, 0)
        scroll_container_layout.setSpacing(0)

        # Fields container within scroll area
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_container)
        self.fields_layout.setContentsMargins(0, 5, 0, 5)
        self.fields_layout.setSpacing(10)

        # Add the first empty field row by default
        self.field_rows = []

        # Add fields container to scroll container
        scroll_container_layout.addWidget(self.fields_container)
        scroll_container_layout.addStretch(1)  # This pushes everything above it to the top
        
        # Scroll area for fields
        fields_scroll = QScrollArea()
        fields_scroll.setWidgetResizable(True)
        fields_scroll.setWidget(scroll_container)
        fields_scroll.setFrameShape(QFrame.Shape.NoFrame)
        fields_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        fields_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        model_form_layout.addWidget(fields_scroll)
        
        # Buttons
        model_buttons_layout = QHBoxLayout()
        create_model_confirm_btn = QPushButton("Create model")
        create_model_confirm_btn.clicked.connect(self.confirm_create_model)
        cancel_model_btn = QPushButton("Cancel")
        cancel_model_btn.clicked.connect(self.hide_model_form)
        model_buttons_layout.addWidget(create_model_confirm_btn)
        model_buttons_layout.addWidget(cancel_model_btn)
        model_form_layout.addLayout(model_buttons_layout)
        
        # Add form to layout but hide it initially
        self.model_form_frame.setVisible(False)
        
        feature_layout.addWidget(self.model_form_frame)
    
    def add_field_row(self):
        """Add a new field row to the fields container"""
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        # Field name
        field_name = QLineEdit()
        field_name.setMaximumWidth(250)
        field_name.setPlaceholderText("Field name")
        
        # Field type dropdown
        field_type = QComboBox()
        field_type.setMinimumWidth(250)
        self.populate_field_types(field_type)
        field_type.currentIndexChanged.connect(lambda idx, ft=field_type: self.on_field_type_changed(ft))
        
        # Options
        field_options = QLineEdit()
        field_options.setText("max_length=255, null=True, blank=True")
        
        # ForeignKey dropdown
        foreign_key = QComboBox()
        foreign_key.setEnabled(False)
        foreign_key.setMinimumWidth(250)
        self.populate_model_classes(foreign_key)
        
        # Add to row
        row_layout.addWidget(field_name)
        row_layout.addWidget(field_type)
        row_layout.addWidget(field_options)
        row_layout.addWidget(foreign_key)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setFixedWidth(120)
        delete_btn.clicked.connect(lambda: self.delete_field_row(row))
        row_layout.addWidget(delete_btn)
        
        # Store references to the widgets
        row_data = {
            "widget": row,
            "name": field_name,
            "type": field_type,
            "options": field_options,
            "foreign_key": foreign_key
        }
        self.field_rows.append(row_data)
        
        # Add to layout
        self.fields_layout.addWidget(row)

        return row_data

    def delete_field_row(self, row):
        """Delete a field row from the container"""
        # Find the row data
        row_data = None
        for i, data in enumerate(self.field_rows):
            if data["widget"] == row:
                row_data = data
                self.field_rows.pop(i)
                break
        
        if row_data:
            # Remove widget
            self.fields_layout.removeWidget(row_data["widget"])
            row_data["widget"].deleteLater()

    def populate_field_types(self, combo_box):
        """Populate the field type dropdown with Django model field types"""
        field_types = [
            "CharField", "TextField", "IntegerField", "BooleanField", 
            "DateField", "DateTimeField", "EmailField", "URLField",
            "DecimalField", "FloatField", "ForeignKey", "OneToOneField",
            "ManyToManyField", "FileField", "ImageField", "JSONField"
        ]
        
        for field_type in field_types:
            combo_box.addItem(field_type)

    def populate_model_classes(self, combo_box):

        """Populate the combo box with available model classes"""
        combo_box.clear()
        combo_box.addItem("-- ForeignKey --")
        
        # Get project path
        project_path = self.app.project_path.text().strip()
        if not project_path:
            return
        
        # Get apps directory
        apps_path = os.path.join(project_path, "apps")
        if not os.path.exists(apps_path) or not os.path.isdir(apps_path):
            return
        
        # Scan each app for models
        for app_name in os.listdir(apps_path):
            app_dir = os.path.join(apps_path, app_name)
            
            if not os.path.isdir(app_dir) or app_name.startswith('.') or app_name.startswith('__'):
                continue
            
            # Check models directory
            models_dir = os.path.join(app_dir, "models")
            if os.path.exists(models_dir) and os.path.isdir(models_dir):
                # Scan models directory
                for model_file in os.listdir(models_dir):
                    if model_file.endswith('.py') and not model_file.startswith('__'):
                        model_name = os.path.splitext(model_file)[0]
            
                        # Try to parse models.py to find model classes
                        model_content_file = os.path.join(models_dir, model_file)
                        try:
                            with open(model_content_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Simple regex to find class definitions
                                import re
                                pattern = r'^class\s+(\w+)\s*\([^)]+\)'
                                matches = re.findall(pattern, content, re.MULTILINE)
                                for match in matches:
                                    combo_box.addItem(f"{app_name}.models.{model_name}.{match}")
                        except Exception as e:
                            print(f"Error parsing models.py in {app_name}: {str(e)}")

    def on_field_type_changed(self, field_type_combo):
        """Handle field type change to enable/disable foreign key dropdown"""
        current_text = field_type_combo.currentText()
        model_name = self.model_name_input.text().strip()
        model_name_capitalize = firstupper(model_name)
        
        # Find the row data for this combo box
        row_data = None
        for data in self.field_rows:
            if data["type"] == field_type_combo:
                row_data = data
                break
        
        if row_data:
            # Enable foreign key dropdown only for relationship fields
            is_relation = current_text in ["ForeignKey", "OneToOneField", "ManyToManyField"]
            row_data["foreign_key"].setEnabled(is_relation)
            if not is_relation:
                self.populate_model_classes(row_data["foreign_key"])
            
            # Update options placeholder based on field type
            if current_text == "CharField":
                row_data["options"].setText("max_length=255, null=True, blank=True")
            elif current_text == "DecimalField":
                row_data["options"].setText("max_digits=10, decimal_places=2")
            elif current_text in ["ForeignKey", "OneToOneField", "ManyToManyField"]:
                field_name = row_data["name"].text().strip()
                row_data["options"].setText(f"on_delete=models.CASCADE, related_name='{model_name_capitalize}_{field_name}'")
            else:
                row_data["options"].setText("null=True, blank=True")

    def confirm_create_model(self):
        """Create model with the fields from the form"""
        model_name = self.model_name_input.text().strip()
        
        if not model_name:
            self.log("Please enter model name", "error")
            return
        
        project_path = self.app.project_path.text().strip()
        models_dir = os.path.join(project_path, "apps", self.selected_app_name, "models", f"{model_name}.py")
        
        if os.path.exists(models_dir):
            self.log(f"Model {model_name} already exists", "error")
            return
        
        # Collect field data
        fields = []
        error_count = 0

        for index, row_data in enumerate(self.field_rows):
            field_name = row_data["name"].text().strip()
            field_type = row_data["type"].currentText()
            field_options = row_data["options"].text().strip()
            foreign_key = row_data["foreign_key"].currentText() if row_data["foreign_key"].isEnabled() else ""
            
            if not field_name or (field_name and not field_name.strip()):
                self.log(f"Please enter field name: Field Items Index [{index}]", "error")
                error_count += 1
            
            if field_type in ["ForeignKey", "OneToOneField", "ManyToManyField"] and foreign_key == "-- ForeignKey --":
                self.log(f"Please select foreign key for field \"{field_name or index}\"", "error")
                error_count += 1
            
            if field_name:  # Only include fields with names
                fields.append({
                    "name": field_name,
                    "type": field_type,
                    "options": field_options,
                    "foreign_key": foreign_key if foreign_key != "-- ForeignKey --" else ""
                })
        
        if not fields:
            self.log(f"Please create at least 1 model field", "error")
            return

        if error_count > 0:
            return
        
        model_code = self.generate_model_code(model_name, fields)
        
        # Create the model file
        self.create_model_with_fields(self.selected_app_name, model_name, model_code)
        
        # Hide the form
        self.hide_model_form()

    def generate_model_code(self, model_name, fields):
        """Generate Django model class code with the specified fields"""
        imports = set(["from django.db import models"])
        model_name_capitalize = firstupper(model_name)
        model_vn_name = self.model_vn_name_input.text().strip()
        model_abstract = self.model_abstract.currentText().strip()
        
        if model_abstract in ("BaseModel", "BaseModelSoftDelete"):
            imports.add(f"from utils.base_models import {model_abstract}")
        
        # Create class definition and docstring
        model_code = f"\nclass {model_name_capitalize}({model_abstract}):\n"
        
        # No fields defined
        if not fields:
            model_code += "    pass\n"
            return model_code
        
        # Add fields
        for field in fields:
            field_code = f"    {field['name']} = models.{field['type']}("
            
            # Handle foreign key reference
            if field['type'] in ["ForeignKey", "OneToOneField", "ManyToManyField"] and field['foreign_key']:
                # Extract model path
                model_parts = field['foreign_key'].split('.')
                if len(model_parts) > 1:
                    model_ref = model_parts[-1]
                    app_name = model_parts[0]
                    
                    field_code += f"to='{app_name}.{model_ref}', "
                else:
                    field_code += f"to='{field['foreign_key']}', "
            
            # Add options
            if field['options']:
                field_code += f"{field['options']}"
            
            # Close the field definition
            field_code += ")\n"
            model_code += field_code
        
        # Add Meta class and string representation
        model_code += "\n    class Meta:\n"
        model_code += f"        verbose_name = '{firstupper(model_vn_name) or (model_name_capitalize + 's')}'\n"
        model_code += f"        verbose_name_plural = '{firstupper(model_vn_name) or (model_name_capitalize + 's')}'\n"
        
        # Add imports at the beginning
        imports_code = "\n".join(imports) + "\n\n"
        
        return imports_code + model_code

    def create_model_with_fields(self, app_name, model_name, model_code):
        """Create the model file with the generated code"""
        model_name_capitalize = firstupper(model_name)
        project_path = self.app.project_path.text().strip()
        
        # Create the models directory if it doesn't exist
        models_dir = os.path.join(project_path, "apps", app_name, "models")
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        
        # Create __init__.py if it doesn't exist
        init_file = os.path.join(models_dir, "__init__.py")
        if not os.path.exists(init_file):
            create_file(init_file, "# Models initialization\n")
            
        init_file_content = read_file(init_file)
        
        # Create or update the model file
        model_file = os.path.join(models_dir, f"{model_name}.py")
        
        try:
            # Write the model code to the file
            create_file(model_file, model_code)
            
            # Update __init__.py to import the model
            start_new_line = "\n" if init_file_content else ""
            with open(init_file, 'a', encoding='utf-8') as f:
                f.write(f"{start_new_line}from .{model_name} import {model_name_capitalize}")
            
            self.log(f"Created model {model_name_capitalize} in app {app_name}", "success")
            
            # Update the tree view
            self.update_tree_from_folder(True)
        except Exception as e:
            self.log(f"Error while creating model: {str(e)}", "error")

    def hide_model_form(self):
        """Hide model form and clear it completely"""
        self.model_form_frame.setVisible(False)
        
        # Remove all existing field rows
        while self.field_rows:
            self.delete_field_row(self.field_rows[0]["widget"])
        
        # Add one default empty field row
        self.add_field_row()
        
        # Clear model inputs
        self.model_name_input.clear()
        self.model_vn_name_input.clear()
        self.model_abstract.setCurrentIndex(0)
        
    def toggle_model_form(self):
        """Toggle visibility of the model creation form"""
        # Check if an app is selected
        selected_items = self.tree.selectedItems()
        if not selected_items:
            self.log("Please select the application", "error")
            return
        
        # Get app name
        selected_item = selected_items[0]
        self.selected_app_name = self.get_selected_app_name(selected_item)
        
        if not self.selected_app_name:
            self.log("Please select an application", "error")
            return

        self.model_form_frame.setVisible(not self.model_form_frame.isVisible())
        
        # Toggle form visibility
        if not self.model_form_frame.isVisible():
            # Reset the form completely when showing
            self.hide_model_form()
        elif not self.field_rows:
            self.add_field_row()
        
        # Focus on model name input if showing the form
        if self.model_form_frame.isVisible():
            self.model_name_input.setText("")
            self.model_name_input.setFocus()
        
    def get_selected_app_name(self, selected_item):
        """Lấy tên ứng dụng từ item được chọn"""
        # Duyệt lên để tìm item ứng dụng
        while selected_item is not None:
            parent = selected_item.parent()
            if parent and parent.text(0) == 'apps':
                return selected_item.text(0)
            selected_item = parent
        return None

    def show_create_view_dialog(self):
        """Hiển thị dialog tạo view"""
        self.log("Chức năng tạo view đang được phát triển", "success")

    def show_create_serializer_dialog(self):
        """Hiển thị dialog tạo serializer"""
        self.log("Chức năng tạo serializer đang được phát triển", "success")

    def show_create_url_dialog(self):
        """Hiển thị dialog tạo URL"""
        self.log("Chức năng tạo URL đang được phát triển", "success")

        
    def log(self, message, tag=None):
        """Thêm thông báo nhật ký với định dạng dựa trên thẻ"""
        color = "black"
        if tag == "error":
            color = "red"
        elif tag == "success":
            color = "green"
        elif tag == "info":
            color = "blue"

        project_path = self.app.project_path.text().strip()
    
        # Kiểm tra xem self.log_text có tồn tại không
        if hasattr(self, 'log_text') and self.log_text is not None:
            path_string = "" if not project_path else f"<strong>{project_path}: </strong>"
            self.log_text.append(f"<span style='color:{color};'>{path_string}{message}</span>")
            # Cuộn xuống cuối
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        else:
            # Nếu không có log_text, in ra console
            print(f"[{tag.upper() if tag else 'LOG'}] {message}")
    
    def on_new_app_name_change(self, text):
        self._new_app_name = text

    def on_verbose_name_change(self, text):
        self._verbose_name = text
    
    def initialize_tree_structure(self):
        """Khởi tạo cấu trúc cây với 'apps' làm gốc"""
        # Xóa tất cả các nút hiện tại
        self.tree.clear()
        
        # Tạo nút gốc 'apps'
        self.apps_item = QTreeWidgetItem(self.tree, ["apps"])
        self.apps_item.setExpanded(True)
        
        QTreeWidgetItem(self.tree, ["settings.py"])
        
        # Kiểm tra đường dẫn dự án
        if not self.app or not hasattr(self.app, 'project_path'):
            self.log("The project path has not been selected", "error")
            return

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
        project_path = self.app.project_path.text().strip()
        
        if not project_path:
            self.log(f"Please select the project path", "error")
            return
        
        """Thêm ứng dụng Django mới"""
        # Lấy tên ứng dụng từ input
        app_name = self._new_app_name.strip()
        verbose_name = self._verbose_name.strip()

        # Kiểm tra tên ứng dụng
        if not app_name:
            self.log("Please enter the application name", "error")
            return
            
        # Kiểm tra tên ứng dụng hợp lệ
        if not app_name.isalnum() and not app_name.isidentifier():
            self.log("Invalid application name. Only letters, numbers and underscores are allowed.", "error")
            return
            
        # Kiểm tra xem ứng dụng đã tồn tại chưa
        for i in range(self.apps_item.childCount()):
            app_item = self.apps_item.child(i)
            if app_item.text(0) == app_name:
                self.log(f"The application '{app_name}' already exists.", "error")
                return
        
        # Sử dụng tên ứng dụng làm tên hiển thị nếu không có
        if not verbose_name:
            verbose_name = firstupper(app_name)
            
        # Tạo nút ứng dụng mới trong cây
        app_item = self.create_app_node(app_name)
        
        # Tạo thư mục và file thực sự trên đĩa nếu đường dẫn dự án đã được chọn
        project_path = self.app.project_path.text().strip()
        if os.path.exists(project_path):
            try:
                # Tạo thư mục ứng dụng và cấu trúc
                create_django_app_files(project_path, app_name, verbose_name, self.log)
                
                self.log(f"App '{app_name}' successfully created", "success")
                
                # Cập nhật file settings.py để thêm ứng dụng vào INSTALLED_APPS
                update_settings_file(project_path, app_name, self.log)
                
                # Xóa giá trị trong ô nhập liệu
                self.new_app_name.setText("")
                self.verbose_name.setText("")
                
                # Cập nhật lại cây từ thư mục
                self.update_tree_from_folder(True)
            except Exception as e:
                self.log(f"Error when creating folders and files for the application '{app_name}': {str(e)}", "error")
    
    def on_tree_select(self):
        """Xử lý khi chọn item trên cây"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            # Reset trạng thái khi không chọn item
            self.file_content.setVisible(False)
            self.disable_all_buttons()
            return
            
        selected_item = selected_items[0]
        
        # Xây dựng đường dẫn từ item đã chọn đến root
        path = []
        item = selected_item
        
        # Duyệt từ item được chọn lên các nút cha
        while item is not None:
            path.insert(0, item.text(0))
            item = item.parent()
            
        def get_file_content(path):
            project_path = self.app.project_path.text().strip()
            
            if project_path:
                file_path = os.path.join(project_path, *path)
                if os.path.isfile(file_path):
                    filet_content = read_file(file_path)
                    self.file_content.setPlainText(filet_content or "No content")
                    self.file_content.setVisible(True)
        
        # Kiểm tra loại item và cập nhật thông tin
        if len(path) == 1 and path[0] == 'apps':
            # Gốc apps
            self.disable_all_buttons()
            self.model_form_frame.setVisible(False)
            self.file_content.setVisible(False)
            self.file_content.setPlainText("")
        elif len(path) == 2 and path[0] == 'apps':
            # Một ứng dụng
            self.enable_app_buttons()
            self.file_content.setPlainText("")
            self.file_content.setVisible(False)
            self.model_form_frame.setVisible(False)
        elif len(path) > 2 and path[0] == 'apps':
            # File hoặc thư mục con
            file_name = path[-1]
            self.model_form_frame.setVisible(False)
            
            # Kiểm tra loại file để kích hoạt nút phù hợp
            if file_name in ('models', 'models.py'):
                self.enable_model_buttons()
                self.file_content.setPlainText("")
                self.file_content.setVisible(False)
            elif file_name in ('views', 'views.py'):
                self.enable_view_buttons()
                self.file_content.setPlainText("")
                self.file_content.setVisible(False)
            elif file_name in ('serializers', 'serializers.py'):
                self.file_content.setPlainText("")
                self.file_content.setVisible(False)
                self.enable_serializer_buttons()
            elif file_name in ('urls', 'urls.py'):
                self.file_content.setVisible(False)
                self.enable_url_buttons()
                get_file_content(path)
            else:
                self.disable_all_buttons()
                get_file_content(path)
        elif len(path) > 0 and path[0] == 'settings.py':
            self.model_form_frame.setVisible(False)
            self.file_content.setVisible(False)
            get_file_content(["config", *path])
            self.disable_all_buttons()

    def disable_all_buttons(self):
        """Vô hiệu hóa tất cả các nút"""
        self.create_model_btn.setEnabled(False)
        self.create_view_btn.setEnabled(False)
        self.create_serializer_btn.setEnabled(False)
        self.create_url_btn.setEnabled(False)

    def enable_app_buttons(self):
        """Kích hoạt các nút cho ứng dụng"""
        self.create_model_btn.setEnabled(True)
        self.create_view_btn.setEnabled(True)
        self.create_serializer_btn.setEnabled(True)
        self.create_url_btn.setEnabled(True)

    def enable_model_buttons(self):
        """Kích hoạt nút model"""
        self.disable_all_buttons()
        self.create_model_btn.setEnabled(True)

    def enable_view_buttons(self):
        """Kích hoạt nút view"""
        self.disable_all_buttons()
        self.create_view_btn.setEnabled(True)

    def enable_serializer_buttons(self):
        """Kích hoạt nút serializer"""
        self.disable_all_buttons()
        self.create_serializer_btn.setEnabled(True)

    def enable_url_buttons(self):
        """Kích hoạt nút URL"""
        self.disable_all_buttons()
        self.create_url_btn.setEnabled(True)
    
    def update_tree_from_folder(self, is_updated=False, is_reload=False):
        """Cập nhật cấu trúc cây dựa trên thư mục thực tế"""
        # Kiểm tra xem project_path có được set chưa
        if not self.app or not hasattr(self.app, 'project_path'):
            self.log("The project path has not been selected", "error")
            return

        project_path = self.app.project_path.text().strip()
        
        # Kiểm tra đường dẫn dự án
        if not project_path:
            self.log("Please select the project path", "error")
            return

        setting_path = os.path.join(project_path, "config", "settings.py")
        if not os.path.exists(setting_path):
            self.app.env_tab.log("The project is not structured correctly, please pull the code from Github: https://github.com/idtinc/django-base", "error")
            return

        # Debug log
        print(f"Updating tree from folder: {project_path}")

        apps_path = os.path.join(project_path, "apps")
        
        # Nếu thư mục apps không tồn tại, tạo mới
        if not os.path.exists(apps_path):
            try:
                os.makedirs(apps_path)
                self.log(f"Created directory {apps_path}", "info")
                self.app.env_tab.log(f"Created directory {apps_path}", "info")
            except Exception as e:
                self.log(f"Cannot create apps folder: {str(e)}", "error")
                self.app.env_tab.log(f"Cannot create apps folder: {str(e)}", "error")
                return
        
        # Nếu không phải thư mục, báo lỗi
        if not os.path.isdir(apps_path):
            self.log(f"{apps_path} not a directory", "error")
            self.app.env_tab.log(f"{apps_path} not a directory", "error")
            return
                
        # Xóa tất cả nút hiện tại
        self.tree.clear()
                
        # Khởi tạo lại file_data
        self.app.file_data = {}
                
        # Tạo nút gốc apps
        self.apps_item = QTreeWidgetItem(self.tree, ["apps"])
        self.apps_item.setExpanded(True)
        
        QTreeWidgetItem(self.tree, ["settings.py"])
        
        # Lấy danh sách các thư mục ứng dụng
        apps = []
        try:
            for item in os.listdir(apps_path):
                item_path = os.path.join(apps_path, item)
                if os.path.isdir(item_path) and not item.startswith('__') and not item.startswith('.'):
                    apps.append(item)
        except Exception as e:
            self.log(f"Error reading application list: {str(e)}", "error")
            self.app.env_tab.log(f"Error reading application list: {str(e)}", "error")
            return
                    
        # Tạo nút cho mỗi ứng dụng
        setting_path = os.path.join(project_path, "config", "settings.py")
        if not apps and os.path.exists(setting_path):
            self.log("There are no applications yet", "info")
            self.app.env_tab.log("There are no applications yet", "info")
        
        for app_name in sorted(apps):
            app_path = os.path.join(apps_path, app_name)
            app_item = QTreeWidgetItem(self.apps_item, [app_name])
            
            # Quét đệ quy thư mục ứng dụng
            self.scan_directory(app_path, app_item, f"apps/{app_name}")
        
        if not is_updated and len(apps) > 0:
            # Log số lượng ứng dụng
            self.log(f"Found {len(apps)} app", "info")
            self.app.env_tab.log(f"Found {len(apps)} app", "info")
        
        if is_reload:
            self.hide_model_form()
            self.disable_all_buttons()
            self.model_form_frame.setVisible(False)
            self.file_content.setVisible(False)
            self.file_content.setPlainText("")
    
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