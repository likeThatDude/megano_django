from rest_framework import serializers

from .models import Product
from .models import Review
from .models import Viewed


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class ReviewFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["user", "text", "created_at"]


class ViewedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Viewed
        fields = "__all__"
