import os
import tkinter as tk
from tkinter import ttk, messagebox

from utils.project_utils import update_settings_file, create_django_app_files

class StructureTab(tk.Frame):
    def __init__(self, parent, app):
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
        
        # Định nghĩa progress bar
        self.progress = None
        
        # Khởi tạo biến cho tên ứng dụng và tên hiển thị
        self.new_app_name = None
        self.verbose_name = None
        
        self.build_ui()
        self.initialize_tree_structure()
        
    def reset_progress_bar(self):
        """Reset thanh tiến trình về 0%"""
        if self.progress:
            self.progress["value"] = 0
    
    def build_ui(self):
        # Frame cho nhập tên ứng dụng và thêm (ở phía trên cấu trúc)
        app_input_frame = tk.Frame(self)
        app_input_frame.pack(fill="x", pady=5)
        
        # Tạo font để các widget có chiều cao đồng nhất
        custom_font = ('Arial', 10)
        
        # Nhập tên ứng dụng
        tk.Label(app_input_frame, text="Tên ứng dụng:", anchor="w").pack(side="left", padx=2)
        self.new_app_name = tk.StringVar()
        app_entry = tk.Entry(app_input_frame, 
                             textvariable=self.new_app_name, 
                             width=15, 
                             font=custom_font,
                             borderwidth=0,
                             highlightthickness=5,
                             highlightcolor='white', 
                             highlightbackground='white')
        app_entry.pack(side="left", padx=2)
        
        # Nhập tên hiển thị
        tk.Label(app_input_frame, text="Tên hiển thị:", anchor="w").pack(side="left", padx=2)
        self.verbose_name = tk.StringVar()
        verbose_entry = tk.Entry(app_input_frame, 
                                 textvariable=self.verbose_name, 
                                 width=15, 
                                 font=custom_font,
                                 borderwidth=0,
                                 highlightthickness=5,
                                 highlightcolor='white', 
                                 highlightbackground='white')
        verbose_entry.pack(side="left", padx=2)
        
        # Nút thêm
        add_app_button = tk.Button(
            app_input_frame,
            text="Thêm",
            command=self.add_new_app,
            font=custom_font
        )
        add_app_button.pack(side="left", padx=2)
        
        # Frame chứa cây cấu trúc và khung hiển thị nội dung file
        # Configure the PanedWindow to expand fully
        structure_container = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        structure_container.pack(fill="both", expand=True, pady=0)
        
         # Frame bên trái chứa danh sách ứng dụng
        left_frame = tk.Frame(structure_container)
        structure_container.add(left_frame, width=300, stretch="always")
        
        # Layout cho left_frame
        left_frame_top = tk.Frame(left_frame)
        left_frame_top.pack(fill="x", pady=0)
        
        # Label cho cây cấu trúc
        project_label = tk.Label(left_frame_top, text="Cấu trúc dự án:", anchor="w")
        project_label.pack(side="left", fill="x", pady=0)
        
        # Tạo TreeView để hiển thị cấu trúc thư mục - setting it to fill the left frame
        tree_frame = tk.Frame(left_frame)
        tree_frame.pack(fill="both", expand=True, pady=0)
        
        self.tree = ttk.Treeview(tree_frame, show=("tree",))
        self.tree.pack(fill="both", expand=True, side="left")
        
        # Thêm thanh cuộn cho tree
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Frame bên phải hiển thị nội dung file
        content_frame = tk.Frame(structure_container)
        structure_container.add(content_frame, stretch="always")
        
        # Label cho phần nội dung
        tk.Label(content_frame, text="Nội dung file:", anchor="w").pack(fill="x", pady=0)
        
        # Wrapping the text widget and scrollbar in a frame to ensure they expand properly
        text_frame = tk.Frame(content_frame)
        text_frame.pack(fill="both", expand=True, pady=0)
        
        # Text widget để hiển thị nội dung file
        self.file_content = tk.Text(text_frame, wrap="word")
        self.file_content.pack(fill="both", expand=True, side="left")
        
        # Thêm thanh cuộn cho nội dung file
        content_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.file_content.yview)
        content_scrollbar.pack(side="right", fill="y")
        self.file_content.config(yscrollcommand=content_scrollbar.set)
        
        # Thêm frame cho nút Làm mới dưới cùng
        refresh_frame = tk.Frame(self)
        refresh_frame.pack(fill="x", pady=5)
        
        # Nút Refresh được chuyển xuống dưới 2 panel
        refresh_button = tk.Button(
            refresh_frame,
            text="Làm mới",
            command=self.update_tree_from_folder,
            font=custom_font
        )
        refresh_button.pack(side="right", padx=10)
        
        # Set a weight for the paned window to maintain even distribution
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Thêm sự kiện khi chọn item trên cây
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
    
    def initialize_tree_structure(self):
        # Xóa tất cả các nút hiện tại
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Tạo nút gốc là 'apps'
        self.apps_id = self.tree.insert("", "end", text="apps", open=True)
        
        # Kiểm tra đường dẫn dự án
        project_path = self.app.project_path.get().strip()
        if os.path.exists(project_path):
            # Nếu đường dẫn tồn tại, quét thư mục apps để lấy danh sách ứng dụng
            apps_path = os.path.join(project_path, "apps")
            if os.path.exists(apps_path) and os.path.isdir(apps_path):
                self.update_tree_from_folder()
                return
    
    def create_app_node(self, app_name):
        # Tạo nút ứng dụng
        app_id = self.tree.insert(self.apps_id, "end", text=app_name, open=False)
        
        # Tạo các thư mục con tiêu chuẩn cho Django
        dirs = ["docs", "migrations", "models", "serializers", "services", "views"]
        dir_nodes = {}
        
        for dir_name in dirs:
            dir_node = self.tree.insert(app_id, "end", text=dir_name)
            dir_nodes[dir_name] = dir_node
            
        # Tạo các file cơ bản cho ứng dụng
        self.tree.insert(app_id, "end", text="__init__.py")
        self.app.file_data[f"apps/{app_name}/__init__.py"] = ""
        
        self.tree.insert(app_id, "end", text="admin.py")
        self.app.file_data[f"apps/{app_name}/admin.py"] = ""
        
        self.tree.insert(app_id, "end", text="apps.py")
        self.app.file_data[f"apps/{app_name}/apps.py"] = ""
        
        self.tree.insert(app_id, "end", text="urls.py")
        self.app.file_data[f"apps/{app_name}/urls.py"] = ""
        
        return app_id
    
    def add_new_app(self):
        # Lấy tên ứng dụng từ input
        app_name = self.new_app_name.get().strip()
        verbose_name = self.verbose_name.get().strip()

        # Kiểm tra tên ứng dụng
        if not app_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên ứng dụng")
            return
            
        # Kiểm tra tên ứng dụng hợp lệ
        if not app_name.isalnum() and not app_name.isidentifier():
            messagebox.showerror("Lỗi", "Tên ứng dụng không hợp lệ. Chỉ được phép sử dụng chữ cái, số và dấu gạch dưới.")
            return
            
        # Kiểm tra xem ứng dụng đã tồn tại chưa
        for app_item in self.tree.get_children(self.apps_id):
            if self.tree.item(app_item)["text"] == app_name:
                messagebox.showerror("Lỗi", f"Ứng dụng '{app_name}' đã tồn tại.")
                return
        
        # Sử dụng tên ứng dụng làm tên hiển thị nếu không có
        if not verbose_name:
            verbose_name = app_name.capitalize()
            
        # Tạo nút ứng dụng mới trong cây
        app_id = self.create_app_node(app_name)
        
        # Tạo thư mục và file thực sự trên đĩa nếu đường dẫn dự án đã được chọn
        project_path = self.app.project_path.get().strip()
        if os.path.exists(project_path):
            try:
                # Tạo thư mục ứng dụng và cấu trúc
                create_django_app_files(project_path, app_name, verbose_name)
                
                # Cập nhật file settings.py để thêm ứng dụng vào INSTALLED_APPS
                update_settings_file(project_path, app_name)
                
                # Xóa giá trị trong ô nhập liệu
                self.new_app_name.set("")
                self.verbose_name.set("")
                
                # Cập nhật lại cây từ thư mục
                self.update_tree_from_folder()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi tạo thư mục và file cho ứng dụng '{app_name}': {str(e)}")
    
    def on_tree_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        selected_item = selected_items[0]
        
        # Xây dựng đường dẫn từ item đã chọn đến root
        path = []
        parent = selected_item
        
        # Duyệt từ item được chọn lên các nút cha
        while parent:
            item_text = self.tree.item(parent)["text"]
            path.insert(0, item_text)
            parent = self.tree.parent(parent)
        
        # Tạo đường dẫn file
        file_path = "/".join(path)
        
        # Xóa nội dung hiện tại
        self.file_content.delete(1.0, tk.END)
        
        # Hiển thị đường dẫn tới file
        self.file_content.insert(tk.END, f"Đường dẫn: {file_path}\n\n")
        
        # Kiểm tra xem đây có phải là file không
        project_path = self.app.project_path.get()
        full_path = os.path.join(project_path, file_path)
        
        if os.path.isfile(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if content.strip():  # Nếu file có nội dung
                    self.file_content.insert(tk.END, content)
                else:  # Nếu file rỗng
                    self.file_content.insert(tk.END, "File rỗng")
            except Exception as e:
                self.file_content.insert(tk.END, f"Không thể đọc file: {str(e)}")
        elif file_path in self.app.file_data:  # Fallback nếu không đọc được từ đĩa
            self.file_content.insert(tk.END, "File rỗng")
        else:  # Nếu là thư mục
            self.file_content.insert(tk.END, "Đây là thư mục")
    
    def update_tree_from_folder(self):
        """Cập nhật cây cấu trúc dựa trên thư mục thực tế"""
        project_path = self.app.project_path.get()
        apps_path = os.path.join(project_path, "apps")
        
        # Nếu thư mục apps không tồn tại, giữ nguyên cấu trúc mẫu
        if not os.path.exists(apps_path) or not os.path.isdir(apps_path):
            return
            
        # Xóa tất cả nút hiện tại
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Khởi tạo lại file_data
        self.app.file_data = {}
            
        # Tạo nút gốc apps
        self.apps_id = self.tree.insert("", "end", text="apps", open=True)
        
        # Lấy danh sách các thư mục ứng dụng
        apps = []
        for item in os.listdir(apps_path):
            item_path = os.path.join(apps_path, item)
            if os.path.isdir(item_path) and not item.startswith('__') and not item.startswith('.'):
                apps.append(item)
                
        # Tạo nút cho mỗi ứng dụng
        for app_name in sorted(apps):
            app_path = os.path.join(apps_path, app_name)
            app_id = self.tree.insert(self.apps_id, "end", text=app_name, open=False)
            
            # Quét đệ quy thư mục ứng dụng
            self.scan_directory(app_path, app_id, f"apps/{app_name}")
    
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
                self.tree.insert(parent_node, "end", text=file_name)
                self.app.file_data[f"{relative_path}/{file_name}"] = ""
        
        # Sau đó thêm các file không phải Python
        for file_name in sorted(files):
            if not file_name.endswith('.py'):
                self.tree.insert(parent_node, "end", text=file_name)
                self.app.file_data[f"{relative_path}/{file_name}"] = ""
        
        # Cuối cùng thêm các thư mục con và quét đệ quy
        for subdir in sorted(subdirs):
            subdir_path = os.path.join(directory_path, subdir)
            subdir_node = self.tree.insert(parent_node, "end", text=subdir)
            self.scan_directory(subdir_path, subdir_node, f"{relative_path}/{subdir}")