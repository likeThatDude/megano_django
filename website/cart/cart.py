from decimal import Decimal

from catalog.models import Price
from catalog.models import Product
from catalog.models import Seller
from rest_framework.request import Request

from website import settings


class Cart:
    """
    Модель корзины, которая хранит в себе информацию о товарах в сессии.
    Для работы с корзиной необходимо создавать объект корзины для получения информации
    из сессии пользователя.
    """

    def __init__(self, request: Request):
        """
        Создание корзины

        Атрибуты:
            request (Request): запрос в котором хранится сессия с корзиной.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {
                "total_quantity": 0,
                "total_cost": "0",
            }
        self.cart: dict = cart

    def save(self) -> None:
        """
        Обновляет кол-во, стоимость товаров в корзине и сохраняет корзину в сессии
        """
        self.__update_total_values_cart()
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить, что сессия изменена
        self.session.modified = True

    def add(
        self,
        product_id: str,
        price_product_id: str,
        quantity: int = 1,
    ) -> None:
        """
        Добавление товара в сессию.

        Атрибуты:
            product_id (str) - id модели товара
            price_product_id (str) - id модели цены товара который добавляется
            quantity (int = 1) - кол-во добавляемого товара
        """
        price_product = Price.objects.get(pk=int(price_product_id))
        product_key = f"product{product_id}"
        if product_key not in self.cart:
            self.cart[product_key] = {
                "quantity": 0,
                "product_id": int(product_id),
                "price": float(price_product.price),
                "seller_id": price_product.seller.pk,
                "seller_name": str(price_product.seller),
                "to_order": True,
                "cost_product": "0.00",
            }
        self.cart[product_key]["quantity"] += quantity
        self.cart[product_key]["cost_product"] = self.__get_cost_product(product_id, self.cart[product_key]["quantity"])
        self.save()

    def __get_cost_product(self, product_id: str, quantity: int) -> float:
        """
        Возвращает общую стоимость товара
        """
        if quantity != 0:
            cost = float(round(Decimal(self.cart[f"product{product_id}"]["price"]) * quantity, 2))
            return cost
        return 0.00

    def update_product(self, product_id: str, new_seller_id: int, new_quantity: int) -> None:
        """
        Обновляет информацию о товаре в корзине

        Атрибуты:
            product_ud (str) - id модели товара
            new_seller_id (int) - id продавца товара
            new_quantity (int) - новое кол-во товара в корзине
        """
        if f"product{product_id}" in self.cart:
            self.cart[f"product{product_id}"]["quantity"] = new_quantity
            self.cart[f"product{product_id}"]["seller_id"] = new_seller_id
            self.cart[f"product{product_id}"]["seller_name"] = str(Seller.objects.get(pk=new_seller_id))
            new_price_product = float(Price.objects.get(seller=new_seller_id, product=product_id).price)
            self.cart[f"product{product_id}"]["price"] = new_price_product
            self.cart[f"product{product_id}"]["cost_product"] = self.__get_cost_product(product_id, new_quantity)
            self.save()

    def remove(self, product_id: str) -> None:
        """
        Удаляет товар из корзины

        Атрибуты:
            product_id (str) - id модели товара, который нужно удалить
        """
        if f"product{product_id}" in self.cart:
            del self.cart[f"product{product_id}"]
            self.save()

    @property
    def total_quantity(self) -> int:
        """
        Возвращает общее кол-во товаров в корзине
        """
        return self.cart["total_quantity"]

    @property
    def total_cost(self) -> str:
        """
        Возвращает общую стоимость товаров в корзине
        """
        return self.cart["total_cost"]

    def __update_total_values_cart(self):
        """
        Обновляет общую информацию о корзине (кол-во и стоимость товаров)
        """
        self.cart["total_quantity"] = self.__get_total_quantity()
        self.cart["total_cost"] = self.__get_total_cost()

    def __get_total_quantity(self) -> int:
        """
        Возвращает общее кол-во товаров в корзине
        """
        return sum(item["quantity"] for item in self.cart.values() if isinstance(item, dict))

    def __get_total_cost(self) -> str:
        """
        Возвращает общую стоимость товаров в корзине
        """
        total_cost = round(
            sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values() if isinstance(item, dict)), 2
        )
        return str(total_cost)

    def get_context_info(self) -> list[dict]:
        """
        Возвращает информацию для отображения страницы корзины
        Структура возвращаемых данных:
            [
                {'product_id': {'price': цена товара (str),
                                'product': товар (Product),
                                'quantity': кол-во товара (int),
                                'seller': продавец этого товара (Seller),
                                'total_price': общая стоимость этого товара в корзине (str),
                                'to_order': отметка о том, что товар будет добавлен в заказ (bool),}
                }
            ]
        """
        info_cart = list()
        for product in self.cart.values():
            if isinstance(product, dict):
                info_product = {
                    "price": product["price"],
                    "product": Product.objects.get(pk=product["product_id"]),
                    "quantity": product["quantity"],
                    "seller": Seller.objects.get(pk=product["seller_id"]),
                    "sellers_product": Seller.objects.prefetch_related("products").filter(
                        products=product["product_id"]
                    ),
                    "total_cost": product["cost_product"],
                    "to_order": product["to_order"],
                }
                info_cart.append(info_product)
        return info_cart

    def clear(self) -> None:
        """
        Полностью очищает корзину
        """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
