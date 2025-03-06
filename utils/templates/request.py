def firstupper(value: str):
    return value[0].upper() + value[1:]


def request_serializer_template(app_name):
    app_name_capitalize = firstupper(app_name)

    return f"""from rest_framework import serializers
from utils.paginator import Paginator

from ..models import {app_name_capitalize}
from ..services.{app_name}_service import {app_name_capitalize}Service


class List{app_name_capitalize}Serializer(serializers.Serializer):
    page = serializers.IntegerField(
        default=Paginator.DEFAULT_PAGE,
        required=False,
    )
    limit = serializers.IntegerField(
        default=Paginator.DEFAULT_PER_PAGE,
        required=False,
    )
    keyword = serializers.CharField(
        allow_blank=True,
        required=False,
        default="",
    )
    order_by = serializers.CharField(
        allow_blank=True,
        required=False,
        default="",
    )
       
 
class {app_name_capitalize}Serializer(serializers.ModelSerializer):

    class Meta:
        model = {app_name_capitalize}
        service = {app_name_capitalize}Service()
        fields = '__all__'
    
    def create(self, validated_data):
        return self.Meta.service.create_{app_name}(**validated_data)
    
    def update(self, instance, validated_data):
        return self.Meta.service.update_{app_name}(instance, **validated_data)
"""

def response_serializer_template(app_name):
    app_name_capitalize = firstupper(app_name)

    return f"""from rest_framework import serializers

from ..models import {app_name_capitalize}


class {app_name_capitalize}Serializer(serializers.ModelSerializer):

    class Meta:
        model = {app_name_capitalize}
        fields = '__all__'
"""