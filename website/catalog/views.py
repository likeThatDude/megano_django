from django.core.cache import cache
from django.db.models import (
    Q,
    Prefetch,
    Min, Count,
    OuterRef,
    Subquery,
)
from django.db.models.functions import Round
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView, TemplateView

from website.settings import PRODUCTS_KEY

from .models import Price, Product, Review, Specification


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
        price_subquery = Price.objects.filter(product=OuterRef('pk')).values('pk')
        if not queryset:
            queryset = (
                Product.objects
                .filter(category__id=category_id)
                .select_related('category')
                .annotate(
                    price=Round(Min("prices__price"), precision=2),
                    price_pk=Subquery(price_subquery)
                )
            )
        cache.set(cache_key, queryset, timeout=60)
        return queryset


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
