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
        
        # Add maximize/restore button
        self.btn_maximize = QPushButton("□")  # Square symbol for maximize
        self.btn_maximize.setStyleSheet("color: #000000; padding: 0 0 2px 2px")
        self.btn_maximize.setFixedSize(30, 30)
        self.btn_maximize.clicked.connect(self.toggleMaximized)
        
        self.btn_close = QPushButton("×")
        self.btn_close.setStyleSheet("color: #000000; padding: 0 0 2px 2px")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.clicked.connect(self.parent().close)
        
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_maximize) 
        layout.addWidget(self.btn_close)
        
        # Biến để theo dõi vị trí chuột khi kéo cửa sổ
        self.m_drag = False
        self.startPos = None
    
    # Toggle maximized/normal state
    def toggleMaximized(self):
        parent = self.window()
        if parent.isMaximized():
            parent.showNormal()
            self.updateMaximizeButton(False)
        else:
            parent.showMaximized()
            self.updateMaximizeButton(True)
    
    # Update maximize button appearance based on state
    def updateMaximizeButton(self, is_maximized):
        if is_maximized:
            # Use a "restore down" symbol (⧉) when maximized
            self.btn_maximize.setText("⧉")
            # Alternative symbols if the above doesn't display correctly: ▣ or ❐
        else:
            # Use a "maximize" symbol (□) when in normal state
            self.btn_maximize.setText("□")
    
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
        self.screen_width = screen.width() - 100
        self.screen_height = screen.height() - 200
        self.setGeometry(50, 100, self.screen_width, self.screen_height)
        self.setMinimumSize(self.screen_width, self.screen_height)
        
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

        self.tab_widget.clear()
        self.tab_widget.addTab(self.env_tab, "Project Setup")
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
        
        # Handle Git URL formatting
        if not github_path.endswith(".git"):
            github_path_git = github_path + ".git"
        else:
            github_path_git = github_path
        
        project_path = self.project_path.text().strip()
        project_name_dir = os.path.join(project_path, project_name)
        
        # Check if we need to remove the .git directory (for django-base repos)
        is_django_base = "django-base" in github_path_git
        
        self.progress.setValue(0)
        self.env_tab.log(f"Pulling code from {github_path}...", "info")

        def run_clone_code(update_signal, progress_signal, finished_signal):
            try:
                # Signal initial progress
                progress_signal.emit(30)
                
                # First, create the directory if it doesn't exist
                os.makedirs(project_path, exist_ok=True)
                
                # Clone the repository
                clone_cmd = ["git", "clone", github_path_git, project_name]
                
                # Execute the git clone command
                process = subprocess.Popen(
                    clone_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=project_path,  # Set the working directory
                    bufsize=1  # Line buffered
                )
                
                # Platform-independent output reading approach
                import threading
                import queue
                
                output_queue = queue.Queue()
                
                def read_output(stream, queue, stream_name):
                    for line in iter(stream.readline, ''):
                        if line:
                            queue.put((stream_name, line.strip()))
                    stream.close()
                
                # Start threads to read stdout and stderr
                stdout_thread = threading.Thread(
                    target=read_output, 
                    args=(process.stdout, output_queue, "stdout")
                )
                stderr_thread = threading.Thread(
                    target=read_output, 
                    args=(process.stderr, output_queue, "stderr")
                )
                
                stdout_thread.daemon = True
                stderr_thread.daemon = True
                stdout_thread.start()
                stderr_thread.start()
                
                # Process output from both streams
                while process.poll() is None or not output_queue.empty():
                    try:
                        stream_name, line = output_queue.get(timeout=0.1)
                        if line:
                            update_signal.emit(line, "black")
                            if stream_name == "stderr":
                                # Check for progress info
                                match = re.search(r'Receiving objects:\s+(\d+)%', line)
                                if match:
                                    percentage = int(match.group(1))
                                    progress_signal.emit(30 + int(percentage * 0.5))  # Scale to 30-80%
                        output_queue.task_done()
                    except queue.Empty:
                        pass
                
                # Wait for process to complete
                process.wait()
                
                # Make sure threads are done
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)
                
                # Process complete, check result
                if process.returncode == 0:
                    update_signal.emit("Git clone completed successfully", "green")
                    progress_signal.emit(80)
                    
                    # Remove .git directory if needed
                    if is_django_base and os.path.exists(os.path.join(project_name_dir, ".git")):
                        try:
                            # Inside run_clone_code function where you handle git removal:
                            is_remove = github_path_git.endswith("django-base") or github_path_git.endswith("django-base.git")

                            if is_remove:
                                update_signal.emit("Removing .git directory for django-base template...", "info")
                                success = self.remove_git_directory(project_name_dir, update_signal)
                                if not success:
                                    update_signal.emit("Warning: Could not fully remove .git directory. This won't affect your project.", "warning")
                            update_signal.emit("Removed .git directory", "black")
                        except Exception as e:
                            update_signal.emit(f"Warning: Could not remove .git directory: {str(e)}", "orange")
                    
                    # Update README if it exists
                    readme_path = os.path.join(project_name_dir, "README.md")
                    if os.path.exists(readme_path) and os.path.isfile(readme_path):
                        try:
                            with open(readme_path, 'r', encoding='utf-8') as f:
                                content_readme = f.read()
                            
                            if content_readme:
                                if "# Django Base Project" in content_readme:
                                    content_readme = content_readme.replace("# Django Base Project", f"# {project_name}")
                                
                                if "django-boilderpalte/" in content_readme:
                                    content_readme = content_readme.replace("django-boilderpalte/", f"{project_name}/")
                                
                                with open(readme_path, 'w', encoding='utf-8') as f:
                                    f.write(content_readme)
                                    
                                update_signal.emit("Updated README.md", "black")
                        except Exception as e:
                            update_signal.emit(f"Warning: Could not update README: {str(e)}", "orange")
                    
                    progress_signal.emit(100)
                    finished_signal.emit(True, "Pulled the code successfully")
                    
                    # Use a signal to update the UI
                    update_signal.emit("PROJECT_PATH:" + os.path.join(project_path, project_name), "command")
                else:
                    stderr_output = ""
                    while not output_queue.empty():
                        try:
                            stream_name, line = output_queue.get(timeout=0.1)
                            if stream_name == "stderr":
                                stderr_output += line + "\n"
                            output_queue.task_done()
                        except queue.Empty:
                            break
                    
                    update_signal.emit(f"Error: Git clone failed: {stderr_output}", "red")
                    progress_signal.emit(0)
                    finished_signal.emit(False, "Pulling code failed")
                    
            except Exception as e:
                import traceback
                traceback_str = traceback.format_exc()
                progress_signal.emit(0)
                update_signal.emit(f"Error: {str(e)}", "red")
                update_signal.emit(traceback_str, "red")
                finished_signal.emit(False, str(e))
        
        # Create and configure the worker thread
        self.worker = WorkerThread(run_clone_code)
        self.worker.update_signal.connect(self.handle_update_signal)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.finished_signal.connect(self.env_tab.on_task_finished)
        self.worker.start()
        
    def remove_git_directory(self, directory_path, update_signal):
        """Safely remove a .git directory even when locked files are present."""
        import shutil
        import os
        import time
        import subprocess
        import platform
        
        git_dir = os.path.join(directory_path, ".git")
        
        if not os.path.exists(git_dir):
            update_signal.emit("No .git directory found", "info")
            return True
        
        # Step 1: Try to use Python's shutil.rmtree with error handling
        try:
            def handle_readonly(func, path, exc_info):
                """Handle read-only files by making them writable first."""
                # Make the file/directory writable if that's the issue
                os.chmod(path, 0o777)
                # Then try the removal operation again
                func(path)
                
            update_signal.emit("Attempting to remove .git directory...", "info")
            shutil.rmtree(git_dir, onerror=handle_readonly)
            update_signal.emit("Successfully removed .git directory", "green")
            return True
        except Exception as e:
            update_signal.emit(f"First removal attempt failed: {str(e)}", "warning")
        
        # Step 2: Wait briefly and try again with Python
        time.sleep(1)
        try:
            shutil.rmtree(git_dir)
            update_signal.emit("Successfully removed .git directory on second attempt", "green")
            return True
        except Exception as e:
            update_signal.emit(f"Second removal attempt failed: {str(e)}", "warning")
        
        # Step 3: As a last resort, use the system's command-line tools
        try:
            update_signal.emit("Trying system commands to remove .git directory...", "info")
            
            if platform.system() == "Windows":
                # On Windows, use both rd and del commands for stubborn files
                subprocess.run(["attrib", "-r", "-s", "-h", "/S", "/D", git_dir], 
                            shell=True, check=False)
                
                subprocess.run(["rd", "/s", "/q", git_dir], 
                            shell=True, check=True)
            else:
                # On Unix-like systems (Linux, macOS)
                subprocess.run(["chmod", "-R", "777", git_dir], 
                            check=False)
                
                subprocess.run(["rm", "-rf", git_dir], 
                            check=True)
                
            update_signal.emit("Successfully removed .git directory using system commands", "green")
            return True
        except Exception as e:
            update_signal.emit(f"Failed to remove .git directory: {str(e)}", "red")
            return False

    def handle_update_signal(self, message, color):
        """Handle update signals from worker thread, including special commands"""
        if color == "command" and message.startswith("PROJECT_PATH:"):
            # Extract path and update UI safely
            path = message[len("PROJECT_PATH:"):]
            self.project_path.setText(path)
            self.browse_project_path(path)
            self.project_name.setText("django-base")
        else:
            # Normal log message
            self.env_tab.log(message, color)
        
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
                self.tab_widget.addTab(self.env_tab, "Project Setup")
            else:
                self.tab_widget.clear()
                self.tab_widget.addTab(self.env_tab, "Project Setup")
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