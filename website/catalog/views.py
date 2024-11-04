from django.core.cache import cache
from django.db.models import Min
from django.db.models import OuterRef
from django.db.models import Prefetch
from django.db.models import Subquery
from django.db.models.functions import Round
from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic import ListView

from website.settings import PRODUCTS_KEY

from .models import Price
from .models import Product
from .models import ProductImage
from .models import Seller
from .models import Specification
from .models import Tag


def catalog_view(request: HttpRequest):
    return render(request, "catalog/catalog.html")


class CatalogListView(ListView):
    template_name = "catalog/catalog.html"
    model = Product
    context_object_name = "products"

    def get_queryset(self):
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


class CategoryDetailView(DetailView):
    pass


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
                Prefetch(
                    "images",
                    queryset=ProductImage.objects.all().only(
                        "image",
                    ),
                ),
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
                "view",
                "manufacture",
                "product_type",
                "specifications",
                "images",
                "preview",
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
