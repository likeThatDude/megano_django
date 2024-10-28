from django.db import models
from django.utils.translation import gettext_lazy as _

from account.models import Profile


class Order(models.Model):
    """
    Модель заказа
    customer: связь с профилем пользователя
    delivery_city: город получателя
    delivery_address: адрес доставки
    comment: комментарий
    status: статус заказа
    payment_method: метод оплаты
    delivery_method: метод доставки
    archived: доступен ли к заказу
    created_at: дата, когда создан заказ

    """
    PENDING = "Pending"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"

    STATUS_CHOICES = {
        PENDING: _("Pending"),        # Заказ ожидает обработки
        PROCESSING: _("Processing"),  # Заказ в процессе выполнения
        SHIPPED: _("Shipped"),        # Заказ отправлен
        DELIVERED: _("Delivered"),    # Заказ доставлен
        CANCELLED: _("Cancelled"),    # Заказ отменен
    }
    PAYMENT_METHODS = (
        ("BANKNOTES", _("Banknotes")),    # Оплата наличными
        ("CARD", _("Bank card")),         # Оплата картой
        ("ONLINE", _("Online payment")),  # Онлайн оплата (электронный кошелек, СБП)
    )
    DELIVERY_METHOD = (
        ("COURIER", _("Courier")),           # Доставка курьером
        ("PICKUP", _("Pickup")),             # Самовывоз
        ("POST", _("Postal service")),       # Доставка почтой
    )

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name=_("Profile")
    )
    delivery_city = models.CharField(
        max_length=255,
        verbose_name=_("Delivery city")
    )
    delivery_address = models.TextField(
        max_length=500,
        verbose_name=_("Delivery address")
    )
    comment = models.TextField(
        max_length=1000,
        verbose_name=_("Comment")
    )
    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    payment_method = models.CharField(
        max_length=100,
        choices=PAYMENT_METHODS
    )
    delivery_method = models.CharField(
        max_length=100,
        choices=DELIVERY_METHOD
    )
    archived = models.BooleanField(
        default=False,
        verbose_name=_("Archived")
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
