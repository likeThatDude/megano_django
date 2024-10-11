from django.urls import path

from .views import catalog_view

app_name = "catalog"

urlpatterns = [
    path("assortment", catalog_view, name="catalog")
]
