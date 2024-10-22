from website import settings
from django.http import HttpRequest

from catalog.models import Product, Price

from decimal import Decimal


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

    def add(self, product: Product, price_product: Price, quantity: int = 1, update_quantity=False):
        """
        Добавление товара и цены в сессию
        """
        product_id = str(product.pk)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': price_product.price,
            }
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
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
        product_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчет всех товаров в корзине
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине
        """
        return sum(Decimal(item['price']) * item['quantity']
                   for item in self.cart.values())

    def clear(self):
        """
        Удаление корзины из сессии
        """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True


