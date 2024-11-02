from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, View

from catalog.models import Price, Product

from .cart import Cart


class DetailCart(TemplateView):
    """
    DetailCart для отображения информации о корзине.

    Этот класс возвращает информацию о корзине.
    Наследуется от `TemplateView`
    Основная информация о корзине собирается в методе get_context_data.

    Атрибуты:
        template_name (str) - путь к шаблону корзины

    Методы:
        get_context_data (**kwargs): собирает информацию из корзины и передает ее в контекст шаблона.

    Примечания:

    """

    template_name = "cart/cart_detail.html"

    def get_context_data(self, **kwargs):
        """
        Возвращает контекст в шаблон. Добавляет информацию о корзине в контекст.
        При итерации по объекту Cart он возвращает словарь с информацией о товаре

        Структура словаря по каждому товару:
            'price': цена товара (str),
            'product': товар (Product),
            'quantity': кол-во товара (int),
            'seller': продавец этого товара (Seller),
            'total_price': общая стоимость этого товара в корзине (str),
        """
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        info_cart = [info_product for info_product in cart]
        context["info_cart"] = info_cart
        return context


class AddProductInCart(View):
    """
    AddProductInCart для добавления товара в корзину.

    Этот класс позволяет добавлять товары в корзину.
    Наследуется от `View`
    Логика добавления товара в корзину отображена в документации
    к модели Cart

    Атрибуты:
        -

    Методы:
        post (HttpRequest): Переопределяет метод POST для добавления товара.

    Примечания:
        -
    """

    def post(
        self, request: HttpRequest, product_id: int, price_id: int, quantity: int = 1
    ):
        """
        Выполняет POST-запрос для добавления товара в корзину.

        Параметры запроса и URL:
            - request (HttpRequest): Текущий запрос пользователя.
            - product_id (int): pk товара который нужно добавить.
            - price_id (int): pk цены товара которого добавляем.
            - quantity (int): кол-во товара, которое нужно прибавить (по умолчанию 1)

        Возвращает:
            JsonResponse: Ответ с кодом 200 при успешном добавлении.
        """
        cart = Cart(request)
        added_product = Product.objects.get(pk=product_id)
        added_price = Price.objects.get(pk=price_id)
        cart.add(added_product, added_price, quantity)
        return JsonResponse({"status_code": 200})


class UpdateQuantityProductInCart(View):
    """ """

    def post(self, request: HttpRequest, product_id: int, price_id: int, quantity: int):
        cart = Cart(request)
        updated_product = Product.objects.get(pk=product_id)
        price_updated_product = Price.objects.get(pk=price_id)
        cart.add(
            updated_product,
            price_updated_product,
            quantity=quantity,
            update_quantity=True,
        )
        return JsonResponse({"status_code": 200})


class DeleteProductInCart(View):
    """
    DeleteProductInCart для удаления товара в корзину.

    Этот класс позволяет добавлять товары в корзину.
    Наследуется от `View`
    Логика добавления товара в корзину отображена в документации
    к модели Cart

    Атрибуты:
        -

    Методы:
        delete (HttpRequest): Переопределяет метод DELETE для удаления товара.

    Примечания:
        Удаляется вся информация о товаре в корзине
    """

    def delete(self, request: HttpRequest, product_id: int):
        """
        Выполняет DELETE-запрос для удаления товара из корзины.

        Параметры запроса и URL:
            - request (HttpRequest): Текущий запрос пользователя.
            - product_id (int): pk товара который нужно удалить.

        Возвращает:
            JsonResponse: Ответ с кодом 204 при успешном удалении.
        """
        cart = Cart(request)
        deleted_product = Product.objects.get(pk=product_id)
        cart.remove(deleted_product)
        request.COOKIES["total_price"] = cart.get_total_price()
        return JsonResponse({"status_code": 204})


class GetTotalQuantityCart(View):
    """
    GetTotalQuantityCart для получения общего кол-ва товаров в корзине.

    Этот класс возвращает общее кол-во товаров в корзине и сохраняет его
    в куках для оптимизации запросов

    Атрибуты:
        -

    Методы:
        get (HttpRequest): возвращает json {'total_quantity': кол-во (int)}

    Примечания:
        общее кол-во товаров сохраняется в куках если там не было
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        """
        Выполняет GET-запрос для получения информации об общем кол-ве товаров.

        Параметры запроса и URL:
            - request (HttpRequest): Текущий запрос пользователя.

        Возвращает:
            JsonResponse: Ответ в ключе 'total_quantity'.
        """
        cart = Cart(request)
        if "total_quantity" not in request.COOKIES:
            request.COOKIES["total_quantity"] = len(cart)
        total_quantity = request.COOKIES.get("total_quantity")
        return JsonResponse({"total_quantity": total_quantity})


class GetTotalPriceCart(View):
    """
    GetTotalPriceCart для получения общей стоимости товаров в корзине.

    Этот класс возвращает общую стоимость товаров в корзине и сохраняет его
    в куках для оптимизации запросов

    Атрибуты:
        -

    Методы:
        get (HttpRequest): возвращает json {'total_price': стоимость (int)}

    Примечания:
        общая стоимость товаров сохраняется в куках если там не было
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        """
        Выполняет GET-запрос для получения информации об общей стоимости товаров.

        Параметры запроса и URL:
            - request (HttpRequest): Текущий запрос пользователя.

        Возвращает:
            JsonResponse: Ответ в ключе 'total_price'.
        """
        cart = Cart(request)
        if "total_price" not in request.COOKIES:
            request.COOKIES["total_price"] = cart.get_total_price()
        total_price = request.COOKIES.get("total_price")
        return JsonResponse({"total_price": total_price})
