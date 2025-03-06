def firstupper(value: str):
    return value[0].upper() + value[1:]


def apps_template(app_name, verbose_name):
    class_name = firstupper(app_name) + "Config"
            
    return f"""from django.apps import AppConfig


class {class_name}(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
    verbose_name = '{verbose_name}'
"""