from itertools import product

from django import template
from django.db.models import QuerySet
from collections import defaultdict

from catalog.models import Seller, Product

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