import json
from django.views.generic import TemplateView

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT

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


class APICart(APIView):
    """
    API для взаимодействия с корзиной
    """
    def get(self, request: Request) -> Response:
        """
        Возвращает ВСЮ информацию о товарах в корзине
        """
        cart = Cart(request)
        return Response({'cart': cart.cart})

    def post(self, request: Request) -> Response:
        """
        Добавляет товар в корзину если в теле запроса
        """
        cart = Cart(request)
        data = request.data
        if data["update_products"]:
            for product_id, quantity in data["products"].items():
                cart.update_quantity(product_id, quantity)
            return Response(status=HTTP_200_OK)
        else:
            product_id = data["product_id"]
            price_id = data["price_id"]
            quantity = 1
            if "quantity" in data:
                quantity = data["quantity"]
            cart.add(product_id, price_id, quantity)
            return Response(status=HTTP_201_CREATED)

    def patch(self, request: Request) -> Response:
        """
        Обновляет кол-во товаров в корзине
        """
        cart = Cart(request)
        data = json.loads(request.body)
        for info_product in data:
            product_id = info_product['product_id']
            quantity = info_product['quantity']
            cart.update_quantity(product_id, quantity)
        return Response(status=HTTP_200_OK)

    def delete(self, request: Request) -> Response:
        """
        Удаляет товар из корзины
        """
        cart = Cart(request)
        product_id = request.data["product_id"]
        cart.remove(product_id)
        return Response(status=HTTP_204_NO_CONTENT)
