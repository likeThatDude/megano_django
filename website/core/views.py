from catalog.models import Category
from django.core.cache import cache
from django.db.models import Count
from django.db.models import Q
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from website.settings import BANNERS_KEY
from website.settings import CATEGORY_CASHING_TIME
from website.settings import CATEGORY_KEY

from .models import Banner


def index(request: HttpRequest) -> HttpResponse:
    categories = cache.get(CATEGORY_KEY)
    if categories is None:
        categories = (
            Category.objects.filter(archived=False)
            .annotate(products_count=Count("products", filter=Q(products__archived=False)))
            .filter(products_count__gt=0)
        )

    cache.set(CATEGORY_KEY, categories, timeout=CATEGORY_CASHING_TIME)

    random_banners = cache.get(BANNERS_KEY)
    if random_banners is None:
        random_banners = (Banner.objects.select_related('product').filter(
            Q(active=True) & Q(deadline_data__gt=timezone.now().date())).order_by("?")[:3]
                          .only('product__name', 'product__preview', 'text'))
        cache.set(BANNERS_KEY, random_banners, timeout=3)
    context = {
        "categories": categories,
        "banners": random_banners,
    }
    return render(request, "core/main_page.html", context=context)

# def about_view(request: HttpRequest):
#     return render(request, "core_1/about.html")
#
# def catalog(request: HttpRequest):
#     return render(request, "core_1/catalog.html")
#
# def comparison(request: HttpRequest):
#     return render(request, "core_1/comparison.html")
#
# @login_required
# def account(request):
#     return render(request, 'core_1/account.html')
#
# def cart(request):
#     return render(request, 'core_1/cart.html')
#
