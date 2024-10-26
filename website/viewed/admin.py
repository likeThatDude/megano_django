from django.contrib import admin

from .models import Viewed


@admin.register(Viewed)
class ViewedAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "product",
        "created_at",
    )
    list_display_links = (
        "pk",
        "user",
        "product",
    )
    list_filter = (
        "user",
        "product",
    )
    search_fields = (
        "user__login",
        "product__name",
    )
