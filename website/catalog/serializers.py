from rest_framework import serializers
from .models import Product, Review

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class ReviewFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['user', 'text', 'created_at']
