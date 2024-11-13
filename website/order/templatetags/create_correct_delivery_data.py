from collections import defaultdict
from decimal import Decimal
from catalog.models import Product
from catalog.models import Seller
from django import template
from django.db.models import QuerySet

from order.models import Order

register = template.Library()


@register.filter
def get_delivery_data(data: QuerySet) -> dict[Seller, list[Product]]:
    """
    Группирует продукты по продавцам, возвращая их в виде словаря.

    Параметры:
        data (QuerySet): Коллекция продуктов с информацией о продавцах.

    Возвращает:
        dict: Словарь, где ключи - продавцы (Seller), а значения - список продуктов (Product),
              связанных с каждым продавцом.
    """
    seller_filter_data = defaultdict(list)
    for i in data:
        seller_filter_data[i.seller].append(i.product)
    return dict(seller_filter_data)


@register.filter
def get_payments_data(data: QuerySet) -> dict[Seller, list[Product]]:
    """
    Группирует продукты по продавцам, возвращая их в виде словаря с учётом платежных типов.

    Параметры:
        data (QuerySet): Коллекция продуктов с информацией о продавцах.

    Возвращает:
        dict: Словарь, где ключи - продавцы (Seller), а значения - список продуктов (Product),
              связанных с каждым продавцом.
    """
    seller_filter_data = defaultdict(list)
    for i in data:
        seller_filter_data[i.seller].append(i.product)
    return dict(seller_filter_data)


@register.simple_tag
def get_product_data(product_id: int, products_dict: dict[int, dict[str, int]], target: str) -> int:
    """
    Извлекает данные о продукте из словаря на основе его ID и целевого поля.

    Параметры:
        product_id (int): Идентификатор продукта.
        products_dict (dict): Словарь, где ключами являются ID продуктов, а значениями - другие данные.
        target (str): Целевое поле (например, "quantity" или "price"), для которого нужно вернуть значение.

    Возвращает:
        int: Значение для целевого поля продукта.
    """
    return products_dict[product_id][target]


@register.simple_tag
def get_short_delivery_payment_type(data: Order, payment=False) -> str:
    """
    Получает краткое описание типов доставки или оплаты для заказа.

    Параметры:
        data (Order): Объект заказа.
        payment (bool): Флаг, указывающий, нужно ли учитывать тип оплаты (по умолчанию - False для доставки).

    Возвращает:
        str: Скомбинированная строка с типами доставки или оплаты.
    """
    if not payment:
        delivery_type_data = {delivery.delivery.__str__() for delivery in data.order_items.all()}
    else:
        delivery_type_data = {delivery.payment_type.__str__() for delivery in data.order_items.all()}
    correct_data = ", ".join(delivery_type_data)
    return correct_data.capitalize()


@register.simple_tag
def get_full_delivery_payment_type(data: Order, payment=False) -> dict[str, list[str] | set[str]]:
    """
    Получает полные данные о типах доставки или оплаты для каждого продавца в заказе.

    Параметры:
        data (Order): Объект заказа.
        payment (bool): Флаг, указывающий, для чего создаётся словарь. (по умолчанию - False для доставки).

    Возвращает:
        dict: Словарь, где ключи - имена продавцов, а значения - множества или список типов доставки или
        оплаты для каждого продавца.
    """
    seller_product_dict = defaultdict(list)
    for i in data.order_items.all():
        if not payment:
            seller_product_dict[i.seller.name].append(i.delivery.__str__())
        else:
            seller_product_dict[i.seller.name].append(i.payment_type.__str__())
    seller_product_dict = {key: set(value) for key, value in seller_product_dict.items()}
    return dict(seller_product_dict)


@register.simple_tag
def check_delivery_payment_type(price: Decimal, order_price: Decimal) -> bool | Decimal:
    """
    Проверяет, нужно ли учитывать цену доставки и добавлять её к общей стоимости заказа.

    Параметры:
        price (Decimal): Стоимость доставки.
        order_price (Decimal): Стоимость заказа.

    Возвращает:
        bool | Decimal: Если стоимость доставки равна нулю, возвращает False; иначе возвращает общую стоимость.
    """
    if price == 0:
        return False
    else:
        total_price = price + order_price
        return total_price
