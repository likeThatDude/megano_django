import json
from django.http import HttpRequest
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.generic import View

from .cart import Cart


class DetailCart(TemplateView):
    """
    Этот класс возвращает информацию о корзине.
    Методы:
        get_context_data (**kwargs): собирает информацию из корзины и передает ее в контекст шаблона.
    """

    template_name = "cart/cart_detail.html"

    def get_context_data(self, **kwargs) -> dict:
        """
        Возвращает контекст в шаблон. Добавляет информацию о корзине в контекст.
        При итерации по объекту Cart он возвращает словарь с информацией о товаре
        """
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        context["info_cart"] = cart.get_info_cart()
        return context


class AddProductInCart(View):
    """
    Этот класс позволяет добавлять товары в корзину.
    Методы:
        post: Переопределяет метод POST для добавления товара.
    """

    def post(self, request: HttpRequest, product_id: str, price_id: str, quantity: int = 1) -> JsonResponse:
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
        cart.add(product_id, price_id, quantity)
        return JsonResponse({"status_code": 200})


class UpdateQuantityProductInCart(View):
    """
    Этот класс позволяет обновлять кол-во товара в корзине
    Методы:
        post: Переопределяет метод POST для обновления кол-ва товара в корзине.
    """

    def post(self, request: HttpRequest) -> JsonResponse:
        cart = Cart(request)
        data = json.loads(request.body)
        for info_product in data:
            product_id = info_product['product_id']
            quantity = info_product['quantity']
            cart.update_quantity(product_id, quantity)
        return JsonResponse({"status_code": 200})


class DeleteProductInCart(View):
    """
    Этот класс позволяет добавлять товары в корзину.
    Методы:
        delete (HttpRequest): Переопределяет метод DELETE для удаления товара.
    """

    def delete(self, request: HttpRequest, product_id: str) -> JsonResponse:
        """
        Выполняет DELETE-запрос для удаления товара из корзины.
        Параметры запроса и URL:
            - request (HttpRequest): Текущий запрос пользователя.
            - product_id (int): pk товара который нужно удалить.
        Возвращает:
            JsonResponse: Ответ с кодом 204 при успешном удалении.
        """
        cart = Cart(request)
        cart.remove(product_id)
        request.COOKIES["total_price"] = cart.get_total_cost()
        return JsonResponse({"status_code": 204})


class GetTotalQuantityCart(View):
    """
    GetTotalQuantityCart для получения общего кол-ва товаров в корзине.
    Методы:
        get (HttpRequest): возвращает json {'total_quantity': кол-во (int)}
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
            request.COOKIES["total_quantity"] = cart.get_total_quantity()
        total_quantity = request.COOKIES.get("total_quantity")
        return JsonResponse({"total_quantity": total_quantity})


class GetTotalCostCart(View):
    """
    GetTotalPriceCart для получения общей стоимости товаров в корзине.
    Методы:
        get (HttpRequest): возвращает json {'total_price': стоимость (int)}
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
            request.COOKIES["total_price"] = cart.get_total_cost()
        total_price = request.COOKIES.get("total_price")
        return JsonResponse({"total_price": total_price})


class GetCostProductInCart(View):
    """

    """
    def get(self, request: HttpRequest, product_id: str, quantity: int | None = None) -> JsonResponse:
        """

        """
        if quantity is not None:
            cart = Cart(request)
            cost = cart.get_cost_product(product_id, quantity)
            return JsonResponse({"product_cost": cost})
