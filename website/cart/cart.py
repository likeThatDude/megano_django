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

    def save(self):
        """
        Сохраняет корзину и ставит отметку о том, чтобы сессия была изменена
        """
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить, что сессия изменена
        self.session.modified = True

    def add(
        self,
        product: Product,
        price_product: Price,
        quantity: int = 1,
        update_quantity: bool = False,
    ):
        """
        Добавление товара в сессию.

        Атрибуты:
            product (Product) - объект модели товара который нужно добавить в корзину
            price_product (Price) - объект модели цены товара который добавляется
            quantity (int = 1) - кол-во добавляемого товара
            update_quantity (bool = False) - флаг обозначающий принцип добавления товара
                                    False - прибавить значение quantity к текущему кол-ву
                                    True - изменить кол-во товара на значение quantity
        """
        product_id = str(product.pk)
        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": 0,
                "product_id": product.pk,
                "price": str(price_product.price),
                "seller_id": price_product.seller.pk,
            }
        if update_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.save()

    def remove(self, product: Product):
        """
        Удаляет товар из корзины

        Атрибуты:
            product (Product) - удаляет товар в корзине и всю информацию о нем, если он есть в корзине
        """
        product_id = str(product.pk)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Итерация по информации о товарах в корзине.

        Возвращает генератор, где при каждом методе next возвращает словарь
        с информацией о каждом товаре в корзине в удобном формате

        Структура словаря по каждому товару:
            'price': цена товара (str),
            'product': товар (Product),
            'quantity': кол-во товара (int),
            'seller': продавец этого товара (Seller),
            'total_price': общая стоимость этого товара в корзине (str),
        """
        for item in self.cart.values():
            info_item = {
                "price": item["price"],
                "product": Product.objects.get(pk=item["product_id"]),
                "quantity": item["quantity"],
                "seller": Seller.objects.get(pk=item["seller_id"]),
                "total_price": str(Decimal(item["price"]) * item["quantity"]),
            }
            yield info_item

    def __len__(self):
        """
        Возвращает общее кол-во товаров в корзине
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        """
        Возвращает общую стоимость товаров в корзине
        """
        return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())

    def clear(self):
        """
        Полностью очищает корзину
        """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
