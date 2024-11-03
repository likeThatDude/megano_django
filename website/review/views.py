from catalog.models import Review
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import serializers


class ReviewCreateView(CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        print(serializer.data)
        response_serializer = serializers.ReviewCreateResponseSerializer(serializer.instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ReviewUpdateViewSet(UpdateAPIView):
    queryset = Review.objects.select_related('user').all()
    serializer_class = serializers.ReviewUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            raise PermissionDenied("Ты не владелец этого объекта.")
        else:
            obj.updating = True
            obj.save(update_fields=['updating'])
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description='Полное изменение данных',
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        description='Частичное изменение данных',
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ReviewDeleteViewSet(DestroyAPIView):
    queryset = Review.objects.select_related('user').all()
    serializer_class = serializers.ReviewDeleteSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        description='Удаление комментария',
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user.id == request.user.id:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
