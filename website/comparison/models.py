from catalog.models import Product
from django.db import models
from django.utils.translation import gettext_lazy as _

from website import settings


class Comparison(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"), db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Product"), db_index=True)

    class Meta:
        unique_together = ('user', 'product')

