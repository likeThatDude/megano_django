from django.urls import path
from core.views import IndexView
from core.imports.views import import_products_view

app_name = "core"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path('import/', import_products_view, name='import_view'),
]
