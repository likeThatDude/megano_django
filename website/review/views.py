from catalog.models import Review
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import serializers


class ReviewListSet(ListAPIView):
    """
    Представление для получения списка отзывов для конкретного товара.

    Атрибуты:
        serializer_class (Serializer): Сериализатор для представления отзывов.
        permission_classes (tuple): Классы разрешений, определяющие доступ.
    """

    serializer_class = serializers.ReviewListSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        Получает набор отзывов для указанного товара по его идентификатору.

        Возвращает:
            QuerySet: Набор запросов, содержащий отзывы для конкретного товара.
        """
        product_id = self.kwargs["product_id"]
        reviews = Review.objects.select_related("product", "user").filter(product__pk=product_id)
        return reviews


class ReviewCreateView(CreateAPIView):
    """
    Представление для создания нового отзыва.

    Атрибуты:
        queryset (QuerySet): Набор запросов для всех отзывов.
        serializer_class (Serializer): Сериализатор для создания отзывов.
        permission_classes (tuple): Классы разрешений, определяющие доступ.
    """

    queryset = Review.objects.all()
    serializer_class = serializers.ReviewCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """
        Сохраняет новый отзыв с привязкой к текущему пользователю.

        Параметры:
            serializer (ReviewCreateSerializer): Сериализатор, содержащий данные нового отзыва.
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для создания нового отзыва.

        Параметры:
            request (Request): Объект запроса.
            *args: Неименованные аргументы.
            **kwargs: Именованные аргументы.

        Возвращает:
            Response: Ответ с данными созданного отзыва и статусом 201.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        print(serializer.data)
        response_serializer = serializers.ReviewCreateResponseSerializer(serializer.instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ReviewUpdateViewSet(UpdateAPIView):
    """
    Представление для обновления существующего отзыва.

    Атрибуты:
        queryset (QuerySet): Набор запросов для всех отзывов.
        serializer_class (Serializer): Сериализатор для обновления отзывов.
        permission_classes (tuple): Классы разрешений, определяющие доступ.
    """

    queryset = Review.objects.select_related("user").all()
    serializer_class = serializers.ReviewUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        """
        Обрабатывает запрос на обновление отзыва.

        Параметры:
            request (Request): Объект запроса.
            *args: Неименованные аргументы.
            **kwargs: Именованные аргументы.

        Возвращает:
            Response: Ответ с данными обновленного отзыва.
        """
        obj = self.get_object()
        if obj.user != request.user:
            raise PermissionDenied("Ты не владелец этого объекта.")
        else:
            obj.updating = True
            obj.save(update_fields=["updating"])
        return super().update(request, *args, **kwargs)


class ReviewDeleteViewSet(DestroyAPIView):
    """
    Представление для удаления отзыва.

    Атрибуты:
        queryset (QuerySet): Набор запросов для всех отзывов.
        serializer_class (Serializer): Сериализатор для удаления отзывов.
        permission_classes (tuple): Классы разрешений, определяющие доступ.
    """

    queryset = Review.objects.select_related("user").all()
    serializer_class = serializers.ReviewDeleteSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        description="Удаление комментария",
    )
    def delete(self, request, *args, **kwargs):
        """
        Обрабатывает запрос на удаление отзыва.

        Параметры:
            request (Request): Объект запроса.
            *args: Неименованные аргументы.
            **kwargs: Именованные аргументы.

        Возвращает:
            Response: Ответ с кодом 204 при успешном удалении.
        """
        return super().delete(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет отзыв, если пользователь является его владельцем.

        Параметры:
            request (Request): Объект запроса.
            *args: Неименованные аргументы.
            **kwargs: Именованные аргументы.

        Возвращает:
            Response: Ответ с кодом 204 при успешном удалении или 400 при ошибке.
        """
        instance = self.get_object()
        if instance.user.id == request.user.id:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
