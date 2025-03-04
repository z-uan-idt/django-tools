def model_template(app_name):
    app_name_capitalize = app_name.capitalize()

    return f"""from django.db import models


class {app_name_capitalize}(models.Model):
    pass
"""