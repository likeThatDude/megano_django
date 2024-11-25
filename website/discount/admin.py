from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Discount
from .models import ProductGroup


@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "short_description",
        "archived",
    )
    list_display_links = ("pk", "name")
    list_filter = ("archived",)
    search_fields = (
        "name",
        "description",
    )
    ordering = (
        "name",
        "pk",
    )

    @staticmethod
    def short_description(obj: ProductGroup) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "slug",
        "kind",
        "short_description",
        "start_date",
        "end_date",
        "is_active",
        "archived",
    )
    list_display_links = "pk", "name"
    list_filter = (
        "kind",
        "method",
        "is_active",
        "archived",
    )
    search_fields = (
        "name",
        "description",
    )
    ordering = (
        "name",
        "pk",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "kind",
                    "method",
                    "description",
                )
            },
        ),
        (
            _("Conditions and/or applicable deduction"),
            {
                "fields": (
                    "value",
                    "quantity_gt",
                    "quantity_lt",
                    "start_date",
                    "end_date",
                    "is_active",
                )
            },
        ),
        (
            _("Items subject to discount"),
            {
                "fields": (
                    "products",
                    "categories",
                    "product_groups",
                )
            },
        ),
        (
            _("Remove discount"),
            {"fields": ("archived",)},
        ),
    )

    @staticmethod
    def short_description(obj: Discount) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."
