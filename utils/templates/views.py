def views_template(app_name):
        app_name_capitalize = app_name.capitalize()
        service_name = app_name_capitalize + "Service"
        class_name = app_name_capitalize + "ViewAPI"

        return f"""from rest_framework.permissions import IsAuthenticated
from utils.views import APIGenericView
from django.db import transaction

from utils.decorators import api

from ..serializers import request_serializer, response_serializer
from ..services.{app_name}_service import {service_name}
from ..docs import {app_name}_swagger


class {class_name}(APIGenericView):
    permission_classes = [IsAuthenticated]
    
    {app_name}_service = {service_name}()

    action_serializers = {{
        "list_request": request_serializer.List{app_name_capitalize}Serializer,
        "list_response": response_serializer.{app_name_capitalize}Serializer,
        "create_request": request_serializer.{app_name_capitalize}Serializer,
        "create_response": response_serializer.{app_name_capitalize}Serializer,
        "update_request": request_serializer.{app_name_capitalize}Serializer,
        "update_response": response_serializer.{app_name_capitalize}Serializer,
        "retrieve_response": response_serializer.{app_name_capitalize}Serializer,
    }}

    @api.swagger(
        tags=["{app_name_capitalize}"],
        operation_id='{app_name_capitalize} List',
        manual_parameters=[
            {app_name}_swagger.PAGE_PARAMETER,
            {app_name}_swagger.LIMIT_PARAMETER,
            {app_name}_swagger.KEYWORD_PARAMETER,
            {app_name}_swagger.ORDER_BY_PARAMETER,
        ]
    )
    def list(self, request):
        serializer = self.get_request_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        {app_name}s = self.{app_name}_service.get_{app_name}s(**serializer.validated_data)
        return self.paginator({app_name}s, many=True)

    @api.swagger(
        tags=["{app_name_capitalize}"],
        operation_id='{app_name_capitalize} Create'
    )
    @transaction.atomic
    def create(self, request):
        serializer = self.get_request_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return self.get_response_serializer(instance).data

    @api.swagger(
        tags=["{app_name_capitalize}"],
        operation_id='{app_name_capitalize} Detail'
    )
    def retrieve(self, request, pk):
        instance = self.{app_name}_service.get_{app_name}_by_id(pk)
        return self.get_response_serializer(instance).data

    @api.swagger(
        tags=["{app_name_capitalize}"],
        operation_id='{app_name_capitalize} Delete'
    )
    @transaction.atomic
    def destroy(self, request, pk):
        self.{app_name}_service.delete_{app_name}_by_id(pk)

    @api.swagger(
        tags=["{app_name_capitalize}"],
        operation_id='{app_name_capitalize} Update'
    )
    @transaction.atomic
    def update(self, request, pk):
        instance = self.{app_name}_service.get_{app_name}_by_id(pk)
        serializer = self.get_request_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        {app_name} = serializer.save()
        return self.get_response_serializer({app_name}).data
"""