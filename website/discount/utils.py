from random import choices
from typing import List

from catalog.models import Product
from django.db.models import Min
from django.db.models import Q
from django.utils import timezone


def get_discounted_products(amount: int) -> List[Product]:
    """
    Возвращает список случайных товаров,
    на которые действует какая-нибудь скидка
    :param amount: количество случайных товаров в списке
    """

    today = timezone.now().date()
    discounted_products = (
        Product.objects.filter(
            Q(
                discounts__is_active=True,
                discounts__archived=False,
                discounts__isnull=False,
                discounts__start_date__lte=today,
                discounts__end_date__gte=today,
            )
            | Q(
                category__discounts__is_active=True,
                category__discounts__archived=False,
                category__discounts__isnull=False,
                category__discounts__start_date__lte=today,
                category__discounts__end_date__gte=today,
            )
            | Q(
                product_groups__discounts__is_active=True,
                product_groups__discounts__archived=False,
                product_groups__discounts__isnull=False,
                product_groups__discounts__start_date__lte=today,
                product_groups__discounts__end_date__gte=today,
            )
        )
        .annotate(
            price=Min("prices__price"),
        )
        .all()
    )
    try:
        return choices(discounted_products, k=amount)
    except IndexError:
        return []