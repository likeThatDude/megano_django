from decimal import Decimal
from itertools import product

from django import template
from django.db.models import QuerySet

from catalog.models import Seller

register = template.Library()


@register.simple_tag()
def get_lower_price(sellers_list: QuerySet) -> str:
    """
    Получает цену самого дешевого товара среди всех продавцов.

    Args:
        sellers_list (QuerySet): Кватерсет с объектами продавцов, у которых есть цены.

    Returns:
        str: Цена самого дешевого товара с символом валюты ('$'),
             или строка "Нет цен", если цены отсутствуют.
    """
    min_price = None
    for seller in sellers_list:
        for price in seller.price.all():
            if min_price is None:
                min_price = price.price
            min_price = price.price if min_price > price.price else min_price
    return f'{min_price}$'


@register.simple_tag()
def get_seller_data_list(data: QuerySet) -> str:
    """
    Формирует строку с названиями методов доставки,
    где первое название с заглавной буквы, а остальные — с маленькой.

    Args:
        data (QuerySet): Кватерсет с объектами методов доставки.

    Returns:
        str: Строка с названиями методов доставки, разделенными запятыми.
    """
    data_generator = (str(method).lower() if index > 1 else str(method) for index, method in enumerate(data, start=1))
    return ", ".join(data_generator)


@register.simple_tag()
def get_seller_price(data: Seller, product_id: int) -> Decimal:
    """
    Получает цену товара для указанного продавца.

    Args:
        data (Seller): Объект продавца, для которого необходимо получить цену.
        product_id (int): Идентификатор товара, для которого нужно узнать цену.

    Returns:
        Decimal: Цена товара, если она найдена; иначе None.
    """
    for price in data.price.all():
        if price.product_id == product_id:
            return price.price