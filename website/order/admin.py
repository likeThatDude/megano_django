from django.contrib import admin

from .models import DeliveryPrice
from .models import Order
from .models import OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "delivery_city",
        "delivery_address_short",
        "status",
        "archived",
        "created_at",
        "updated_at",
        "total_price",
        "delivery_price",
    )
    list_display_links = (
        "pk",
        "user",
        "delivery_city",
        "delivery_address_short",
        "status",
        "archived",
        "created_at",
        "updated_at",
        "total_price",
        "delivery_price",
    )
    ordering = ("pk",)
    inlines = [OrderItemInline]
    list_per_page = 20

    def delivery_address_short(self, obj: Order) -> str:
        if len(obj.delivery_address) < 20:
            return obj.delivery_address
        return obj.delivery_address[:20] + "..."

    def get_queryset(self, request):
        return Order.objects.select_related("user", "delivery_price").prefetch_related("order_items").all()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "seller",
        "product",
        "quantity",
        "price",
        "delivery",
        "payment_type",
        "payment_status",
    )
    list_display_links = (
        "seller",
        "product",
        "quantity",
        "price",
        "delivery",
        "payment_type",
        "payment_status",
    )
    ordering = ("pk",)

    def get_queryset(self, request):
        return OrderItem.objects.select_related("product", "seller", "delivery", "payment_type", "order").all()


@admin.register(DeliveryPrice)
class DeliveryPriceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
    )
    list_display_links = (
        "name",
        "price",
    )
