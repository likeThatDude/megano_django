from django.urls import path
from . import views
from core.imports.views import import_products_view

app_name = "core"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path('import/', import_products_view, name='import_products'),
]
