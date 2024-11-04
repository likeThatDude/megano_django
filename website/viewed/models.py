from catalog.models import Product
from django.conf import settings
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext_lazy as _


class Viewed(models.Model):
    """
    Модель таблицы просмотренных пользователем товаров.

    user: пользователь, который посмотрел товар;
    product: товар, который был просмотрен пользователем;
    created_at: дата/время просмотра товара.
    """

    class Meta:
        verbose_name = _("Viewed")
        verbose_name_plural = _("Viewed")
        ordering = ("-created_at",)
        constraints = [UniqueConstraint(fields=["user", "product"], name="user_product_unique")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name="viewed",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
        related_name="viewed",
    )
    created_at = models.DateTimeField(auto_now=True, verbose_name=_("Created_at"))
