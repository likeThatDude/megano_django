from django.core.cache import cache
from django.db.models import (
    Q,
    Prefetch,
    Min, Count,
)
from django.http import HttpRequest
from django.views.generic import DetailView, TemplateView, ListView

from website.settings import PRODUCTS_KEY
from django.shortcuts import render, redirect

from .models import Product, Seller, Price, Review, Category, Specification, Tag


# from .forms import ReviewForm
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from .models import Product, Review
# from .serializers import ProductSerializer, ReviewSerializer, ReviewFormSerializer


def catalog_view(request: HttpRequest):
    return render(request, "catalog/catalog.html")


class CatalogListView(ListView):
    template_name = "catalog/catalog.html"
    model = Product
    context_object_name = "products"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_param())
        return context

    def get_param(self):
        """Получаем дополнительные параметры для контекста."""
        return {
            "sellers": Seller.objects.all(),
            "manufactures": Product.objects.values_list('manufacture', flat=True).distinct(),
            "specifications": Specification.objects.distinct(),
            "tags": Tag.objects.filter(products__isnull=False).distinct(),
            "category_id": self.kwargs.get("pk"),
        }

    def get_queryset(self):
        """Получаем список продуктов с учетом кэширования."""
        category_id = self.kwargs.get("pk")
        cache_key = PRODUCTS_KEY.format(category_id=category_id)
        queryset = cache.get(cache_key)

        if not queryset:
            queryset = (
                super(CatalogListView, self)
                .get_queryset()
                .filter(category__id=category_id)
                .annotate(price=Min("prices__price"))
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
        selected_specification = request.POST.get("specification")

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

        return products

    def post(self, request, *args, **kwargs):
        """Обработка POST-запроса для фильтрации продуктов."""
        products = self.get_queryset()
        products = self.filter_products(products, request)

        context = self.get_param()
        context["products"] = products
        print(context)
        return render(request, self.template_name, context)


class CategoryDetailView(DetailView):
    pass


class ProductDetailView(DetailView):
    template_name = 'catalog/product_detail.html'
    model = Product
    context_object_name = 'product'

    def get_queryset(self):
        pk = self.kwargs.get('pk')

        return (Product.objects
                .select_related('category')
                .prefetch_related(
            Prefetch('images', ),
            Prefetch('review', queryset=Review.objects.select_related('user').all().order_by('-created_at'), ),
            Prefetch('price',
                     queryset=Price.objects.select_related('seller').only('seller', 'price').order_by('price')),
            Prefetch('specifications',
                     queryset=Specification.objects.select_related('name', ).order_by(
                         'name__name'))
        ).annotate(reviews_count=Count('review')).filter(pk=pk))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['storages'] = self.object.price.all()
        return context

    # class ProductDetailView(TemplateView):
    #     template_name = 'catalog/product_detail.html'
