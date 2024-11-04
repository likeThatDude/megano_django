from catalog.models import Product
from django.db import models
from django.utils.translation import gettext_lazy as _

from website import settings


class Comparison(models.Model):
    """
    Модель для хранения товаров, добавленных в список сравнения пользователем.

    Этот класс представляет связь между пользователем и товаром в контексте
    функции сравнения товаров. Каждый пользователь может добавлять товары
    в список сравнения, и каждая пара "пользователь-товар" должна быть уникальной.

    Атрибуты:
        user (ForeignKey): Ссылка на модель пользователя, которая добавила товар в сравнение.
        product (ForeignKey): Ссылка на модель товара, добавленного в сравнение.

    Метаданные:
        unique_together (tuple): Ограничение, гарантирующее уникальность каждой комбинации
        пользователя и товара в списке сравнения.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"), db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Comparison product"), db_index=True)

    class Meta:
        unique_together = ("user", "product")
