from decimal import Decimal

from catalog.models import Price
from catalog.models import Product
from catalog.models import Seller
from django.http import HttpRequest

from website import settings


class Cart:
    """
    Модель корзины, которая хранит в себе информацию о товарах в сессии.
    Для работы с корзиной необходимо создавать объект корзины для получения информации
    из сессии пользователя.

    Примечание:
    Данный класс работает исключительно с объектами моделей Product и Price при добавлении, удалении и изменении
    """

    def __init__(self, request: HttpRequest):
        """
        Создание корзины. Если корзины не было, то она будет создана в сессиях

        Атрибуты:
            request (HttpRequest): запрос в котором хранится сессия с корзиной.

        """
        # берем текущую сессию пользователя
        self.session = request.session
        # достаем корзину из этой сессии
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # если корзины нет, то создаем пустой список
            cart = self.session[settings.CART_SESSION_ID] = {}
        # сохраняем корзину в атрибуте
        self.cart = cart

    def save(self) -> None:
        """
        Сохраняет корзину и ставит отметку о том, чтобы сессия была изменена
        """
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить, что сессия изменена
        self.session.modified = True

    def add(
        self,
        product_id: int,
        price_product_id: int,
        quantity: int = 1,
    ) -> None:
        """
        Добавление товара в сессию.

        Атрибуты:
            product_id (int) - id модели товара
            price_product_id (id) - id модели цены товара который добавляется
            quantity (int = 1) - кол-во добавляемого товара
        """
        product = Product.objects.get(pk=product_id)
        price_product = Price.objects.get(pk=price_product_id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": 0,
                "product_id": product.pk,
                "price": str(price_product.price),
                "seller_id": price_product.seller.pk,
                "to_order": True,
            }
        self.cart[product_id]["quantity"] += quantity
        self.save()

    def update_quantity(self, product_id: int, new_quantity: int) -> None:
        """
        Обновляет кол-во товара в корзине

        Атрибуты:
            product_ud (int) - id модели товара
            new_quantity (int) - новое кол-во товара в корзине
        """
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = new_quantity
            self.save()

    def remove(self, product_id: int) -> None:
        """
        Удаляет товар из корзины

        Атрибуты:
            product_id (int) - id модели товара, который нужно удалить
        """
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Возвращает генератор, где при каждом методе next возвращает словарь
        с информацией о каждом товаре в корзине в удобном формате


        """
        for item in self.cart.values():
            info_item = {
                "price": item["price"],
                "product": Product.objects.get(pk=item["product_id"]),
                "quantity": item["quantity"],
                "seller": Seller.objects.get(pk=item["seller_id"]),
                "total_cost": str(Decimal(item["price"]) * item["quantity"]),
                "to_order": item["to_order"],
            }
            yield info_item

    def get_total_quantity(self) -> int:
        """
        Возвращает общее кол-во товаров в корзине
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_info_cart(self) -> list[dict]:
        """
        Возвращает информацию о товарах в корзине
        Структура возвращаемых данных:
            [
                {'product_id': {'price': цена товара (str),
                                'product': товар (Product),
                                'quantity': кол-во товара (int),
                                'seller': продавец этого товара (Seller),
                                'total_price': общая стоимость этого товара в корзине (str),}
                }
            ]
        """
        info_cart = list()
        for info_product in self.cart:
            info_cart.append(info_product)
        return info_cart

    def get_total_price(self) -> int:
        """
        Возвращает общую стоимость товаров в корзине
        """
        return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())

    def clear(self) -> None:
        """
        Полностью очищает корзину
        """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
