from collections import defaultdict
from itertools import product

from django.core.cache import cache
from django.db import transaction
from django.db.models import (
    Min,
    Count,
    Max,
    Sum,
)
from django.db.models import Min, Q
from django.db.models import OuterRef
from django.db.models import Prefetch
from django.db.models import Subquery
from django.db.models.functions import Round
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import ListView
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from website.settings import PRODUCTS_KEY

from .models import Price
from .models import Product
from .models import ProductImage
from .models import Seller
from .models import Specification
from .models import Tag
from .models import Viewed
from .serializers import ViewedSerializer
from .utils import generate_sort_param, sort_convert
from .models import ViewedSession


def catalog_view(request: HttpRequest):
    return render(request, "catalog/catalog.html")


class CatalogListView(ListView):
    """
    Представление для отображения списка продуктов в каталоге.

    Это представление обрабатывает запросы на отображение продуктов в
    определенной категории, предоставляет возможность фильтрации по
    различным параметрам, таким как продавцы, производители,
    ограниченные серии, диапазон цен, название, спецификации и теги.

    Атрибуты:
        template_name (str): Путь к шаблону, который будет использоваться для отображения.
        model (Model): Модель, используемая для получения данных (Product).
        context_object_name (str): Имя контекста, под которым будут доступны продукты в шаблоне.

    """

    template_name = "catalog/catalog.html"
    model = Product
    context_object_name = "products"
    paginate_by = 12

    def get_context_data(self, **kwargs):
        """
            Получаем контекст для шаблона.

            Объединяет контекст, предоставляемый родительским классом, с дополнительными
            параметрами, полученными из метода get_param.

            Параметры:
                **kwargs: Дополнительные именованные аргументы.

            Возвращает:
                dict: Объединенный контекст для шаблона.
        """
        context = super().get_context_data(**kwargs)
        context.update(self.get_param())
        return context

    def sort_queryset(self, queryset, sort):
        """
            Сортирует набор данных по заданному параметру.

            Обновляет параметры сортировки в сессии и сортирует переданный
            queryset в соответствии с указанным параметром.

            Параметры:
                queryset (QuerySet): Набор данных, который необходимо отсортировать.
                sort (str): Параметр сортировки.

            Возвращает:
                QuerySet: Отсортированный набор данных.
        """
        sort_convert(self.request.session, sort)
        return queryset.order_by(sort)

    def get_last_sort(self, session):
        """
            Получает последний использованный параметр сортировки из сессии.

            Параметры:
                session (dict): Словарь сессии, содержащий параметры сортировки.

            Возвращает:
                str: Параметр последней сортировки или None, если сортировка не была установлена.
        """
        for key, value in session["sort_catalog"].items():
            if value["style"]:
                return value["param"]

    def get_param(self):
        """
            Получаем дополнительные параметры для контекста.

            Собирает информацию о продуктах, продавцах, производителях, спецификациях и тегах
            для текущей категории и возвращает это в виде словаря.

            Возвращает:
                dict: Словарь с дополнительными параметрами для контекста.
        """

        category_id = self.kwargs.get("pk")

        products_with_related = Product.objects.prefetch_related("specifications").filter(category__id=category_id)

        sellers = Seller.objects.all()
        manufactures = products_with_related.values_list("manufacture", flat=True).distinct()

        # Получаем все спецификации для всех продуктов в категории
        specifications = (
            Specification.objects.filter(product__in=products_with_related).distinct()
        )

        # Группируем спецификации по имени
        grouped_specifications = defaultdict(set)
        for spec in specifications:
            grouped_specifications[spec.name.name].add(spec.value)

        # Получить уникальные теги
        tags = Tag.objects.filter(products__isnull=False).distinct()

        if "sort_catalog" not in self.request.session:
            self.request.session["sort_catalog"] = generate_sort_param()
        sorting = self.request.session["sort_catalog"]

        return {
            "sellers": sellers,
            "manufactures": manufactures,
            "grouped_specifications": grouped_specifications.items(),
            "tags": tags,
            "sort": sorting,
            "category_id": category_id,
        }

    def get_queryset(self):
        """
            Получаем список продуктов с учетом кэширования.

            Извлекает список продуктов для текущей категории, используя кэш для
            повышения производительности. Если кэш пуст, выполняет запрос к базе данных.

            Возвращает:
                QuerySet: Набор данных с продуктами для текущей категории.
        """
        category_id = self.kwargs.get("pk")
        cache_key = PRODUCTS_KEY.format(category_id=category_id)
        queryset = cache.get(cache_key)
        price_subquery = Price.objects.filter(product=OuterRef("pk")).values("pk")
        if not queryset:
            queryset = (
                Product.objects.filter(category__id=category_id, archived=False)
                .select_related("category")
                .annotate(
                    price=Round(Min("prices__price"), precision=2),
                    price_pk=Subquery(price_subquery),
                    quantity=Sum("prices__sold_quantity"),
                    date=Max("prices__created_at"),
                    rating=Count("review__created_at"),
                )
            )

        cache.set(cache_key, queryset, timeout=60)

        sort = self.request.GET.get("sort")
        if sort:
            sort_convert(self.request.session, sort)
            queryset = self.sort_queryset(queryset, sort)
        return queryset

    def filter_products(self, products, request):
        """
            Фильтруем продукты по выбранным параметрам.

            Этот метод применяет фильтры к переданному набору продуктов на основе
            выбранных пользователем параметров, таких как продавцы, производители,
            диапазон цен, название, спецификации и теги.

            Параметры:
                products (QuerySet): Набор данных с продуктами, к которому будут применены фильтры.
                request (HttpRequest): Объект запроса, содержащий параметры фильтрации.

            Возвращает:
                QuerySet: Отфильтрованный набор данных с продуктами.
        """
        selected_sellers = request.POST.getlist("seller[]")
        selected_manufactures = request.POST.getlist("manufacture[]")
        selected_limited_edition = request.POST.get("limited_edition")
        selected_range_price = request.POST.get("price")
        selected_title = request.POST.get("title")
        selected_specifications = request.POST.getlist("specification")
        selected_tags = request.POST.getlist("tags")


        # Фильтрация по диапазону цен
        if selected_range_price:
            try:
                price_min, price_max = map(float, selected_range_price.split(";"))
                products = products.filter(price__range=[price_min, price_max])
            except ValueError:
                pass  # Игнорируем ошибку, если значения некорректные

        # Фильтрация по названию
        if selected_title:
            products = products.filter(name__icontains=selected_title)

        # Фильтрация по продавцам
        if selected_sellers:
            products = products.filter(prices__seller__id__in=selected_sellers)

        # Фильтрация по производителям
        if selected_manufactures:
            products = products.filter(manufacture__in=selected_manufactures)

        # Фильтрация по ограниченным сериям
        if selected_limited_edition:
            products = products.filter(limited_edition=True)

        # Фильтрация по характеристикам
        if selected_specifications:
            products = products.filter(specifications__value__in=selected_specifications).distinct()

        # Фильтрация по тегам
        if selected_tags:
            products = products.filter(tags__id__in=selected_tags).distinct()

        last_sort = self.get_last_sort(self.request.session)
        # Сортировка
        if last_sort:
            products = products.order_by(last_sort)

        return products

    def clear_cache(self, category_id):
        """
            Метод для очистки кэша по категории.

            Этот метод удаляет кэшированные данные для заданной категории, что
            позволяет обновить информацию о продуктах.

            Параметры:
                category_id (int): Идентификатор категории, для которой нужно очистить кэш.

            Возвращает:
                None
        """
        cache_key = PRODUCTS_KEY.format(category_id=category_id)
        cache.delete(cache_key)  # Очистка кэша по ключу

    def post(self, request, *args, **kwargs):
        """
            Обработка POST-запроса для фильтрации продуктов.

            Этот метод обрабатывает POST-запросы, применяет фильтры к продуктам
            и обновляет кэш, если данные были изменены.

            Параметры:
                request (HttpRequest): Объект запроса, содержащий данные для фильтрации.
                *args: Дополнительные позиционные аргументы.
                **kwargs: Дополнительные именованные аргументы.

            Возвращает:
                HttpResponse: Ответ с отфильтрованными продуктами и контекстом для шаблона.
        """
        products = self.get_queryset()
        products = self.filter_products(products, request)

        # очистка кэша после изменения данных
        category_id = self.kwargs.get("pk")  # Получаем ID категории из URL
        self.clear_cache(category_id)  # Очищаем кэш для данной категории

        context = self.get_param()

        context["products"] = products
        return render(request, self.template_name, context)


