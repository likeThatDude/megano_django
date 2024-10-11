from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Manager


def category_icon_directory_path(instance: "Category", filename: str) -> str:
    """Путь для сохранения иконки категории"""
    return "products/category_{name}/images/{filename}".format(
        name=instance.name,
        filename=filename,
    )


class Category(models.Model):
    """
    Модель категории товара
    name: название категории
    icon: иконка категории
    archived: статус архива категории
    parent_category: ссылка на родительскую категорию (если значение не NULL, то это подкатегория категория)
    """
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to=category_icon_directory_path)
    archived = models.BooleanField(default=False)
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_category",
    )

    if TYPE_CHECKING:
        objects: Manager


class Product(models.Model):
    """
    Модель товара
    name: имя товара
    description: описание товара
    manufacture: производитель товара
    created_at: когда создан товар
    category: категория товара (Category)
    archived: статус архива товара
    limited_edition: статус ограниченности предложения товара
    view: статус просмотра товара
    """
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=True, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    manufacture = models.CharField(max_length=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    archived = models.BooleanField(default=False)
    limited_edition = models.BooleanField(default=False)
    view = models.BooleanField(default=False)

    if TYPE_CHECKING:
        objects: Manager


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    """Путь для сохранения изображений товаров"""
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product,
        filename=filename,
    )


class ProductImage(models.Model):
    """
    Модель изображения товара
    product: ссылка на товар к которому относится фотография (Product)
    image: изображение товара
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_images_directory_path)

    if TYPE_CHECKING:
        objects: Manager
