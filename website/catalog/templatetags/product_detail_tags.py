from django import template
from django.db.models import QuerySet

register = template.Library()


@register.simple_tag()
def get_lower_price(data: QuerySet) -> str:
    """
    Получает цену самого дешевого товара среди всех продавцов.

    Args:
        data (QuerySet): Кватерсет с объектами продавцов, у которых есть цены.

    Returns:
        str: Цена самого дешевого товара с символом валюты ('$'),
             или строка "Нет цен", если цены отсутствуют.
    """
    for seller in data:
        for price in seller.price.all():
            min_price = float(price.price)
            return f"{min_price} $"


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
