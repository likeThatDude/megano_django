from django.contrib import admin

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
    )
    ordering = ("pk",)
    inlines = [OrderItemInline]

    def delivery_address_short(self, obj: Order) -> str:
        if len(obj.delivery_address) < 20:
            return obj.delivery_address
        return obj.delivery_address[:20] + "..."

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("order_items").all()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "seller",
        "product",
        "quantity",
        "price",
        "delivery",
        "payment_type",
    )
    list_display_link = (
        "seller",
        "product",
        "quantity",
        "price",
        "delivery",
        "payment_type",
    )
    ordering = ("pk",)

    def get_queryset(self, request):
        return OrderItem.objects.select_related("product", "seller", "delivery", "payment_type", "order").all()
