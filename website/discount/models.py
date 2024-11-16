from catalog.models import Category
from catalog.models import Product
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ProductGroup(models.Model):
    """
    Модель группы товаров. Используется как вспомогательная таблица для
    реализации вида скидка "Скидка на наборы(группы)".

    Attributes:
        name: название группы
        description: описание группы
        products: связь многие-ко-многим с товарами, которые относятся к данной группе
    """

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    archived = models.BooleanField(default=False, verbose_name=_("Archived status"))

    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="product_groups",
        verbose_name=_("Products"),
        db_table="discount_groups_products",
    )

    class Meta:
        verbose_name = _("Product group")
        verbose_name_plural = _("Product groups")
        ordering = ("name",)
        db_table = "discount_group"

    def __str__(self) -> str:
        return f"{self.pk}. {self.name}"


class Discount(models.Model):
    """
    Модель скидки

    Attributes:
        name: название скидки
        kind: вид скидки. Скидка может быть следующих видов:
            - Скидка на товар: скидка на список товаров и/или на категории товаров;
            - Скидка на наборы: применяется, если товары из корзины состоят в указанных группах;
            - Скидка на корзину: применяется, если общая стоимость товаров в корзине выше value и
                при этом количество товаров в диапазоне от quantity_gt до quantity_lt
        method: механизм скидки. Скидка может иметь следующие механизмы расчета:
            - Процент скидки;
            - Сумма скидки - сумма вычета из итоговой стоимости;
            - Фиксированная итоговая стоимость
        quantity_gt: наименьшее количество товаров в корзине. Поле используется только при выборе
            скидки на корзину
        quantity_lt: наибольшее количество товаров в корзине. Поле используется только при выборе
            скидки на корзину
        value: значение применяемой скидки. В зависимости от механизма скидки, тут могут храниться
            как проценты, так и значение цены
        description: описание скидки
        start_date: дата начала действия скидки
        end_date: дата окончания действия скидки
        is_active: статус актуальности скидки
        archived: механизм мягкого удаления скидки
        products: связь многие-ко-многим с продуктами, к которым применима скидка. Связь используется,
            если выбран вид скидки "Скидка на товар"
        categories: связь многие-ко-многим с категориями товаров, к которым применима скидка. Связь
            используется, если выбран вид скидки "Скидка на товар"
        product_groups: связь многие-ко-многим с группами товаров, к которым применима скидка. Связь
            используется, если выбран вид скидки "Скидка на наборы"
    """

    # виды скидок
    PRODUCT = "PT"
    SET = "ST"
    CART = "CT"

    KIND_CHOICES = [
        (PRODUCT, _("Скидка на товар")),
        (SET, _("Скидка на наборы")),
        (CART, _("Скидка на корзину")),
    ]

    # типы механизмов расчёта скидки
    PERCENT = "PT"
    SUMM = "SM"
    FIXED = "FD"

    METHOD_CHOICES = [
        (PERCENT, _("Процент скидки")),
        (SUMM, _("Сумма скидки")),
        (FIXED, _("Фиксированная стоимость")),
    ]

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    kind = models.CharField(max_length=2, choices=KIND_CHOICES, verbose_name=_("Вид скидки"))
    method = models.CharField(max_length=2, choices=METHOD_CHOICES, verbose_name=_("Механизм скидки"))
    quantity_gt = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Наименьшее количество"),
        help_text=_("Установите нижнюю границу количества товара/ов, если выбран вид 'Скидка на корзину'. "),
    )
    quantity_lt = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Наибольшее количество"),
        help_text=_("Установите верхнюю границу количества товара/ов, если выбран вид 'Скидка на корзину'. "),
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Значение"),
        help_text=_("В зависимости от механизма скидки, тут могут храниться как проценты, так и значение цены. "),
    )
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    start_date = models.DateField(default=timezone.now, verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is active?"))
    archived = models.BooleanField(default=False, verbose_name=_("Archived status"))

    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="discounts",
        verbose_name=_("Products"),
        db_table="discounts_products",
        help_text=_("Добавьте продукты, если выбран вид 'Скидка на товар'. "),
    )
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="discounts",
        verbose_name=_("Categories"),
        db_table="discounts_categories",
        help_text=_("Добавьте категории, если выбран вид 'Скидка на товар'. "),
    )
    product_groups = models.ManyToManyField(
        ProductGroup,
        blank=True,
        related_name="discounts",
        verbose_name=_("Product groups"),
        db_table="discounts_groups",
        help_text=_("Добавьте группы, если выбран вид 'Скидка на наборы'. "),
    )

    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")
        ordering = ("id",)
        db_table = "discount"

    def __str__(self) -> str:
        return f"{self.pk}. {self.name}"
