from django.views.generic import TemplateView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from .cart import Cart


class DetailCart(TemplateView):
    """
    Представление для отображения страницы корзины
    """

    template_name = "cart/cart_detail.html"

    def get_context_data(self, **kwargs) -> dict:
        """
        Возвращает контекст в шаблон
        """
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        context["info_cart"] = cart.get_context_info()
        context["total_quantity_products"] = cart.total_quantity
        return context


class APICart(APIView):
    """
    API для взаимодействия с корзиной
    """

    def get(self, request: Request) -> Response:
        """
        Возвращает информацию о товарах в корзине
        Формат корзины:
        {
            "product1": {
                    "quantity": "кол-во товара (int)",
                    "product_id": "id товара (int)",
                    "price": "цена товара (float)",
                    "seller_id": "id продавца (int)",
                    "seller_name": "имя продавца (str)",
                    "to_order": "в заказе товара или нет (bool)",
                    "cost_product": "стоимость товара (str),"
            },
            "total_quantity": "общее кол-во товара в корзине (int)",
            "total_cost": "общая стоимость товаров в корзине (str)",
        }
        """
        cart = Cart(request)
        return Response(cart.cart)

    def post(self, request: Request) -> Response:
        """
        Добавляет товар в корзину
        """
        cart = Cart(request)
        data = request.data
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
        data = request.data
        product_id = data["product_id"]
        quantity = data["quantity"]
        seller_id = data["seller_id"]
        cart.update_product(product_id, seller_id, quantity)
        return Response(status=HTTP_200_OK)

    def delete(self, request: Request) -> Response:
        """
        Удаляет товар из корзины
        """
        cart = Cart(request)
        product_id = request.data["product_id"]
        cart.remove(product_id)
        return Response(status=HTTP_204_NO_CONTENT)
