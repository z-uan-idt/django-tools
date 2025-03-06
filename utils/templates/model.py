def firstupper(value: str):
    return value[0].upper() + value[1:]


def model_template(app_name):
    app_name_capitalize = firstupper(app_name)

    return f"""from django.db import models


class {app_name_capitalize}(models.Model):
    pass
"""