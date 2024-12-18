from django.urls import path

from . import views
from .views import CatalogListView, catalog_view

app_name = "catalog"

urlpatterns = [
    path("assortment", catalog_view, name="catalog"),
    path("<int:pk>", CatalogListView.as_view(), name="catalog"),
    # products
    path("products/<int:pk>", views.ProductDetailView.as_view(), name="product_detail"),
]
