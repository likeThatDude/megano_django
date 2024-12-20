from catalog.models import Product
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class ComparisonAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(write_only=True)

    def validate_product_id(self, value):
        """
        Проверяем, существует ли продукт с данным ID.
        """
        try:
            product = Product.objects.get(pk=value)
            return product
        except Product.DoesNotExist:
            raise ValidationError(_(f"There is no product with id {value} in the database"))


class AnswerAddSerializer(serializers.Serializer):
    status = serializers.BooleanField(required=False, allow_null=True)
    title = serializers.CharField(max_length=20)
    text = serializers.CharField(max_length=100)

    def to_internal_value(self, data):
        if not isinstance(data.get("title"), str):
            data["title"] = str(data["title"])
        if not isinstance(data.get("text"), str):
            data["text"] = str(data["text"])
        return super().to_internal_value(data)

    def validate_status(self, value):
        """
        Проверяем значение status.
        """
        if value is not None and not isinstance(value, bool):
            raise serializers.ValidationError(_("Status must be a Boolean value or None"))
        return value
