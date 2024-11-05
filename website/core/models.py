from catalog.models import Product
from django.db import models
from django.utils.translation import gettext_lazy as _


class Banner(models.Model):
    """
    Модель Banner представляет собой рекламный баннер, связанный с определённым продуктом.

    Поля:
    - product: Внешний ключ, указывающий на связанный продукт.
    - deadline_data: Дата, до которой баннер активен.
    - created_date: Дата создания баннера.
    - active: Логическое значение, показывающее, активен ли баннер.

    Связь:
    Один баннер может быть связан с одним продуктом, но продукт может иметь множество баннеров.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="banner",
        verbose_name=_("Product"),
    )
    deadline_data = models.DateField(verbose_name=_("Deadline Date"))
    created_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Created_date"))
    active = models.BooleanField(verbose_name=_("Active"), default=True)
