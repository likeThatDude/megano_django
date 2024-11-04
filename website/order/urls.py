from django.urls import path

from .views import order_create_view
from .views import order_detail_view

app_name = "order"

urlpatterns = [
    path("create/", order_create_view, name="order_create"),
    path("detail/", order_detail_view, name="order_detail"),
]
