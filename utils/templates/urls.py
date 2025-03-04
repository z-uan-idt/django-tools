def url_template(app_name):
    app_name_capitalize = app_name.capitalize()
    api_view_name = app_name_capitalize + "ViewAPI"

    return f"""from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views.{app_name}_view import {api_view_name}


v1_api_router = DefaultRouter(trailing_slash=False)
v1_api_router.register(prefix="{app_name}", viewset={api_view_name}, basename="{app_name}")

{app_name}_urlpatterns = [
    path("api/v1/", include(v1_api_router.urls)),
]
"""