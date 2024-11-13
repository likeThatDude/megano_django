from comparison.models import Comparison
from django.contrib import admin


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "product",
    )
    list_display_links = (
        "pk",
        "user",
        "product",
    )
    ordering = (
        "user",
        "pk",
    )
    list_per_page = 20
