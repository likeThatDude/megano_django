from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("assortment", views.catalog_view, name="catalog"),
    path("categories/<int:pk>", views.CategoryDetailView.as_view(), name="category_detail"),
    path('products/<int:pk>', views.ProductDetailView.as_view(), name="product_detail"),
]
