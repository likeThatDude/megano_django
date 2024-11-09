from django.urls import path

from .views import order_create_view
from .views import OrderDetailView
from .views import OrdersHistoryListView

app_name = "order"

urlpatterns = [
    path("create/", order_create_view, name="order_create"),
    path("order_detail/<int:pk>", OrderDetailView.as_view(), name="order_detail"),
    path("orders_history/", OrdersHistoryListView.as_view(), name="orders-history"),
]
