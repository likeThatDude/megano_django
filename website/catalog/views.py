from collections import defaultdict

from django.core.cache import cache
from django.db import transaction
from django.db.models import Min
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_param())
        return context

    def get_param(self):
        """Получаем дополнительные параметры для контекста."""

        category_id = self.kwargs.get("pk")

        products_with_related = Product.objects.prefetch_related("specifications").filter(category__id=category_id)

        sellers = Seller.objects.all()
        manufactures = products_with_related.values_list("manufacture", flat=True).distinct()

        # Получаем все спецификации для всех продуктов в категории
        specifications = (
            Specification.objects.filter(product__in=products_with_related).select_related("name").distinct()
        )
        # Группируем спецификации по имени
        grouped_specifications = defaultdict(list)
        for spec in specifications:
            print("spec:", spec)
            grouped_specifications[spec.name.name].append(spec.value)

        print("spec grouped:", grouped_specifications.items)
        # Получить уникальные теги
        tags = Tag.objects.filter(products__isnull=False).distinct()
        print("tags", tags)

        return {
            "sellers": sellers,
            "manufactures": manufactures,
            "grouped_specifications": grouped_specifications.items(),
            "tags": tags,
            "category_id": category_id,
        }

    def get_queryset(self):
        """Получаем список продуктов с учетом кэширования."""
        category_id = self.kwargs.get("pk")
        cache_key = PRODUCTS_KEY.format(category_id=category_id)
        queryset = cache.get(cache_key)
        price_subquery = Price.objects.filter(product=OuterRef("pk")).values("pk")
        if not queryset:
            queryset = (
                Product.objects.filter(category__id=category_id)
                .select_related("category")
                .annotate(price=Round(Min("prices__price"), precision=2), price_pk=Subquery(price_subquery))
            )
        cache.set(cache_key, queryset, timeout=60)
        return queryset

    def filter_products(self, products, request):
        """Фильтруем продукты по выбранным параметрам."""
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

        return products

    def post(self, request, *args, **kwargs):
        """Обработка POST-запроса для фильтрации продуктов."""
        products = self.get_queryset()
        products = self.filter_products(products, request)

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
                    .all()
                    .only("product__id", "product__name", "seller", "price"),
                ),
                "delivery_methods",
                "payment_methods",
            )
            .only("name", "price")
            .filter(price__product__pk=1)
            .order_by("price__price"),
            timeout=240,
        )

        context["sellers"] = sellers_list
        return context


class ViewedListActionsView(APIView):
    serializer_class = ViewedSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=[_("views")],
        summary="Есть ли товар в списке просмотренных",
        description="Проверяет есть ли указанный товар в списке просмотренных"
        " и возвращает true если есть, иначе - false.",
    )
    def get(self, request: Request, product_id: int) -> Response:
        exists = Viewed.objects.filter(user=request.user, product_id=product_id).exists()
        return Response({"exists": exists}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=[_("views")],
        summary="Добавление/обновление товара в просмотренных",
        description="Добавляет или обновляет товар в списке просмотренных текущим пользователем."
        " Если товар еще не существует в списке, то увеличивается его количество просмотров.",
    )
    def post(self, request: Request, product_id: int) -> Response:
        with transaction.atomic():
            new_view, created = Viewed.objects.update_or_create(user=request.user, product_id=product_id)

            if created:
                product = Product.objects.select_for_update().get(id=product_id)
                product.views += 1
                product.save()

        serialized = ViewedSerializer(new_view)
        return Response(
            {"viewed": serialized.data},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        tags=[_("views")],
        summary="Удаление товара из просмотренных",
        description="Удаляет товар из списка просмотренных пользователем, "
        "возвращает логическое значение результата операции.",
    )
    def delete(self, request: Request, product_id: int) -> Response:
        deleted_rows, deleted_dict = Viewed.objects.filter(user=request.user, product_id=product_id).delete()
        return Response({"deleted": deleted_rows != 0}, status=status.HTTP_200_OK)


class ViewedListView(APIView):
    serializer_class = ViewedSerializer

    @extend_schema(
        tags=[_("views")],
        summary="Список просмотренных товаров",
        description="Возварщает список просмотренных текущим пользователем товаров (по умолчанию 20)",
    )
    def get(self, request: Request):
        limit = request.query_params.get("limit", 20)
        viewed_products = Viewed.objects.filter(user=request.user)[:limit].all()
        serialized = ViewedSerializer(viewed_products, many=True)
        return Response(
            {"viewed products": serialized.data},
            status=status.HTTP_200_OK,
        )


class ViewsCountView(APIView):
    serializer_class = ViewedSerializer

    @extend_schema(
        tags=[_("views")],
        summary="Количество просмотров товара",
        description="Возвращает количество просмотров указанного товара.",
    )
    def get(self, request: Request, product_id: int) -> Response:
        product = Product.objects.only("views").filter(id=product_id).first()
        return Response(
            {"product id": product_id, "views count": product.views},
            status=status.HTTP_200_OK,
        )
