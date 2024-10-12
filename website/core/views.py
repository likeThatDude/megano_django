from django.core.cache import cache
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from catalog.models import Category
from website.settings import CATEGORY_CASHING_TIME, CATEGORY_KEY


def index(request: HttpRequest) -> HttpResponse:
    categories = cache.get(CATEGORY_KEY)
    if categories is None:
        categories = (
            Category.objects.filter(archived=False)
            .annotate(
                products_count=Count("products", filter=Q(products__archived=False))
            )
            .filter(products_count__gt=0)
        )

    cache.set(CATEGORY_KEY, categories, timeout=CATEGORY_CASHING_TIME)
    return render(request, "core/index.html", context={"categories": categories})


def about_view(request: HttpRequest):
    return render(request, "core/about.html")
