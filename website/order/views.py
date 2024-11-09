from django.http import HttpRequest
from django.db.models import F, Sum
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin

from .models import Order


def order_create_view(request: HttpRequest):
    return render(request, "order/order.html")


class OrderDetailView(PermissionRequiredMixin, DetailView):
    """
    Представление для деталей заказа

    Доступно тем пользователям, у которых есть соответствующие разрешения

    Атрибуты:
        permission_required: Необходимые разрешения пользователю
        template_name (str): Путь к шаблону, который будет использоваться для отображения деталей заказа
        queryset (Queryset): Queryset конкретного заказа
        context_object_name (str): Имя объекта контекста для передачи в шаблон.
    """
    permission_required = "order.view_order"
    model = Order
    context_object_name = "order"
    template_name = "order/order_details.html"

    def get_object(self, queryset=None):
        """
        Получаем pk заказа и возвращаем соответствующий заказ
        """
        pk = self.kwargs.get("pk")
        return Order.objects.get(pk=pk)


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
