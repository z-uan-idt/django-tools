import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QProgressBar, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class WorkerThread(QThread):
    """Worker thread to run background tasks"""
    update_signal = pyqtSignal(str, str)  # Message, tag
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)  # Success, message

    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.task(
                self.update_signal, 
                self.progress_signal, 
                self.finished_signal, 
                *self.args, **self.kwargs
            )
        except Exception as e:
            self.update_signal.emit(f"Lỗi: {str(e)}", "error")
            self.finished_signal.emit(False, str(e))


class EnvTab(QWidget):
    """Tab môi trường cho việc tạo và quản lý môi trường ảo Python"""
    
    def __init__(self, parent=None, app=None):
        super().__init__(parent)
        self.app = app
        self.build_ui()
        
    def build_ui(self):
        # Layout chính
        layout = QVBoxLayout(self)
        
        # Frame điều khiển
        control_layout = QHBoxLayout()
        
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
        
        # Nhập tên môi trường
        control_layout.addWidget(QLabel("Tên môi trường:"))
        self.env_name = QLineEdit(".pyenv")
        control_layout.addWidget(self.env_name)
        
        # Nút tạo môi trường
        self.create_button = QPushButton("Tạo môi trường")
        self.create_button.clicked.connect(self.create_environment)
        control_layout.addWidget(self.create_button)
        
        # Nút cài đặt requirements
        self.requirements_button = QPushButton("Cài đặt requirements.txt")
        self.requirements_button.clicked.connect(self.install_requirements)
        control_layout.addWidget(self.requirements_button)
        
        layout.addLayout(control_layout)
        
        # Thanh tiến trình
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        # Khu vực nhật ký
        layout.addWidget(QLabel("Nhật ký:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
    def log(self, message, tag=None):
        """Thêm thông báo nhật ký với định dạng dựa trên thẻ"""
        color = "black"
        if tag == "error":
            color = "red"
        elif tag == "success":
            color = "green"
        elif tag == "info":
            color = "blue"
            
        self.log_text.append(f"<span style='color:{color};'>{message}</span>")
        # Cuộn xuống cuối
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def reset_progress_bar(self):
        """Reset thanh tiến trình về 0%"""
        self.progress.setValue(0)
    
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
                        if self.app.os_type == "Windows":
                            startupinfo = subprocess.STARTUPINFO()
                            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                            
                            result = subprocess.run(
                                [path, "--version"], 
                                capture_output=True, 
                                text=True,
                                startupinfo=startupinfo
                            )
                        else:
                            result = subprocess.run(
                                [path, "--version"], 
                                capture_output=True, 
                                text=True
                            )
                        
                        if result.returncode == 0:
                            self.log(f"Đã tìm thấy Python hệ thống: {path}", "success")
                            return path
                    except Exception:
                        continue
                
                # Nếu không tìm thấy, thử sử dụng py launcher
                try:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                    result = subprocess.run(
                        ["py", "-3", "--version"], 
                        capture_output=True, 
                        text=True,
                        startupinfo=startupinfo
                    )
                    if result.returncode == 0:
                        self.log("Đã tìm thấy Python Launcher", "success")
                        return "py -3"
                except Exception:
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
                        result = subprocess.run(
                            [path, "--version"], 
                            capture_output=True, 
                            text=True
                        )
                        if result.returncode == 0:
                            self.log(f"Đã tìm thấy Python hệ thống: {path}", "success")
                            return path
                    except Exception:
                        continue
            
            # Nếu không tìm thấy Python
            self.log("Không tìm thấy Python hệ thống. Vui lòng cài đặt Python.", "error")
            QMessageBox.critical(self, "Lỗi", "Không tìm thấy Python hệ thống. Vui lòng cài đặt Python.")
            return None
        else:
            # Đang chạy từ mã nguồn - sử dụng Python hiện tại
            return sys.executable
    
    def create_environment(self):
        """Tạo môi trường ảo Python mới"""
        env_name = self.env_name.text().strip()
        if not env_name:
            QMessageBox.critical(self, "Lỗi", "Vui lòng nhập tên môi trường")
            return

        # Đảm bảo đường dẫn dự án tồn tại
        project_path = self.app.project_path.text().strip()
        if not os.path.exists(project_path):
            QMessageBox.critical(self, "Lỗi", f"Đường dẫn dự án không tồn tại: {project_path}")
            return

        # Chuyển đến thư mục dự án
        os.chdir(project_path)

        self.progress.setValue(0)
        self.log(f"Đang tạo môi trường Python tại: {project_path}/{env_name}", "info")

        # Lấy đường dẫn Python hệ thống
        python_executable = self.get_system_python()
        if not python_executable:
            return

        # Định nghĩa tác vụ chạy trong luồng worker
        def run_venv_creation(update_signal, progress_signal, finished_signal):
            try:
                progress_signal.emit(30)
                
                # Xử lý đặc biệt cho Python Launcher trên Windows
                if python_executable == "py -3":
                    if self.app.os_type == "Windows":
                        # Sử dụng cmd để chạy Python Launcher
                        command = f'cmd /c "py -3 -m venv {env_name}"'
                        
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        
                        process = subprocess.Popen(
                            command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            startupinfo=startupinfo
                        )
                    else:
                        update_signal.emit("Python Launcher chỉ có sẵn trên Windows", "error")
                        return
                else:
                    # Sử dụng đường dẫn Python trực tiếp
                    if self.app.os_type == "Windows":
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        
                        process = subprocess.Popen(
                            [python_executable, "-m", "venv", env_name],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            startupinfo=startupinfo
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
                
                progress_signal.emit(90)

                if process.returncode == 0:
                    progress_signal.emit(100)
                    update_signal.emit(f"Đã tạo thành công môi trường: {env_name}", "success")

                    # Hiển thị cách kích hoạt môi trường
                    if self.app.os_type == "Windows":
                        activate_cmd = f".\\{env_name}\\Scripts\\activate"
                        activate_ps_cmd = f".\\{env_name}\\Scripts\\Activate.ps1"
                        update_signal.emit(f"Để kích hoạt môi trường trong CMD: {activate_cmd}", "info")
                        update_signal.emit(f"Để kích hoạt môi trường trong PowerShell: {activate_ps_cmd}", "info")
                    else:  # macOS/Linux
                        activate_cmd = f"source ./{env_name}/bin/activate"
                        update_signal.emit(f"Để kích hoạt môi trường, sử dụng lệnh: {activate_cmd}", "info")
                    
                    finished_signal.emit(True, "Đã tạo môi trường thành công")
                else:
                    progress_signal.emit(0)
                    if stderr:
                        update_signal.emit(f"Lỗi khi tạo môi trường: {stderr}", "error")
                    else:
                        update_signal.emit("Lỗi không xác định khi tạo môi trường", "error")
                    finished_signal.emit(False, "Không thể tạo môi trường")

            except Exception as e:
                progress_signal.emit(0)
                update_signal.emit(f"Lỗi: {str(e)}", "error")
                finished_signal.emit(False, str(e))

        # Tạo và cấu hình luồng worker
        self.worker = WorkerThread(run_venv_creation)
        self.worker.update_signal.connect(self.log)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.finished_signal.connect(self.on_task_finished)
        self.worker.start()
    
    def on_task_finished(self, success, message):
        """Xử lý khi tác vụ hoàn thành"""
        if success:
            QMessageBox.information(self, "Thành công", message)
        else:
            QMessageBox.critical(self, "Lỗi", message)
        
        # Reset thanh tiến trình sau khi hoàn thành
        if success:
            self.reset_progress_bar()
    
    def install_requirements(self):
        """Cài đặt các gói từ requirements.txt"""
        env_name = self.env_name.text().strip()
        if not env_name:
            QMessageBox.critical(self, "Lỗi", "Vui lòng nhập tên môi trường")
            return

        # Đảm bảo đường dẫn dự án tồn tại
        project_path = self.app.project_path.text().strip()
        if not os.path.exists(project_path):
            QMessageBox.critical(self, "Lỗi", f"Đường dẫn dự án không tồn tại: {project_path}")
            return

        # Chuyển đến thư mục dự án
        os.chdir(project_path)

        if not os.path.exists(env_name):
            response = QMessageBox.question(
                self, 
                "Môi trường không tồn tại", 
                f"Môi trường {env_name} chưa tồn tại. Bạn có muốn tạo nó trước không?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if response == QMessageBox.StandardButton.Yes:
                self.create_environment()
            else:
                return

        # Mở hộp thoại chọn file requirements.txt
        req_file, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file requirements.txt",
            "",
            "Text files (*.txt);;All files (*.*)"
        )

        if not req_file:
            return

        self.progress.setValue(0)
        self.log(f"Đang cài đặt các gói từ {req_file}...", "info")

        # Định nghĩa tác vụ chạy trong luồng worker
        def run_requirements_install(update_signal, progress_signal, finished_signal):
            try:
                # Xác định đường dẫn đến pip và activate script trong môi trường ảo
                if self.app.os_type == "Windows":
                    pip_path = os.path.join(env_name, "Scripts", "pip.exe")
                    activate_path = os.path.join(env_name, "Scripts", "activate.bat")
                    
                    # Sử dụng CMD để kích hoạt môi trường và cài đặt
                    install_command = f'cmd /c "cd /d {project_path} && {activate_path} && pip install -r {req_file}"'
                    
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                    process = subprocess.Popen(
                        install_command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        shell=True,
                        startupinfo=startupinfo
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

                # Kiểm tra xem pip có tồn tại không
                if not os.path.exists(pip_path):
                    update_signal.emit(f"Không tìm thấy pip tại {pip_path}", "error")
                    finished_signal.emit(False, f"Không tìm thấy pip tại {pip_path}")
                    return

                progress_signal.emit(10)

                # Đọc đầu ra của quá trình theo từng dòng
                for line in iter(process.stdout.readline, ""):
                    if line:
                        update_signal.emit(line.strip(), "")
                        # Tăng thanh tiến trình
                        current_value = self.progress.value()
                        if current_value < 99:
                            progress_signal.emit(current_value + 1)

                # Đọc lỗi nếu có
                for line in iter(process.stderr.readline, ""):
                    if line:
                        update_signal.emit(line.strip(), "error")

                # Chờ quá trình hoàn tất
                returncode = process.wait()

                if returncode == 0:
                    progress_signal.emit(100)
                    update_signal.emit("Đã cài đặt thành công các gói từ requirements.txt", "success")
                    finished_signal.emit(True, "Đã cài đặt thành công các gói")
                else:
                    progress_signal.emit(0)
                    update_signal.emit("Lỗi khi cài đặt các gói", "error")
                    finished_signal.emit(False, "Không thể cài đặt các gói")

            except Exception as e:
                progress_signal.emit(0)
                update_signal.emit(f"Lỗi: {str(e)}", "error")
                finished_signal.emit(False, str(e))

        # Tạo và cấu hình luồng worker
        self.worker = WorkerThread(run_requirements_install)
        self.worker.update_signal.connect(self.log)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.finished_signal.connect(self.on_task_finished)
        self.worker.start()