class ProductDetailView(DetailView):
    """
    Представление для отображения детальной информации о товаре.

    Атрибуты:
        template_name (str): Путь к шаблону, который будет использоваться для отображения страницы продукта.
        model (Product): Модель, используемая для получения информации о товаре.
        context_object_name (str): Имя объекта контекста для передачи в шаблон.
    """

    template_name = "catalog/product_detail.html"
    model = Product
    context_object_name = "product"

    def get_queryset(self):
        """
        Получает набор запросов для конкретного товара по его первичному ключу.

        Возвращает:
            QuerySet: Набор запросов, содержащий выбранный товар с его категориями, изображениями, ценами и спецификациями.
        """
        pk = self.kwargs.get("pk")

        product_data = (
            Product.objects.prefetch_related(
                Prefetch(
                    "tags",
                    queryset=Tag.objects.all().only(
                        "name",
                    ),
                ),
                Prefetch("images", queryset=ProductImage.objects.all()),
                Prefetch(
                    "specifications",
                    queryset=Specification.objects.select_related(
                        "name",
                        "product",
                    )
                    .all()
                    .only("name__name", "value", "product__id"),
                ),
            )
            .only(
                "name",
                "tags",
                "description",
                "views",
                "manufacture",
                "product_type",
                "specifications",
                "images",
                "preview",
                "short_description",
            )
            .filter(pk=pk)
        )

        return product_data

    def get_object(self, queryset=None):
        """
        Получает объект товара по первичному ключу с использованием кэширования.

        Если объект уже кэширован, возвращает его из кэша.
        В противном случае запрашивает объект из базы данных,
        кэширует его и затем возвращает.

        Аргументы:
            queryset (QuerySet, optional): Набор запросов для фильтрации объектов.
                Если не указан, используется стандартный набор запросов.

        Возвращает:
            Product: Экземпляр модели Product, соответствующий указанному первичному ключу.
        """
        pk = self.kwargs.get("pk")
        cache_key = f"Product_{pk}"
        product_data = cache.get(cache_key)
        if product_data is None:
            product_data = super().get_object(queryset)
            cache.set(cache_key, product_data, 240)
        return product_data

    def get_context_data(self, **kwargs):
        """
        Получает контекст для рендеринга шаблона.

        Параметры:
            **kwargs: Дополнительные параметры, передаваемые в контекст.

        Возвращает:
            dict: Контекст, содержащий информацию о товаре и доступные цены.
        """
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk")
        sellers_list = cache.get_or_set(
            f"Seller-{pk}",
            Seller.objects.prefetch_related(
                Prefetch(
                    "price",
                    queryset=Price.objects.select_related("product")
                    .filter(Q(product__id=pk))
                    .only("product__id", "product__name", "seller", "price"),
                ),
                "delivery_methods",
                "payment_methods",
            )
            .only(
                "name",
                "price",
                "image",
            )
            .filter(Q(price__product__pk=pk))
            .order_by("price__price"),
            timeout=240,
        )

        # Если пользователь авторизован, добавляется запись просмотра в БД
        if self.request.user.is_authenticated:
            Viewed.add_viewed_product(product_id=pk, user=self.request.user)
        else:
            # иначе, запись о просмотре добавляется в сессию
            viewed = ViewedSession(self.request)
            viewed.add(product_id=pk)

        context["sellers"] = sellers_list
        return context
