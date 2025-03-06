import os
import re
import platform
import subprocess
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTabWidget, QFileDialog,
    QProgressBar, QApplication, QLabel
)
from PyQt6.QtCore import Qt
from gui.env_tab import EnvTab, WorkerThread
from gui.structure_tab import StructureTab
from utils.file_utils import create_file, get_current_directory, read_file
from utils.theme import LIGHT_THEME


class CustomTitleBar(QWidget):
    def __init__(self, parent=None, title=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tiêu đề cửa sổ
        self.title = QLabel(title or parent.windowTitle() if parent else "")
        self.title.setStyleSheet("color: #000000; line-height: 20px; font-size: 14px; font-weight: bold; text-transform: uppercase; padding-bottom: 5px")
        
        # Nút điều khiển cửa sổ
        self.btn_minimize = QPushButton("−")
        self.btn_minimize.setStyleSheet("color: #000000; padding: 0 0 2px 2px")
        self.btn_minimize.setFixedSize(30, 30)
        self.btn_minimize.clicked.connect(self.parent().showMinimized)
        
        self.btn_close = QPushButton("×")
        self.btn_close.setStyleSheet("color: #000000; padding: 0 0 2px 2px")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.clicked.connect(self.parent().close)
        
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_close)
        
        # Biến để theo dõi vị trí chuột khi kéo cửa sổ
        self.m_drag = False
        self.startPos = None
    
    # Cập nhật tiêu đề
    def updateTitle(self, title):
        self.title.setText(title)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.m_drag = True
            self.startPos = event.position().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.m_drag and event.buttons() == Qt.MouseButton.LeftButton:
            parent = self.window()
            globalPos = parent.mapToGlobal(event.position().toPoint())
            diff = globalPos - parent.mapToGlobal(self.startPos)
            newpos = parent.pos() + diff
            parent.move(newpos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.m_drag = False


class EnvSetupApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Set application title
        self.setWindowTitle("Python Django Base Setup")
        # self.showFullScreen()
        screen = QApplication.primaryScreen().size()
        width = screen.width() - 100
        height = screen.height() - 200
        self.setGeometry(50, 100, width, height)
        self.setMinimumSize(width, height)
        
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
        
        self.title_bar = CustomTitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # Tạo giao diện
        self.create_widgets()
        
        self.setStyleSheet(LIGHT_THEME)

    def create_widgets(self):
        # Tạo widget tab
        self.tab_widget = QTabWidget()
        
        # Ô nhập đường dẫn
        self.project_path = QLineEdit()
        self.project_path.setEnabled(False)
        self.project_path.setStyleSheet("""
            border: none;
        """)
        
        # Thanh tiến trình
        self.progress = QProgressBar()
        self.progress.setValue(0)
        
        # Tab Môi trường
        self.env_tab = EnvTab(self.tab_widget, self)
        self.tab_widget.addTab(self.env_tab, "Project Setup")
        
        # Tab Cấu trúc dự án
        self.structure_tab = StructureTab(self.tab_widget, self)
        self.structure_tab.setVisible(False)

        # Frame chọn đường dẫn dự án
        project_frame = QWidget()
        project_layout = QHBoxLayout(project_frame)
        project_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_layout.addWidget(self.progress)

        self.browse_button = QPushButton("Select project folder")
        self.browse_button.setFixedWidth(300)
        self.browse_button.clicked.connect(self.browse_project_path)
        project_layout.addWidget(self.browse_button)
        
        # Tim du an
        self.project_path.setPlaceholderText("Path to project directory")
        self.project_path.setStyleSheet("""
            QLineEdit:disabled {
                background-color: transparent;
                color: #000;
                color: blue;
                border: 0;
                font-weight: bold;
            }
        """)
        project_layout.addWidget(self.project_path)
        
        self.close_project = QPushButton("Close")
        self.close_project.setFixedWidth(150)
        self.close_project.setVisible(False)
        self.close_project.clicked.connect(self.clear_select_project)
        project_layout.addWidget(self.close_project)
    
        # Frame chọn đường dẫn dự án
        self.github_frame = QWidget()
        self.github_frame.setVisible(False)
        github_layout = QHBoxLayout(self.github_frame)
        github_layout.setContentsMargins(0, 0, 0, 0)
        
        self.project_name = QLineEdit("django-base")
        self.project_name.setMaximumWidth(250)
        self.project_name.setPlaceholderText("Project name")
        github_layout.addWidget(self.project_name)
        
        self.github_path = QLineEdit("https://github.com/idtinc/django-base")
        self.github_path.setPlaceholderText("Github Project Base link")
        github_layout.addWidget(self.github_path)

        self.pull_code_button = QPushButton("Pull Code")
        self.pull_code_button.setFixedWidth(300)
        self.pull_code_button.clicked.connect(self.pull_code)

        github_layout.addWidget(self.pull_code_button)
        
        self.main_layout.addWidget(self.tab_widget, 1)
        
        self.main_layout.addWidget(project_frame)

        self.main_layout.addWidget(self.github_frame)

        self.main_layout.addWidget(self.progress)
        
    def remove_folder(self, folder_path):
        system = platform.system()
    
        if system == "Windows":
            # Windows command (Command Prompt)
            return f'rmdir /q /s "{folder_path}"'
        else:
            # macOS or Linux command
            return f'rm -rf "{folder_path}"'
    
    def clear_select_project(self):
        self.project_path.setText("")
        
        self.tab_widget.setCurrentIndex(0)
            
        # Cập nhật cấu trúc cây cho cả hai tab
        self.env_tab.env_name.setEnabled(False)
        self.env_tab.create_button.setEnabled(False)
        self.structure_tab.new_app_name.setEnabled(False)
        self.structure_tab.verbose_name.setEnabled(False)
        self.env_tab.requirements_button.setEnabled(False)
        self.structure_tab.add_app_button.setEnabled(False)
        self.structure_tab.refresh_button.setVisible(False)
        self.structure_tab.tree_widget.setVisible(False)
        self.structure_tab.update_tree_from_folder()
        self.env_tab.reset_progress_bar()
        self.title_bar.updateTitle("Python Django Base Setup")
        self.close_project.setVisible(False)
        
    def pull_code(self):
        project_name = self.project_name.text().strip()
        github_path = self.github_path.text().strip()
        github_path_git = github_path
        
        if not github_path_git.endswith(".git"):
            github_path_git = github_path_git + ".git"
        
        project_path = self.project_path.text().strip()
        project_name_dir = os.path.join(project_path, project_name)
        is_remove = github_path_git.endswith("django-base") or github_path_git.endswith("django-base.git")
        remove_dir = " && " + self.remove_folder(os.path.join(project_path, project_name, ".git")) if is_remove else ""
        
        # Sử dụng shell để kích hoạt môi trường và cài đặt
        clone_command = f"cd {project_path} && git clone {github_path_git} {project_name} && cd {project_name_dir} {remove_dir}"
        
        self.progress.setValue(0)
        self.env_tab.log(f"Pulling code from {github_path}...", "info")

        def run_clone_code(update_signal, progress_signal, finished_signal):
            try:
                progress_signal.emit(30)

                process = subprocess.Popen(
                    clone_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True
                )
                
                while process.poll() is None:
                    line = process.stderr.readline()
                    if line:
                        update_signal.emit(line.strip(), "black")
                        
                        match = re.search(r'Receiving objects:\s+(\d+)%', line)
                        if match:
                            percentage = match.group(1)
                            progress_signal.emit(percentage)
                        
                    line = process.stdout.readline()
                    if line:
                        update_signal.emit(line.strip(), "black")
                
                README = os.path.join(project_name_dir, "README.md")
                if os.path.exists(README) and os.path.isfile(README):
                    content_readme = read_file(os.path.join(project_name_dir, "README.md"))
                    
                    if content_readme:
                        if "# Django Base Project" in content_readme:
                            content_readme = content_readme.replace("# Django Base Project", f"# {project_name}")

                        if "django-boilderpalte/" in content_readme:
                            content_readme = content_readme.replace("django-boilderpalte/", f"{project_name}/")

                        create_file(README, content_readme)
                
                progress_signal.emit(90)
                
                if process.returncode == 0:
                    progress_signal.emit(100)
                    finished_signal.emit(True, "Pulled the code successfully")
                    self.project_path.setText(os.path.join(project_path, project_name))
                    self.browse_project_path(self.project_path.text().strip())
                    self.project_name.setText("django-base")
                else:
                    progress_signal.emit(0)
                    finished_signal.emit(False, "Pulling code failed")
            except Exception as e:
                progress_signal.emit(0)
                update_signal.emit(f"Lỗi: {str(e)}", "error")
                finished_signal.emit(False, str(e))
                
        # Tạo và cấu hình luồng worker
        self.worker = WorkerThread(run_clone_code)
        self.worker.update_signal.connect(self.env_tab.log)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.finished_signal.connect(self.env_tab.on_task_finished)
        self.worker.start()
    
    def browse_project_path(self, folder_path_default=None):
        if folder_path_default:
            folder_path = folder_path_default
        else:
            folder_path = QFileDialog.getExistingDirectory(
                self,
                "Select project folder",
                self.current_dir
            )

        if folder_path:
            if not folder_path_default:
                self.project_path.setText(folder_path)

            # Cập nhật thư mục làm việc hiện tại
            os.chdir(folder_path)
            
            if folder_path:
                self.browse_button.setText("Change project directory")
                
            self.close_project.setVisible(True)
                
            setting_path = os.path.join(folder_path, "config", "settings.py")
            self.github_frame.setVisible(not os.path.exists(setting_path))
            self.structure_tab.setVisible(os.path.exists(setting_path))
            
            if not os.path.exists(setting_path):
                self.tab_widget.clear()
                self.tab_widget.addTab(self.env_tab, "Environment")
            else:
                self.tab_widget.clear()
                self.tab_widget.addTab(self.env_tab, "Environment")
                self.tab_widget.addTab(self.structure_tab, "Project structure")
            
            self.tab_widget.setCurrentIndex(0)
            
            # Thông báo cho các tab biết đường dẫn đã thay đổi
            self.env_tab.log(f"Project folder selected: {folder_path}", "info")
            
            # Cập nhật cấu trúc cây cho cả hai tab
            self.env_tab.env_name.setEnabled(True)
            self.env_tab.create_button.setEnabled(True)
            self.structure_tab.new_app_name.setEnabled(True)
            self.structure_tab.verbose_name.setEnabled(True)
            self.env_tab.requirements_button.setEnabled(True)
            self.structure_tab.add_app_button.setEnabled(True)
            self.structure_tab.refresh_button.setVisible(True)
            self.structure_tab.tree_widget.setVisible(True)
            self.structure_tab.update_tree_from_folder()
            self.env_tab.reset_progress_bar()
            self.title_bar.updateTitle(folder_path)