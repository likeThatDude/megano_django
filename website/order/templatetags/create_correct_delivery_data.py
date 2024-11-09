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
