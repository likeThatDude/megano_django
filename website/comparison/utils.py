from catalog.models import Price
from catalog.models import Product
from catalog.models import Specification
from comparison.models import Comparison
from django.db.models import Min
from django.db.models import Prefetch
from django.db.models import QuerySet
from django.http import HttpRequest


def get_products_with_auth_user(user) -> tuple:
    """
    Получает товары, связанные с аутентифицированным пользователем.

    Параметры:
        user (User): Объект пользователя, для которого необходимо получить товары.

    Возвращает:
        tuple: Кортеж, содержащий:
            - dict: Спецификации категорий товаров.
            - list: Список объектов товаров, связанных с пользователем.
    """
    products = (
        Comparison.objects.select_related("user", "product__category")
        .prefetch_related(
            Prefetch(
                "product__specifications",
                queryset=Specification.objects.select_related("name"),
            ),
            Prefetch("product__price", queryset=Price.objects.only("price")),
        )
        .filter(user=user)
        .annotate(min_price=Min("product__price__price"))
    )
    correct_spec = get_category_spec(products)
    products_data = list(products)
    return correct_spec, products_data


def get_products_with_unauth_user(request: HttpRequest) -> tuple:
    """
    Получает товары для неаутентифицированного пользователя на основе идентификаторов в сессии.

    Параметры:
        request (HttpRequest): Объект HTTP-запроса, содержащий информацию о сессии.

    Возвращает:
        tuple: Кортеж, содержащий:
            - dict: Спецификации категорий товаров.
            - list: Список объектов товаров, идентификаторы которых находятся в сессии.
    """
    products_ids = request.session.get("products_ids", [])
    products = (
        Product.objects.select_related("category")
        .prefetch_related(
            Prefetch("specifications", queryset=Specification.objects.select_related("name")),
            Prefetch("price", queryset=Price.objects.only("price")),
        )
        .filter(id__in=products_ids)
        .annotate(min_price=Min("price__price"))
    )
    correct_spec = get_category_spec(products, False)
    products_data = list(products)
    return correct_spec, products_data


def create_categorization(products: list, auth_flag: bool = True) -> dict:
    """
    Создает категоризацию списка товаров по категориям.

    Параметры:
        products (list): Список объектов товаров, которые необходимо категоризировать.
        auth_flag (bool): Флаг, указывающий, является ли пользователь аутентифицированным.

    Возвращает:
        dict: Словарь, где ключами являются названия категорий, а значениями — списки товаров, относящихся к каждой категории.
    """
    products_list = dict()
    for product in products:
        if auth_flag:
            category = product.product.category
        else:
            category = product.category
        products_list.setdefault(category, []).append(product)
    return products_list


def get_category_spec(products: QuerySet, auth_flag: bool = True) -> dict:
    """
    Получает спецификации товаров, сгруппированные по категориям.

    Параметры:
        products (QuerySet): Запрос, содержащий объекты товаров.
        auth_flag (bool): Флаг, указывающий, является ли пользователь аутентифицированным.

    Возвращает:
        dict: Словарь, где ключами являются названия категорий, а значениями — списки названий спецификаций для каждой категории.
    """
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
