from catalog.models import Price
from catalog.models import Product
from catalog.models import Specification
from comparison.models import Comparison
from django.core.cache import cache
from django.db.models import Min
from django.db.models import Prefetch
from django.db.models import QuerySet
from django.http import HttpRequest

from website.settings import anonymous_comparison_key
from website.settings import user_comparison_key


def get_products_with_auth_user(user) -> tuple:
    """
    Получает товары, добавленные пользователем в сравнение.

    Эта функция сначала пытается извлечь данные о товарах из кэша по ключу, связанному с пользователем.
    Если данные отсутствуют в кэше, выполняется запрос к базе данных для получения объектов Comparison,
    связанных с указанным пользователем. Запрос включает связанные данные о категории продукта,
    спецификациях и ценах. Также вычисляется минимальная цена для каждого товара.

    Параметры:
    ----------
    user : User
        id аутентифицированного пользователя, чьи товары необходимо получить.

    Возвращает:
    ----------
    tuple
        - correct_spec: Спецификации товаров, отформатированные для дальнейшей обработки.
        - products_data: Список объектов Comparison, представляющих товары, добавленные в сравнение.
    """
    key = f"{user_comparison_key}{user}"
    products = cache.get(key)
    if products is None:
        products = (
            Comparison.objects.select_related("user", "product__category")
            .prefetch_related(
                Prefetch(
                    "product__specifications",
                    queryset=Specification.objects.select_related("name", "product").only(
                        "value", "name__name", "product__id"
                    ),
                ),
                Prefetch(
                    "product__prices", queryset=Price.objects.select_related("product").only("product__id", "price")
                ),
            )
            .filter(user__pk=user)
            .annotate(min_price=Min("product__prices__price"))
            .only(
                "user__id",
                "product__name",
                "product__category__name",
                "product__specifications",
                "product__preview",
                "product__product_type",
            )
        )
        cache.set(key, products, timeout=3600)
    correct_spec = get_category_spec(products)
    products_data = list(products)
    return correct_spec, products_data


def get_products_with_unauth_user(request: HttpRequest) -> tuple:
    """
    Получает список товаров для неаутентифицированного пользователя.

    Эта функция извлекает id товаров из сессии пользователя,
    формирует уникальный ключ для кеша, а затем пытается получить
    товары из кеша. Если товары не найдены в кеше, они извлекаются
    из базы данных с использованием оптимизации выборки, включая
    связанные модели (категории, спецификации и цены).

    Затем возвращается корректированный список спецификаций и данные о товарах.

    Параметры:
    ----------
    request : HttpRequest
        Объект запроса, содержащий информацию о сессии пользователя
        и идентификаторах товаров.

    Возвращает:
    ----------
    tuple
        Кортеж, содержащий:
            - correct_spec : список спецификаций, скорректированных по категориям;
            - products_data : список товаров с минимальными ценами и
              другими атрибутами (название, категория, спецификации и т.д.).

    Примечание:
    ----------
    Если пользователь неаутентифицирован, идентификаторы товаров
    хранятся в сессии и кешируются для оптимизации последующих
    запросов.
    """
    products_ids = request.session.get("products_ids", [])
    # request.session["products_ids"] = ['1']
    print(products_ids)
    key = f"{anonymous_comparison_key}{request.session.session_key}"
    products = cache.get(key)
    if products is None:
        products = (
            Product.objects.select_related("category")
            .prefetch_related(
                Prefetch(
                    "specifications",
                    queryset=Specification.objects.select_related("name", "product").only(
                        "value", "name__name", "product__id"
                    ),
                ),
                Prefetch("prices", queryset=Price.objects.select_related("product").only("product__id", "price")),
            )
            .filter(id__in=products_ids)
            .annotate(min_price=Min("prices__price"))
            .only("name", "category__name", "specifications", "preview", "product_type")
        )
        cache.set(key, products, timeout=3600)
    correct_spec = get_category_spec(products, False)
    products_data = list(products)
    return correct_spec, products_data


def create_categorization(products: list, auth_flag: bool = True) -> dict:
    """
    Создает категоризацию списка товаров по категориям.

    Параметры:
    ----------
        products (list): Список объектов товаров, которые необходимо категоризировать.
        auth_flag (bool): Флаг, указывающий, является ли пользователь аутентифицированным.

    Возвращает:
    ----------
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
    ----------
        products (QuerySet): Запрос, содержащий объекты товаров.
        auth_flag (bool): Флаг, указывающий, является ли пользователь аутентифицированным.

    Возвращает:
    ----------
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
