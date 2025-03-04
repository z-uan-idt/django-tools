import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class EnvTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.build_ui()
        
    def reset_progress_bar(self):
        """Reset thanh tiến trình về 0%"""
        self.progress["value"] = 0

    def build_ui(self):
        # Frame cho cả nhập liệu và nút bấm trong cùng một hàng
        control_frame = tk.Frame(self)
        control_frame.pack(fill="x", pady=5)

        tk.Label(control_frame, text="Tên môi trường:", width=15, anchor="w").pack(side="left")

        # Tạo font để các widget có chiều cao đồng nhất
        custom_font = ('Arial', 10)
        self.env_name = tk.StringVar(value=".pyenv")
        env_entry = tk.Entry(control_frame,
                             textvariable=self.env_name,
                             width=20,
                             font=custom_font,
                             borderwidth=0,
                             highlightthickness=5,
                             highlightcolor='white', 
                             highlightbackground='white')
        env_entry.pack(side="left", padx=5)

        self.create_button = tk.Button(
            control_frame,
            text="Tạo môi trường",
            command=self.create_environment,
            padx=10,
            font=custom_font
        )
        self.create_button.pack(side="left", padx=5)

        self.requirements_button = tk.Button(
            control_frame,
            text="Cài đặt requirements.txt",
            command=self.install_requirements,
            padx=10,
            font=custom_font
        )
        self.requirements_button.pack(side="left", padx=5)

        # Thanh tiến trình
        progress_frame = tk.Frame(self)
        progress_frame.pack(fill="x", pady=5)

        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill="x")

        # Frame nhật ký
        log_frame = tk.Frame(self)
        log_frame.pack(fill="both", expand=True, pady=5)

        tk.Label(log_frame, text="Nhật ký:", anchor="w").pack(fill="x")

        self.log_text = tk.Text(log_frame, height=15, width=80)
        self.log_text.pack(fill="both", expand=True, side="left")

        # Thêm thanh cuộn cho log
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

        # Cài đặt màu văn bản
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("info", foreground="blue")

    def log(self, message, tag=None):
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.update()

    def get_system_python(self):
        """Lấy đường dẫn đến Python hệ thống (không phải Python được đóng gói)"""
        # Kiểm tra xem ứng dụng có đang chạy từ bản đóng gói không
        if getattr(sys, 'frozen', False):
            # Đang chạy từ bản đóng gói - cần tìm Python hệ thống
            self.log("Phát hiện ứng dụng đã đóng gói, đang tìm Python hệ thống...", "info")
            
            if self.app.os_type == "Windows":
                # Thử một số vị trí cài đặt Python phổ biến trên Windows
                python_paths = [
                    "python.exe",  # Nếu có trong PATH
                    "C:\\Python39\\python.exe",
                    "C:\\Python310\\python.exe",
                    "C:\\Python311\\python.exe",
                    "C:\\Python312\\python.exe",
                    "C:\\Program Files\\Python39\\python.exe",
                    "C:\\Program Files\\Python310\\python.exe",
                    "C:\\Program Files\\Python311\\python.exe",
                    "C:\\Program Files\\Python312\\python.exe",
                    "C:\\Program Files (x86)\\Python39\\python.exe",
                    "C:\\Program Files (x86)\\Python310\\python.exe",
                    "C:\\Program Files (x86)\\Python311\\python.exe",
                    "C:\\Program Files (x86)\\Python312\\python.exe"
                ]
                
                for path in python_paths:
                    try:
                        # Kiểm tra xem Python có thể chạy không
                        result = subprocess.run([path, "--version"], 
                                               capture_output=True, 
                                               text=True,
                                               creationflags=subprocess.CREATE_NO_WINDOW)
                        if result.returncode == 0:
                            self.log(f"Đã tìm thấy Python hệ thống: {path}", "success")
                            return path
                    except:
                        continue
                
                # Nếu không tìm thấy, thử sử dụng py launcher
                try:
                    result = subprocess.run(["py", "-3", "--version"], 
                                           capture_output=True, 
                                           text=True,
                                           creationflags=subprocess.CREATE_NO_WINDOW)
                    if result.returncode == 0:
                        self.log("Đã tìm thấy Python Launcher", "success")
                        return "py -3"
                except:
                    pass
                
            else:  # macOS/Linux
                # Kiểm tra các bản Python phổ biến trên Unix
                python_paths = [
                    "python3",
                    "python3.9",
                    "python3.10",
                    "python3.11",
                    "python3.12",
                    "/usr/bin/python3",
                    "/usr/local/bin/python3",
                    "/opt/homebrew/bin/python3"
                ]
                
                for path in python_paths:
                    try:
                        result = subprocess.run([path, "--version"], 
                                               capture_output=True, 
                                               text=True)
                        if result.returncode == 0:
                            self.log(f"Đã tìm thấy Python hệ thống: {path}", "success")
                            return path
                    except:
                        continue
            
            # Nếu không tìm thấy Python
            self.log("Không tìm thấy Python hệ thống. Vui lòng cài đặt Python.", "error")
            messagebox.showerror("Lỗi", "Không tìm thấy Python hệ thống. Vui lòng cài đặt Python.")
            return None
        else:
            # Đang chạy từ mã nguồn - sử dụng Python hiện tại
            return sys.executable

    def create_environment(self):
        env_name = self.env_name.get().strip()
        if not env_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên môi trường")
            return

        # Đảm bảo đường dẫn dự án tồn tại
        project_path = self.app.project_path.get().strip()
        if not os.path.exists(project_path):
            messagebox.showerror("Lỗi", f"Đường dẫn dự án không tồn tại: {project_path}")
            return

        # Chuyển đến thư mục dự án
        os.chdir(project_path)

        self.progress["value"] = 0
        self.log(f"Đang tạo môi trường Python tại: {project_path}/{env_name}", "info")

        # Lấy đường dẫn Python hệ thống
        python_executable = self.get_system_python()
        if not python_executable:
            return

        def run_task():
            try:
                self.progress["value"] = 30
                
                # Xử lý đặc biệt cho Python Launcher trên Windows
                if python_executable == "py -3":
                    if self.app.os_type == "Windows":
                        # Sử dụng cmd để chạy Python Launcher
                        command = f'cmd /c "py -3 -m venv {env_name}"'
                        process = subprocess.Popen(
                            command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    else:
                        self.log("Python Launcher chỉ khả dụng trên Windows", "error")
                        return
                else:
                    # Sử dụng đường dẫn Python trực tiếp
                    if self.app.os_type == "Windows":
                        process = subprocess.Popen(
                            [python_executable, "-m", "venv", env_name],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    else:
                        process = subprocess.Popen(
                            [python_executable, "-m", "venv", env_name],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )

                # Đọc đầu ra của quá trình
                stdout, stderr = process.communicate()
                
                self.progress["value"] = 90

                if process.returncode == 0:
                    self.progress["value"] = 100
                    self.log(f"Đã tạo thành công môi trường: {env_name}", "success")

                    # Hiển thị cách kích hoạt môi trường
                    if self.app.os_type == "Windows":
                        activate_cmd = f".\\{env_name}\\Scripts\\activate"
                        activate_ps_cmd = f".\\{env_name}\\Scripts\\Activate.ps1"
                        self.log(f"Để kích hoạt môi trường trong CMD: {activate_cmd}", "info")
                        self.log(f"Để kích hoạt môi trường trong PowerShell: {activate_ps_cmd}", "info")
                    else:  # macOS/Linux
                        activate_cmd = f"source ./{env_name}/bin/activate"
                        self.log(f"Để kích hoạt môi trường, sử dụng lệnh: {activate_cmd}", "info")
                    
                    self.after(1000, self.reset_progress_bar)
                else:
                    self.progress["value"] = 0
                    if stderr:
                        self.log(f"Lỗi khi tạo môi trường: {stderr}", "error")
                    else:
                        self.log("Lỗi không xác định khi tạo môi trường", "error")

            except Exception as e:
                self.progress["value"] = 0
                self.log(f"Lỗi: {str(e)}", "error")

        # Chạy tác vụ trong một luồng riêng biệt
        thread = threading.Thread(target=run_task)
        thread.daemon = True
        thread.start()

    def install_requirements(self):
        env_name = self.env_name.get().strip()
        if not env_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên môi trường")
            return

        # Đảm bảo đường dẫn dự án tồn tại
        project_path = self.app.project_path.get().strip()
        if not os.path.exists(project_path):
            messagebox.showerror(
                "Lỗi", f"Đường dẫn dự án không tồn tại: {project_path}")
            return

        # Chuyển đến thư mục dự án
        os.chdir(project_path)

        if not os.path.exists(env_name):
            res = messagebox.askyesno("Môi trường không tồn tại", f"Môi trường {env_name} chưa tồn tại. Bạn có muốn tạo mới không?")
            if res:
                self.create_environment()
            else:
                return

        # Mở hộp thoại chọn file requirements.txt
        req_file = filedialog.askopenfilename(
            title="Chọn file requirements.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not req_file:
            return

        self.progress["value"] = 0
        self.log(f"Đang cài đặt các gói từ {req_file}...", "info")

        def run_install():
            try:
                # Xác định đường dẫn đến pip và activate script trong môi trường ảo
                if self.app.os_type == "Windows":
                    pip_path = os.path.join(env_name, "Scripts", "pip.exe")
                    activate_path = os.path.join(env_name, "Scripts", "activate.bat")
                    
                    # Sử dụng CMD để kích hoạt môi trường và cài đặt
                    install_command = f'cmd /c "cd /d {project_path} && {activate_path} && pip install -r {req_file}"'
                    
                    process = subprocess.Popen(
                        install_command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:  # macOS/Linux
                    pip_path = os.path.join(env_name, "bin", "pip")
                    activate_path = os.path.join(env_name, "bin", "activate")
                    
                    # Sử dụng shell để kích hoạt môi trường và cài đặt
                    install_command = f'cd "{project_path}" && source "{activate_path}" && pip install -r "{req_file}"'
                    
                    process = subprocess.Popen(
                        install_command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        shell=True
                    )

                # Kiểm tra xem pip tồn tại
                if not os.path.exists(pip_path):
                    self.log(f"Không tìm thấy pip tại {pip_path}", "error")
                    return

                self.progress["value"] = 10

                # Đọc đầu ra của quá trình theo từng dòng
                for line in iter(process.stdout.readline, ""):
                    if line:
                        self.log(line.strip())
                        self.progress["value"] += 1
                        if self.progress["value"] >= 100:
                            self.progress["value"] = 99

                # Đọc lỗi nếu có
                for line in iter(process.stderr.readline, ""):
                    if line:
                        self.log(line.strip(), "error")

                # Chờ quá trình hoàn tất
                returncode = process.wait()

                if returncode == 0:
                    self.progress["value"] = 100
                    self.log("Đã cài đặt thành công các gói từ requirements.txt", "success")

                    self.after(1000, self.reset_progress_bar)
                else:
                    self.progress["value"] = 0
                    self.log("Lỗi khi cài đặt các gói", "error")

            except Exception as e:
                self.progress["value"] = 0
                self.log(f"Lỗi: {str(e)}", "error")

        # Chạy cài đặt trong một luồng riêng biệt
        thread = threading.Thread(target=run_install)
        thread.daemon = True
        thread.start()