from django.contrib import admin
from django.core.cache import cache
from django.db.models import QuerySet
from django.http import HttpRequest

from website.settings import CATEGORY_KEY

from .models import Category
from .models import Delivery
from .models import NameSpecification
from .models import Payment
from .models import Price
from .models import Product
from .models import ProductImage
from .models import Review
from .models import Seller
from .models import Specification
from .models import Tag
from .models import Viewed


@admin.action(description="Delete cache")
def delete_cache(model_admin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
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


class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_name_short",
        "archived",
        "product_type",
    )
    list_display_links = (
        "id",
        "product_name_short",
    )
    ordering = ("id",)
    inlines = [
        ProductInline,
    ]

    def product_name_short(self, obj: Product) -> str:
        if len(obj.name) < 20:
            return obj.name
        return obj.name[:20] + "..."


class SellerProductsInline(admin.TabularInline):
    model = Seller.products.through


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    inlines = [
        SellerProductsInline,
    ]
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
    ordering = (
        "name",
        "id",
    )
    search_fields = ("name",)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "payment_methods":
            kwargs["queryset"] = Payment.objects.exclude(name__in=[Payment.STORE_ONLINE, Payment.STORE_RANDOM])
        elif db_field.name == "delivery_methods":
            kwargs["queryset"] = Delivery.objects.exclude(name__in=[Delivery.SHOP_STANDARD, Delivery.SHOP_EXPRESS])

        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
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
    search_fields = (
        "id",
        "seller",
        "product",
    )


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
    list_per_page = 20


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
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
    list_display = (
        "pk",
        "name",
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_display_links = ("name",)
    ordering = ("name",)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_display_links = ("name",)
    ordering = ("name",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_display_links = ("name",)
    ordering = ("name",)


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
