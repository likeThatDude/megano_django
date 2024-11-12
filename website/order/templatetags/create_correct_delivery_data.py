from collections import defaultdict
from itertools import product

from catalog.models import Product
from catalog.models import Seller
from django import template
from django.db.models import QuerySet

from order.models import Order

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


@register.simple_tag
def get_short_delivery_payment_type(data: Order, payment=False) -> str:
    if not payment:
        delivery_type_data = {delivery.delivery.__str__() for delivery in data.order_items.all()}
    else:
        delivery_type_data = {delivery.payment_type.__str__() for delivery in data.order_items.all()}
    correct_data = ", ".join(delivery_type_data)
    return correct_data.capitalize()

@register.simple_tag
def get_full_delivery_payment_type(data: Order, payment=False) -> dict[str, list[str]]:
    seller_product_dict = defaultdict(list)
    for i in data.order_items.all():
        if not payment:
            seller_product_dict[i.seller.name].append(i.delivery.__str__())
        else:
            seller_product_dict[i.seller.name].append(i.payment_type.__str__())
    return dict(seller_product_dict)
