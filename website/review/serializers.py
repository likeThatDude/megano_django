from django.db.models import Q
from rest_framework import serializers
from catalog.models import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['product', 'text']


class ReviewCreateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['pk', 'text', 'created_at', ]


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('pk', 'text')


class ReviewDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('pk',)


class ReviewGoodResponseSerializer(serializers.Serializer):
    operation_status = serializers.BooleanField(default=True)
    update_data = serializers.DateTimeField(default=None)


class ReviewBadResponseSerializer(serializers.Serializer):
    operation_status = serializers.BooleanField(default=False)


class ReviewDeleteGoodResponseSerializer(serializers.Serializer):
    operation_status = serializers.BooleanField(default=True)


class ReviewDeleteBadResponseSerializer(serializers.Serializer):
    operation_status = serializers.BooleanField(default=True)
