
def services_template(app_name):
    app_name_capitalize = app_name.capitalize()

    return f"""from utils.decorators import singleton
from django.db import models

from ..models import {app_name_capitalize}


@singleton
class {app_name_capitalize}Service:
    {app_name}_objects = {app_name_capitalize}.objects

    def get_{app_name}s(self, keyword=None, **kwargs):
        filter_query = models.Q()

        if keyword and keyword.strip():
            keyword = keyword.strip()

        {app_name}s = self.{app_name}_objects.filter(filter_query)

        order_by = str(kwargs.get("order_by") or "asc").lower()

        if order_by == "asc":
            {app_name}s = {app_name}s.order_by("created_at")
        else:
            {app_name}s = {app_name}s.order_by("-created_at")

        return {app_name}s

    def get_{app_name}_by_id(self, id: int):
        return self.{app_name}_objects.get(pk=id)

    def delete_{app_name}_by_id(self, id: int):
        instance = self.{app_name}_objects.get(pk=id)
        instance.delete()

    def create_{app_name}(self, **kwargs):
        instance = self.{app_name}_objects.create(**kwargs)
        return instance

    def update_{app_name}(self, instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)

        instance.save()

        return instance
"""