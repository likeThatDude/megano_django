from django.urls import path

from .views import order_create_view, order_detail_view

app_name = "order"

urlpatterns = [
    path("order-create/", order_create_view, name="order-create"),
    path("order-detail/", order_detail_view, name="order-detail"),
]
