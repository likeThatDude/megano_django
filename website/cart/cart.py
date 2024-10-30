from decimal import Decimal

from django.http import HttpRequest

from catalog.models import Price, Product, Seller
from website import settings


class Cart:
    """
    Модель корзины, которая хранит в себе информацию о товарах в сессии
    """

    def __init__(self, request: HttpRequest):
        """
        Создание корзины
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
        Сохранение корзины
        """
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить, что сессия изменена
        self.session.modified = True

    def add(
        self,
        product: Product,
        price_product: Price,
        quantity: int = 1,
        update_quantity=False,
    ):
        """
        Добавление товара и цены в сессию
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
        Удаление товара из корзины
        """
        product_id = str(product.pk)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных
        """
        for item in self.cart.values():
            info_item = {
                'price': item['price'],
                'product': Product.objects.get(pk=item['product_id']),
                'quantity': item['quantity'],
                'seller': Seller.objects.get(pk=item['seller_id']),
                'total_price': str(Decimal(item["price"]) * item["quantity"]),
            }
            yield info_item

    def __len__(self):
        """
        Подсчет всех товаров в корзине
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине
        """
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )

    def clear(self):
        """
        Удаление корзины из сессии
        """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
