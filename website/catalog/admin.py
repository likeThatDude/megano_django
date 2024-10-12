from django.contrib import admin

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "icon",
        "archived",
        "parent",
    )
    list_display_links = (
        "id",
        "name",
    )
