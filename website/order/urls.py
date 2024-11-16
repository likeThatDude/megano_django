from django.urls import path

from . import views

app_name = "order"

urlpatterns = [
    path("create/", views.OrderCreateView.as_view(), name="order_create"),
    path("detail/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("payment/", views.pay_view, name="payment_view"),
    path("payment1/", views.pay_view2, name="payment_view"),
    # path("orders_history/", views.OrdersHistoryListView.as_view(), name="orders-history"),
]
