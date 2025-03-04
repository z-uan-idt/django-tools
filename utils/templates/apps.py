def apps_template(app_name, verbose_name):
    class_name = app_name.capitalize() + "Config"
            
    return f"""from django.apps import AppConfig


class {class_name}(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
    verbose_name = '{verbose_name}'
"""