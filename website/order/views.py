from cart.cart import Cart
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.db.models import F
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import Sum
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView
from django.views.generic import ListView
from kombu.exceptions import HttpError
from order import utils
from order.forms import OrderForm

from .models import Order
from .models import OrderItem
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
        if products_list:
            products_correct_list = get_order_products(products_list)
            product_data = utils.create_product_context_data(products_correct_list)
            prices = utils.get_correct_queryset(products_correct_list)
            context["order_data"] = prices
            context["product_data"] = product_data
            return render(request, "order/order.html", context=context)
        else:
            return redirect(reverse("core:index"))

    def post(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            cart = Cart(request)
            products_list = cart.products
            data = request.POST
            validate_data = OrderForm(data)
            if validate_data.is_valid():
                correct_data = validate_data.cleaned_data
                products_correct_list = get_order_products(products_list)
                order_data = utils.data_preparation_and_recording(correct_data, products_correct_list, request.user.pk)
            else:
                context = {}
                data_errors = validate_data.errors.items()
                errors_list = create_errors_list(data_errors)
                context["errors"] = errors_list
                return render(request, "order/order_error_list.html", context=context)
            return redirect(reverse("order:order_detail", kwargs={"pk": order_data}))
        else:
            return redirect(reverse("account:login"))


class OrderDetailView(DetailView):
    """
    Представление для отображения подробной информации о заказе.

    Извлекает заказ по первичному ключу (pk) и связанные данные, такие как пользователь, товары в заказе,
    информация о доставке и оплате. Только пользователь, создавший заказ, или администратор могут получить
    доступ к данным заказа. В случае отказа в доступе выбрасывается PermissionDenied.

    Атрибуты:
        template_name (str): Шаблон для рендеринга страницы с деталями заказа.
        context_object_name (str): Имя объекта, доступного в контексте шаблона.
    """

    template_name = "order/order-detail.html"
    context_object_name = "order"

    def get_object(self):
        """
        Получает объект заказа по его первичному ключу (pk), включая связанные объекты, такие как пользователь,
        товары в заказе, доставка и оплата.

        Этот метод используется в представлении для загрузки подробностей заказа. Он извлекает заказ по его первичному
        ключу и подготавливает связанные объекты для отображения в шаблоне. Для каждого товара в заказе извлекаются
        данные о продавце, продукте, типе доставки и типе оплаты.
        Также учитываются только активные товары, и фильтрация по полям из связанных моделей оптимизирована для более
        эффективного извлечения данных.

        В случае, если текущий пользователь не является владельцем заказа или не является администратором, будет
        поднята ошибка PermissionDenied.

        Возвращает:
            Order: Объект заказа с полной информацией о заказе, товарах, пользователе и других связанных данных.

        Исключения:
            PermissionDenied: Поднимется, если текущий пользователь не имеет доступа к данному заказу.

        Примечание:
            Этот метод использует `select_related` и `prefetch_related` для оптимизации запросов, загружая только
            нужные поля и избегая ненужных запросов к базе данных.
        """
        order = get_object_or_404(
            Order.objects.select_related(
                "user",
                "delivery_price",
            )
            .prefetch_related(
                Prefetch(
                    "order_items",
                    queryset=OrderItem.objects.select_related(
                        "seller",
                        "product",
                        "delivery",
                        "payment_type",
                    )
                    .filter(active=True)
                    .only(
                        "seller__name",
                        "product__preview",
                        "product__name",
                        "product__short_description",
                        "delivery__name",
                        "payment_type__name",
                        "order__id",
                        "quantity",
                        "price",
                        "payment_status",
                    ),
                )
            )
            .annotate(unique_payment_types=Count("order_items__payment_type", distinct=True))
            .only(
                "user__id",
                "order_items",
                "name",
                "delivery_city",
                "delivery_address",
                "recipient_phone",
                "recipient_email",
                "status",
                "archived",
                "created_at",
                "total_price",
                "delivery_price",
                "paid_status",
            ),
            pk=self.kwargs["pk"],
        )
        if order.user.pk == self.request.user.pk or self.request.user.is_staff:
            return order
        else:
            raise PermissionDenied(_("У вас нет доступа к этому заказу."))

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        scheme = self.request.scheme
        host = self.request.get_host()
        current_receipt_url = f"{scheme}://{host}"
        context["current_receipt_url"] = current_receipt_url

        return context
