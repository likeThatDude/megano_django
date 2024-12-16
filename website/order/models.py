from catalog.models import Delivery
from catalog.models import Payment
from catalog.models import Product
from catalog.models import Seller
from custom_auth.models import Profile
from django.db import models
from django.db.models import PROTECT
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from website import settings


class Order(models.Model):
    """
    Модель для хранения информации о заказах пользователей.

    Этот класс представляет заказ пользователя, содержащий информацию о доставке, статусе, стоимости и других деталях.
    Каждый заказ может быть в одном из нескольких состояний (например, в процессе обработки или доставлен).
    Каждый заказ связан с конкретным пользователем.

    Атрибуты:
        user (ForeignKey): Ссылка на пользователя, сделавшего заказ.
        delivery_city (CharField): Город, в который будет доставлен заказ.
        delivery_address (TextField): Адрес для доставки.
        recipient_phone (CharField): Телефон получателя заказа.
        recipient_email (EmailField): Email получателя заказа.
        status (CharField): Статус заказа, выбирается из заранее заданных вариантов.
        archived (BooleanField): Указывает, является ли заказ архивированным.
        created_at (DateTimeField): Дата и время создания заказа.
        updated_at (DateTimeField): Дата и время последнего обновления заказа.
        total_price (DecimalField): Общая стоимость заказа.
        comment (TextField): Комментарий к заказу.
        delivery_price (ForeignKey): Ссылка на цену доставки для этого заказа.

    Метаданные:
        уникальность данных не гарантируется, но статус заказа можно изменять по мере обработки.
    """

    PENDING = "OP"
    PROCESSING = "PR"
    SHIPPED = "SH"
    DELIVERED = "DL"
    CANCELLED = "CN"

    STATUS_CHOICES = (
        (PENDING, _("The order is awaiting processing")),
        (PROCESSING, _("The order is in progress")),
        (SHIPPED, _("The order has been sent")),
        (DELIVERED, _("The order has been delivered")),
        (CANCELLED, _("The order has been cancelled")),
    )

    PAID = "PD"
    PARTLY_PAID = "PP"
    UNPAID = "UN"

    PAID_CHOICES = (
        (PAID, _("The order has been paid for")),
        (PARTLY_PAID, _("The order has been partially paid for")),
        (UNPAID, _("The order has not been paid")),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"), related_name="orders"
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    delivery_city = models.CharField(max_length=255, verbose_name=_("Delivery city"))
    delivery_address = models.TextField(max_length=500, verbose_name=_("Delivery address"))
    recipient_phone = models.CharField(max_length=15, verbose_name=_("Recipient phone number"))
    recipient_email = models.EmailField(verbose_name=_("Recipient email"))
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=PENDING)
    archived = models.BooleanField(default=False, verbose_name=_("Archived"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    total_price = models.DecimalField(null=False, max_digits=10, decimal_places=2, verbose_name=_("Total price"))
    comment = models.TextField(max_length=1000, null=True, blank=True, verbose_name=_("Comment"))
    delivery_price = models.ForeignKey("DeliveryPrice", on_delete=PROTECT, verbose_name=_("Delivery price"))
    paid_status = models.CharField(max_length=2, choices=PAID_CHOICES, default=UNPAID)

    def __str__(self):
        return f"Order: {self.id}"

    def get_absolute_url(self):
        return reverse("order:order_detail", kwargs={"pk": self.id})


class OrderItem(models.Model):
    """
    Модель для хранения информации о товаре в рамках заказа.

    Этот класс представляет товар, добавленный в заказ. Каждый товар имеет ссылку на продавца, тип доставки, способ оплаты, а также
    информацию о количестве и цене. Один заказ может содержать несколько товаров.

    Атрибуты:
        seller (ForeignKey): Ссылка на продавца товара.
        product (ForeignKey): Ссылка на товар, добавленный в заказ.
        quantity (IntegerField): Количество товара в заказе.
        price (DecimalField): Цена товара в заказе.
        delivery (ForeignKey): Ссылка на тип доставки для товара.
        payment_type (ForeignKey): Ссылка на способ оплаты для товара.
        order (ForeignKey): Ссылка на заказ, к которому относится товар.
        active (BooleanField): Указывает, активен ли товар в заказе.
        payment_status (BooleanField): Указывает, оплачен ли товар.

    Метаданные:
        Один заказ может содержать несколько товаров. Связь с заказом через `related_name="order_items"`.
    """

    seller = models.ForeignKey(Seller, on_delete=models.PROTECT, verbose_name=_("Seller"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    quantity = models.IntegerField(verbose_name=_("Quantity"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"), default=0.00)
    delivery = models.ForeignKey(Delivery, on_delete=models.PROTECT, verbose_name=_("Delivery"))
    payment_type = models.ForeignKey(Payment, on_delete=models.PROTECT, verbose_name=_("Payment type"))
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.PROTECT, verbose_name=_("Order"))
    active = models.BooleanField(default=True, verbose_name=_("Active"))
    payment_status = models.BooleanField(default=False, verbose_name=_("Payment status"))
    receipt_url = models.CharField(max_length=255, null=False, default="", verbose_name=_("Receipt url"))

    def __str__(self):
        return f"{self.product}, {self.seller}, {self.quantity}, {self.price}"


class DeliveryPrice(models.Model):
    """
    Модель для хранения информации о типах доставки и их ценах.

    Этот класс представляет различные варианты доставки с ценами. Типы доставки могут включать бесплатную, стандартную или экспресс-доставку.

    Атрибуты:
        name (CharField): Тип доставки, выбирается из предустановленных вариантов.
        price (DecimalField): Цена выбранного типа доставки.

    Метаданные:
        `name` уникален для каждого типа доставки и индексируется для быстрого поиска.
    """

    FREE_DELIVERY = "FD"
    STANDARD_DELIVERY = "SD"
    EXPRESS_DELIVERY = "ED"

    DELIVERY_PRICE_CHOICES = (
        (FREE_DELIVERY, _("Free delivery")),
        (STANDARD_DELIVERY, _("Standard delivery")),
        (EXPRESS_DELIVERY, _("Express delivery")),
    )
    name = models.CharField(
        max_length=2,
        choices=DELIVERY_PRICE_CHOICES,
        default=FREE_DELIVERY,
        verbose_name=_("Delivery price"),
        db_index=True,
        unique=True,
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))

    def __str__(self):
        return str(dict(self.DELIVERY_PRICE_CHOICES).get(self.name))
