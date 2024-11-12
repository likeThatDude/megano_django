from collections import defaultdict
from itertools import product

from catalog.models import Product
from catalog.models import Seller
from django import template
from django.db.models import QuerySet

register = template.Library()


@register.filter
def get_delivery_data(data: QuerySet) -> dict[Seller, list[Product]]:
    seller_filter_data = defaultdict(list)
    for i in data:
        seller_filter_data[i.seller].append(i.product)
    return dict(seller_filter_data)


@register.filter
def get_payments_data(data: QuerySet) -> dict[Seller, list[Product]]:
    seller_filter_data = defaultdict(list)
    for i in data:
        seller_filter_data[i.seller].append(i.product)
    return dict(seller_filter_data)


@register.simple_tag
def get_product_data(product_id: int, products_dict: dict[int, dict[str, int]], target: str) -> int:
    return products_dict[product_id][target]
