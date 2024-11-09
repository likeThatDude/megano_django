from account.models import Profile
from django.db import models
from django.utils.translation import gettext_lazy as _

from website import settings
from catalog.models import Product, Seller, Delivery, Payment


class Order(models.Model):
    PENDING = "OP"
    PROCESSING = "PR"
    SHIPPED = "SH"
    DELIVERED = "DL"
    CANCELLED = "CN"

    STATUS_CHOICES = (
        (PENDING, _("Заказ ожидает обработки")),
        (PROCESSING, _("Заказ в процессе выполнения")),
        (SHIPPED, _("Заказ отправлен")),
        (DELIVERED, _("Заказ доставлен")),
        (CANCELLED, _("Заказ отменен")),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"),
                             related_name="orders")
    delivery_city = models.CharField(max_length=255, verbose_name=_("Delivery city"))
    delivery_address = models.TextField(max_length=500, verbose_name=_("Delivery address"))
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING)
    archived = models.BooleanField(default=False, verbose_name=_("Archived"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    def __str__(self):
        return f'Order: {self.id}'


class OrderItem(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT, verbose_name=_("Seller"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    quantity = models.IntegerField(verbose_name=_("Quantity"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"), default=0.00)
    delivery = models.ForeignKey(Delivery, on_delete=models.PROTECT, verbose_name=_("Delivery"))
    payment_type = models.ForeignKey(Payment, on_delete=models.PROTECT, verbose_name=_("Payment type"))
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.PROTECT, verbose_name=_("Order"))
    active = models.BooleanField(default=True, verbose_name=_("Active"))

    def __str__(self):
        return f'{self.product}, {self.seller}, {self.quantity}, {self.price}'
