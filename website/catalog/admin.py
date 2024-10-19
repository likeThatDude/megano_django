from django.contrib import admin
from django.core.cache import cache
from django.db.models import QuerySet
from django.http import HttpRequest

from website.settings import CATEGORY_KEY


from .models import Category, NameSpecification, Product, Review, Specification, Seller, Storage


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
    )
    list_display_links = (
        "id",
        "name",
    )
    ordering = ("id",)


class SellerProductsInline(admin.TabularInline):
    model = Seller.products.through


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    inlines = [SellerProductsInline,]
    list_display = (
        "id",
        "name",
        "description",
        "image",
        "phone",
        "address",
        "email",
        "archived",
    )
    list_display_links = (
        "id",
        "name",
    )
    ordering = ("name", "id", )
    search_fields = ("name", )


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "seller",
        "product",
        "quantity",
        "price",
        "created_at",
    )
    list_display_links = (
        "id",
        "seller",
        "product",
    )
    search_fields = ("id", "seller", "product", )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "user",
        "text",
        "created_at",
    )
    list_display_links = (
        "id",
        "text",
    )
    ordering = ("id",)


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = (
        "value",
        "name",
        "product",
    )
    list_display_links = (
        # "specification",
        "name",
    )
    ordering = ("id",)


@admin.register(NameSpecification)
class NameSpecificationAdmin(admin.ModelAdmin):
    list_display = ("name",)

