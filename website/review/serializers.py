from account.models import CustomUser
from catalog.models import Review
from django.db.models import Q
from rest_framework import serializers

from website import settings


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания нового отзыва.

    Поля:
        product (ForeignKey): Ссылка на товар, к которому относится отзыв.
        text (str): Текст отзыва.
    """

    class Meta:
        model = Review
        fields = (
            "product",
            "text"
        )


class ReviewCreateResponseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ответа на создание отзыва.

    Поля:
        pk (int): Первичный ключ созданного отзыва.
        text (str): Текст отзыва.
        created_at (datetime): Дата и время создания отзыва.
    """

    class Meta:
        model = Review
        fields = (
            "pk",
            "text",
            "created_at",
        )


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления существующего отзыва.

    Поля:
        pk (int): Первичный ключ отзыва.
        text (str): Обновленный текст отзыва.
    """

    class Meta:
        model = Review
        fields = (
            "pk",
            "text"
        )


class ReviewDeleteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для удаления отзыва.

    Поля:
        pk (int): Первичный ключ отзыва, который необходимо удалить.
    """

    class Meta:
        model = Review
        fields = (
            "pk",
        )


class UserReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователя, оставившего отзыв.

    Поля:
        pk (int): Первичный ключ пользователя.
        login (str): Логин пользователя.
    """

    class Meta:
        model = CustomUser
        fields = (
            "pk",
            "login",
        )


class ReviewListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка отзывов с информацией о пользователе.

    Поля:
        pk (int): Первичный ключ отзыва.
        user (UserReviewSerializer): Информация о пользователе, оставившем отзыв.
        text (str): Текст отзыва.
        created_at (datetime): Дата и время создания отзыва.
        update_at (datetime): Дата и время последнего обновления отзыва.
        updating (bool): Флаг, указывающий, находится ли отзыв в процессе обновления.
    """

    user = UserReviewSerializer(read_only=True)

    class Meta:
        model = Review
        fields = (
            "pk",
            "user",
            "text",
            "created_at",
            "update_at",
            "updating",
        )
        ordering = (
            "-created_at",
        )
