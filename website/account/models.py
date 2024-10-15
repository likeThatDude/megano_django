from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from catalog.models import Product


class Review(models.Model):
    """
    Модель отзыва
    product: товар к которому относится данный отзыв
    user: пользователь, который оставил отзыв #TODO после создания модели CustomUser заменить связанную
    text: текст отзыва
    created_at: время создания отзыва (создается автоматически)
    """

    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    text = models.TextField(verbose_name=_("Text"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
