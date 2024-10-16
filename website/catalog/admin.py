from django.contrib import admin
from django.core.cache import cache
from django.db.models import QuerySet
from django.http import HttpRequest

from website.settings import CATEGORY_KEY

from .models import Category, Product, Review


@admin.action(description="Delete cache")
def delete_cache(
    model_admin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
):
    cache.delete(CATEGORY_KEY)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = [
        delete_cache,
    ]
    list_display = (
        "id",
        "name",
        "icon",
        "archived",
        "parent_category",
    )
    list_display_links = (
        "id",
        "name",
    )
    ordering = ("id",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "archived",
        "price",
    )
    list_display_links = (
        "id",
        "name",
    )
    ordering = ("id",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'user',
        'text',
        'created_at',
    )
    list_display_links = (
        'id',
        'text',
    )
    ordering = ('id',)
