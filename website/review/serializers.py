from django.db.models import Q
from rest_framework import serializers

from account.models import CustomUser
from catalog.models import Review
from website import settings


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

class UserReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['pk', 'login',]

class ReviewListSerializer(serializers.ModelSerializer):
    user = UserReviewSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['pk', 'user', 'text', 'created_at', 'update_at', 'updating',]
        ordering = ('-created_at',)

