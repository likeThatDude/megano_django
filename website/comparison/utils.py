from itertools import product

from catalog.models import Price
from catalog.models import Product
from catalog.models import Specification
from comparison.models import Comparison
from django.core.cache import cache
from django.db.models import Count
from django.db.models import F
from django.db.models import Min
from django.db.models import OuterRef
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import Subquery
from django.http import HttpRequest

from website.settings import anonymous_comparison_key
from website.settings import user_comparison_key


def get_products_with_auth_user(user, unic_spec: None | str) -> tuple:
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
    unic_spec : None | str
        Передаёт состояние чекбокса в шаблоне, если пользователь не хочет видеть
        одинаковые характеристики, то с бд загружаются только разные характеристики

    Возвращает:
    ----------
    tuple
        - correct_spec: Спецификации товаров, отформатированные для дальнейшей обработки.
        - products_data: Список объектов Comparison, представляющих товары, добавленные в сравнение.
    """
    key = f"{user_comparison_key}{user}{unic_spec}"
    products = cache.get(key)

    if products is None:
        common_specifications = list()
        if unic_spec:
            common_specifications = get_unic_spec_for_auth_user(user)

        products = (
            Comparison.objects.select_related("user", "product__category")
            .prefetch_related(
                Prefetch(
                    "product__specifications",
                    queryset=Specification.objects.select_related("name", "product")
                    .only("value", "name__name", "product__id")
                    .exclude(id__in=common_specifications),
                ),
                Prefetch(
                    "product__prices", queryset=Price.objects.select_related("product").only("product__id", "price")
                ),
            )
            .filter(user__pk=user)
            .only(
                "user__id",
                "product__name",
                "product__category__name",
                "product__specifications",
                "product__preview",
                "product__product_type",
            )
            .annotate(min_price=Min("product__prices__price"))
        )
        cache.set(key, products, timeout=3600)
    correct_spec = get_category_spec(products)
    products_data = list(products)
    return correct_spec, products_data


def get_products_with_unauth_user(request: HttpRequest, unic_spec: None | str) -> tuple:
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
    unic_spec : None | str
        Передаёт состояние чекбокса в шаблоне, если пользователь не хочет видеть
        одинаковые характеристики, то с бд загружаются только разные характеристики

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
    key = f"{anonymous_comparison_key}{request.session.session_key}{unic_spec}"
    products = cache.get(key)

    if products is None:
        common_specifications = list()
        if unic_spec:
            common_specifications = get_unic_spec_for_unauth_user(products_ids)
        products = (
            Product.objects.select_related("category")
            .prefetch_related(
                Prefetch(
                    "specifications",
                    queryset=Specification.objects.select_related("name", "product")
                    .only("value", "name__name", "product__id")
                    .exclude(id__in=common_specifications),
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


def get_unic_spec_for_auth_user(user: int) -> list[int]:
    """
    Получает список уникальных спецификаций для заданного пользователя, основываясь на категориях
    товаров в их сравнении. Сравнивает количество товаров в категории с количеством товаров
    в каждой спецификации и возвращает ID спецификаций, которые соответствуют этому условию.

    Параметры:
    ----------
    user (int): ID пользователя, для которого выполняется запрос.

    Возвращает:
    ----------
    list[int]: Список ID спецификаций, соответствующих условиям запроса.
    """
    subquery = (
        Comparison.objects.select_related("product__category")
        .filter(Q(user=user) & Q(product__category=OuterRef("product__category")))
        .values("product__category")
        .annotate(category_count=Count("id"))
        .values("category_count")
    )

    common_specifications = list(
        Comparison.objects.select_related("user", "product__category")
        .prefetch_related(
            Prefetch(
                "product__specifications",
                queryset=Specification.objects.select_related("name", "product").only(
                    "value", "name__name", "product__id"
                ),
            )
        )
        .values(
            "product__specifications__name__name",
            "product__specifications__value",
            "product__category",
        )
        .annotate(
            product_count=Count("product"),
            category_count=Subquery(subquery),
        )
        .filter(Q(user=user) & Q(product_count=F("category_count")))
    )

    if common_specifications:
        spec_ids = (
            Specification.objects.select_related("name", "product")
            .filter(
                Q(value__in=list(spec_value["product__specifications__value"] for spec_value in common_specifications))
                & Q(
                    name__name__in=list(
                        spec_name["product__specifications__name__name"] for spec_name in common_specifications
                    )
                )
            )
            .values_list("id", flat=True)
        )
        return list(spec_ids)
    return list()


def get_unic_spec_for_unauth_user(products_ids: list[int]) -> list[int]:
    """
    Получает список уникальных спецификаций для заданного пользователя, основываясь на категориях
    товаров в их сравнении. Сравнивает количество товаров в категории с количеством товаров
    в каждой спецификации и возвращает ID спецификаций, которые соответствуют этому условию.

    Параметры:
    ----------
    products_ids: list[int]: ID продуктов полученных из сессии.

    Возвращает:
    ----------
    list[int]: Список ID спецификаций, соответствующих условиям запроса.
    """
    subquery = (
        Product.objects.select_related("category")
        .filter(Q(category=OuterRef("category")) & Q(id__in=products_ids))
        .values("category")
        .annotate(category_count=Count("id"))
        .values("category_count")
    )

    common_specifications = (
        Product.objects.select_related("category")
        .prefetch_related(
            Prefetch(
                "specifications",
                queryset=Specification.objects.select_related("name", "product").only(
                    "value", "name__name", "product__id"
                ),
            )
        )
        .values(
            "specifications__name__name",
            "specifications__value",
            "category",
        )
        .annotate(
            product_count=Count("specifications"),
            category_count=Subquery(subquery),
        )
        .filter(Q(id__in=products_ids) & Q(product_count=F("category_count")))
    )

    if common_specifications:
        spec_ids = (
            Specification.objects.select_related("name", "product")
            .filter(
                Q(value__in=list(spec_value["specifications__value"] for spec_value in common_specifications))
                & Q(
                    name__name__in=list(spec_name["specifications__name__name"] for spec_name in common_specifications)
                ),
            )
            .values_list("id", flat=True)
        )
        return list(spec_ids)
    return list()
