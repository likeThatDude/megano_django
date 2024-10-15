from django.utils.translation import gettext_lazy as _
from django.db import models


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
    parent_category: ссылка на родительскую категорию (если значение не NULL, то это подкатегория категории)
    """

    class Meta:
        verbose_name_plural = "categories"
        ordering = ("name",)

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    icon = models.FileField(
        upload_to="assets/img/icons/departments", verbose_name=_("Icon")
    )
    archived = models.BooleanField(default=False, verbose_name=_("Archived status"))
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_categories",
        verbose_name=_("PK category"),
    )


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

    name = models.CharField(max_length=100, db_index=True, verbose_name=_("Name"))
    description = models.TextField(
        null=True, blank=True, db_index=True, verbose_name=_("Description")
    )
    price = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, verbose_name=_("Price")
    )
    manufacture = models.CharField(
        max_length=100, db_index=True, verbose_name=_("Manufacture")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("'Created at"))
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_("PK category"),
        related_name="products",
    )
    archived = models.BooleanField(default=False, verbose_name=_("Archived status"))
    limited_edition = models.BooleanField(
        default=False, verbose_name=_("Limited edition")
    )
    view = models.BooleanField(default=False, verbose_name=_("View"))


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

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("PK product")
    )
    image = models.ImageField(
        upload_to=product_images_directory_path, verbose_name=_("Image product")
    )
