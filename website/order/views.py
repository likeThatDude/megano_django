from django.http import HttpRequest
from django.db.models import F, Sum
from django.shortcuts import render
from django.views.generic import ListView

from .models import Order


def order_create_view(request: HttpRequest):
    return render(request, "order/order.html")


def order_detail_view(request: HttpRequest):
    return render(request, "order/order-detail.html")


class OrdersHistoryListView(ListView):
    """
    Представление для истории заказов профиля пользователя.

    Атрибуты:
        template_name (str): Путь к шаблону, который будет использоваться для отображения страницы истории заказов
        queryset (Queryset): Queryset всех заказов пользователя
        context_object_name (str): Имя объекта контекста для передачи в шаблон.
    """

    queryset = Order.objects.annotate(
        total_price=Sum(F("products__prices__price") * F("products__prices__quantity"))
    )
    context_object_name = "orders"
    template_name = "order/orders_history.html"
