from django.db.models import F
from django.db.models import Sum
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from order import utils
from order.forms import OrderForm

from website import settings

from cart.cart import Cart
from .models import Order
from .utils import create_errors_list
from .utils import get_order_products

# products_list = {
#     "product1": {"quantity": 2, "product_id": 1, "price": 1200.25, "seller_id": 2, "to_order": True},
#     "product2": {"quantity": 1, "product_id": 2, "price": 1300.75, "seller_id": 1, "to_order": True},
#     "product3": {"quantity": 1, "product_id": 3, "price": 1500.10, "seller_id": 1, "to_order": False},
# }


class OrderCreateView(View):
    """
    Представление для создания заказа.

    Этот класс обрабатывает как GET, так и POST запросы для создания нового заказа.
    В случае GET запроса отображается страница с данными для оформления заказа, включая товары в корзине,
    а также их цену и дополнительные данные.
    В случае POST запроса происходит обработка формы для создания заказа, включая проверку данных.
    Если данные формы валидны, заказ сохраняется, иначе возвращаются ошибки формы.

    Атрибуты:
        None.

    Методы:
        get(request: HttpRequest) -> HttpResponse:
            Обрабатывает GET запрос и отображает страницу с данными для оформления заказа.
            Данные берутся из сессии, которые добавляются туда в корзине.

        post(request: HttpRequest) -> HttpResponse:
            Обрабатывает POST запрос, проверяет валидность данных формы и сохраняет заказ,
            если данные корректны, или возвращает страницу с ошибками, если данные некорректны.

    Параметры:
        request (HttpRequest): Объект HTTP запроса, содержащий информацию о запросе.

    Возвращает:
        HttpResponse: Страница с данными для оформления заказа или страница с ошибками,
        или перенаправление на страницу подтверждения создания заказа.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {}
        user = utils.get_user_data(request)
        context.update(user)
        cart = Cart(request)
        products_list = cart.products
        products_correct_list = get_order_products(products_list)
        product_data = utils.create_product_context_data(products_correct_list)
        prices = utils.get_correct_queryset(products_correct_list)
        context["order_data"] = prices
        context["product_data"] = product_data
        return render(request, "order/order.html", context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            cart = Cart(request)
            products_list = cart.products
            data = request.POST
            validate_data = OrderForm(data)
            if validate_data.is_valid():
                correct_data = validate_data.cleaned_data
                products_correct_list = get_order_products(products_list)
                utils.data_preparation_and_recording(correct_data, products_correct_list, request.user.pk)
            else:
                context = {}
                data_errors = validate_data.errors.items()
                errors_list = create_errors_list(data_errors)
                context["errors"] = errors_list
                return render(request, "order/order_error_list.html", context=context)
            return redirect(reverse("order:order_create"))
        else:
            return redirect(reverse("account:login"))


def order_detail_view(request: HttpRequest):
    return render(request, "order/order-detail.html")


def pay_view(request: HttpRequest):
    return render(request, "order/payment.html")


def pay_view2(request: HttpRequest):
    return render(request, "order/paymentsomeone.html")


# class OrdersHistoryListView(ListView):
#     """
#     Представление для истории заказов профиля пользователя.
#
#     Атрибуты:
#         template_name (str): Путь к шаблону, который будет использоваться для отображения страницы истории заказов
#         queryset (Queryset): Queryset всех заказов пользователя
#         context_object_name (str): Имя объекта контекста для передачи в шаблон.
#     """
#
#     queryset = Order.objects.annotate(
#         total_price=Sum(F("products__prices__price") * F("products__prices__quantity"))
#     )
#     context_object_name = "orders"
#     template_name = "order/orders_history.html"
