from django.urls import path
<<<<<<< website/core/urls.py
from core.views import index
from core.imports.views import import_products_view
from .views import index


app_name = "core"

urlpatterns = [
    path("", index, name="index"),
    path('import/', import_products_view, name='import_products'),

]
