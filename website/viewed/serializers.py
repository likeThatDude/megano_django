from rest_framework import serializers

from .models import Viewed


class ViewedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Viewed
        fields = "__all__"
