from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager


def category_icon_directory_path(instance: "Category", filename: str) -> str:
    return "products/category_{name}/images/{filename}".format(
        name=instance.name,
        filename=filename,
    )


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to=category_icon_directory_path)
    archived = models.BooleanField(default=False)
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_category'
    )

    if TYPE_CHECKING:
        objects: Manager


class Product(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=True, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    manufacture = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    discount = models.SmallIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    archived = models.BooleanField(default=False)
    limited_edition = models.BooleanField(default=False)
    view = models.BooleanField(default=False)

    if TYPE_CHECKING:
        objects: Manager


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product,
        filename=filename,
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_images_directory_path)

    if TYPE_CHECKING:
        objects: Manager


