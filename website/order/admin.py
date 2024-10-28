from django.contrib import admin


from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "profile",
        "delivery_city",
        "delivery_address",
        "status",
        "payment_method",
        "delivery_method",
        "archived",
        "created_at",
    )
    ordering = ("pk",)
    list_editable = [
        "delivery_city",
        "delivery_address",
        "status",
        "payment_method",
        "delivery_method",
        "archived",
    ]
