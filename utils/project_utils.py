import os
import re
from utils.file_utils import create_file, read_file
from utils.templates.apps import apps_template
from utils.templates.doc import docs_template
from utils.templates.request import request_serializer_template, response_serializer_template
from utils.templates.service import services_template
from utils.templates.urls import url_template
from utils.templates.views import views_template


def update_settings_file(project_path, app_name, logger=None):
    """Cập nhật file settings.py để thêm ứng dụng vào INSTALLED_APPS"""
    # Tìm file settings.py
    # Sử dụng file settings.py đầu tiên tìm thấy
    settings_path = os.path.join(project_path, "config", 'settings.py')

    try:
        # Đọc nội dung file settings.py
        settings_content = read_file(settings_path)

        # Kiểm tra xem ứng dụng đã được thêm vào chưa
        app_pattern = r"['\"]apps\.{}['\"]".format(app_name)
        if re.search(app_pattern, settings_content):
            logger(f"The application 'apps.{app_name}' already exists in INSTALLED_APPS", "error")
            return True

        # Tìm vị trí INSTALLED_APPS trong file
        installed_apps_pattern = r"INSTALLED_APPS\s*=\s*\[([^\]]*)\]"
        # Cũng hỗ trợ định dạng sử dụng dấu ngoặc tròn
        if "INSTALLED_APPS = (" in settings_content:
            installed_apps_pattern = r"INSTALLED_APPS\s*=\s*\(([^\)]*)\)"

        match = re.search(installed_apps_pattern, settings_content, re.DOTALL)
        if not match:
            logger("Unable to determine format of INSTALLED_APPS", "error")
            return False

        apps_content = match.group(1)

        # Thêm app mới vào danh sách
        if apps_content.strip().endswith(','):
            # Nếu có dấu phẩy cuối cùng thì thêm vào
            new_app = f"    'apps.{app_name}',\n"
        else:
            # Nếu không có dấu phẩy thì thêm dấu phẩy vào
            new_app = f",\n    'apps.{app_name}',\n"

        # Vị trí chèn app mới
        insert_pos = match.start(1) + len(apps_content)

        # Tạo nội dung mới
        new_settings_content = settings_content[:insert_pos] + \
            new_app + settings_content[insert_pos:]

        # Ghi lại file settings.py
        create_file(settings_path, new_settings_content)

        logger(f"Added 'apps.{app_name}' to INSTALLED_APPS", "success")
        return True
    except Exception as e:
        logger(f"Error updating settings.py file: {str(e)}", "error")
        return False


def create_django_app_files(project_path, app_name, verbose_name=None, logger=None):
    """Tạo các thư mục và file cho một ứng dụng Django"""
    if verbose_name is None:
        verbose_name = app_name.capitalize()

    try:
        # Tạo thư mục ứng dụng
        app_path = os.path.join(project_path, "apps", app_name)
        os.makedirs(app_path, exist_ok=True)

        # Tạo các thư mục con
        dirs = ["docs", "migrations", "models", "serializers", "services", "views"]
        for dir_name in dirs:
            dir_path = os.path.join(app_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)

            # Thêm file __init__.py nếu chưa tồn tại
            init_file = os.path.join(dir_path, "__init__.py")
            if not os.path.exists(init_file):
                create_file(init_file, "")
            
            if dir_name == "views":
                # Thêm file {app_name}_view.py nếu chưa tồn tại
                view_file = os.path.join(dir_path, f"{app_name}_view.py")
                if not os.path.exists(view_file):
                    create_file(view_file, views_template(app_name))
                
                continue
            
            if dir_name == "serializers":
                # Thêm file request_serializer.py nếu chưa tồn tại
                request_file = os.path.join(dir_path, f"request_serializer.py")
                if not os.path.exists(request_file):
                    create_file(request_file, request_serializer_template(app_name))
                
                # Thêm file response_serializer.py nếu chưa tồn tại
                response_file = os.path.join(dir_path, f"response_serializer.py")
                if not os.path.exists(response_file):
                    create_file(response_file, response_serializer_template(app_name))

                continue
            
            if dir_name == "services":
                # Thêm file {app_name}_service.py nếu chưa tồn tại
                service_file = os.path.join(dir_path, f"{app_name}_service.py")
                if not os.path.exists(service_file):
                    create_file(service_file, services_template(app_name))
            
            if dir_name == "docs":
                # Thêm file {app_name}_swagger.py nếu chưa tồn tại
                doc_file = os.path.join(dir_path, f"{app_name}_swagger.py")
                if not os.path.exists(doc_file):
                    create_file(doc_file, docs_template(app_name))
            
        # Tạo file __init__.py trong thư mục ứng dụng nếu chưa tồn tại
        init_file = os.path.join(app_path, "__init__.py")
        if not os.path.exists(init_file):
            create_file(init_file, "")

        # Tạo file admin.py
        create_file(os.path.join(app_path, "admin.py"), "from django.contrib import admin\n\n# Register your models here.\n")

        # Tạo file apps.py với cấu hình đúng và verbose_name
        create_file(os.path.join(app_path, "apps.py"), apps_template(app_name, verbose_name))

        # Tạo file urls.py
        create_file(os.path.join(app_path, "urls.py"), url_template(app_name))
        
        return True
    except Exception as e:
        logger(f"Error when creating folders and files for the application '{app_name}': {str(e)}", "error")
        return False
