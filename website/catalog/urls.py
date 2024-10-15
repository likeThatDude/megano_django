from django.urls import path

from .views import CategoryDetailView, catalog_view

app_name = "catalog"

urlpatterns = [
    path("assortment", catalog_view, name="catalog"),
    path("categories/<int:pk>", CategoryDetailView.as_view(), name="category_detail"),
]
