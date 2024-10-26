from itertools import product
from unicodedata import category

from django.contrib.auth.models import User
from django.db.models import Prefetch, QuerySet, Min
from django.http import HttpRequest

from catalog.models import Product, Specification, Storage
from comparison.models import Comparison


def get_products_with_auth_user(user) -> tuple:
    products = (Comparison.objects
                .select_related('user', 'product__category')
                .prefetch_related(
        Prefetch(
            'product__specifications',
            queryset=Specification.objects.select_related('name'),
        ),
        Prefetch(
            'product__storage',
            queryset=Storage.objects.only('price')
        )
    )
                .filter(user=user)
                .annotate(min_price=Min('product__storage__price')))
    correct_spec = get_category_spec(products)
    products_data = list(products)
    return correct_spec, products_data


def get_products_with_unauth_user(request: HttpRequest) -> tuple:
    products_ids = request.session.get('products_ids', [])
    products = (Product.objects
                .select_related('category')
                .prefetch_related(
        Prefetch(
            'specifications',
            queryset=Specification.objects.select_related('name')
        ),
        Prefetch(
            'storage',
            queryset=Storage.objects.only('price')
        )
    )
                .filter(id__in=products_ids)
                .annotate(min_price=Min('storage__price')))
    correct_spec = get_category_spec(products, False)
    products_data = list(products)
    return correct_spec, products_data


def create_categorization(products: list, auth_flag: bool = True) -> dict:
    products_list = dict()
    for product in products:
        if auth_flag:
            category = product.product.category
        else:
            category = product.category
        products_list.setdefault(category, []).append(product)
    return products_list


def get_category_spec(products: QuerySet, auth_flag: bool = True) -> dict:
    category_spec = dict()
    for comparison in products:
        if auth_flag:
            product = comparison.product
        else:
            product = comparison
        category_spec.setdefault(product.category.name, [])
        for spec in product.specifications.all():
            if spec.name.name not in category_spec[product.category.name]:
                category_spec[product.category.name].append(spec.name.name)

    return category_spec
