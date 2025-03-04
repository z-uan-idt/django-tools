import os
import platform
import tkinter as tk
from tkinter import ttk

from gui.env_tab import EnvTab
from gui.structure_tab import StructureTab
from utils.file_utils import get_current_directory


class EnvSetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Django Base Setup")
        self.root.geometry("800x650")
        self.root.resizable(False, False)

        # Xác định hệ điều hành
        self.os_type = platform.system()

        # Lưu đường dẫn hiện tại
        self.current_dir = get_current_directory()

        # Khởi tạo file_data
        self.file_data = {}

        # Giao diện chính
        self.create_widgets()

    def create_widgets(self):
        # Frame chính
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Frame chọn đường dẫn dự án
        project_frame = tk.Frame(main_frame)
        project_frame.pack(fill="x", pady=5)

        tk.Label(project_frame, text="Đường dẫn dự án:", width=15, anchor="w").pack(side="left")

        # Sử dụng font để điều chỉnh chiều cao gián tiếp
        custom_font = ('Arial', 10)
        self.project_path = tk.StringVar(value=os.getcwd())
        path_entry = tk.Entry(project_frame,
                              textvariable=self.project_path,
                              width=50,
                              font=custom_font,
                              borderwidth=0,
                              highlightthickness=5,
                              highlightcolor='white', 
                              highlightbackground='white')
        path_entry.pack(side="left", padx=5, fill="x", expand=True)

        browse_button = tk.Button(
            project_frame,
            text="Chọn",
            command=self.browse_project_path,
            padx=5,
            font=custom_font
        )
        browse_button.pack(side="left", padx=5)

        # Tạo notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=5)

        # Tab Môi trường
        self.env_tab = EnvTab(self.notebook, self)
        self.notebook.add(self.env_tab, text="Môi trường")

        # Tab Cấu trúc dự án
        self.structure_tab = StructureTab(self.notebook, self)
        self.notebook.add(self.structure_tab, text="Cấu trúc dự án")

    def browse_project_path(self):
        """Mở hộp thoại chọn thư mục dự án"""
        from tkinter import filedialog

        folder_path = filedialog.askdirectory(
            title="Chọn thư mục dự án",
            initialdir=self.current_dir
        )
        if folder_path:
            self.project_path.set(folder_path)
            # Cập nhật thư mục làm việc hiện tại
            os.chdir(folder_path)

            # Thông báo cho các tab biết đường dẫn đã thay đổi
            self.env_tab.log(f"Đã chọn thư mục dự án: {folder_path}", "info")
            self.structure_tab.update_tree_from_folder()
