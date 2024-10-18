from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone


from catalog.models import Category
from .models import Banner
from website.settings import CATEGORY_CASHING_TIME, CATEGORY_KEY, BANNERS_KEY


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

    random_banners = cache.get(BANNERS_KEY)
    if random_banners is None:
        random_banners = (
            Banner.objects
            .filter(Q(active=True) & Q(deadline_data__gt=timezone.now().date()))
            .order_by('?')[:3]
        )
        print(random_banners)
        cache.set(BANNERS_KEY, random_banners, timeout=3)

    context = {
        "categories": categories,
        "banners": random_banners,
    }
    return render(request, "core/index.html", context=context)

def about_view(request: HttpRequest):
    return render(request, "core/about.html")

def catalog(request: HttpRequest):
    return render(request, "core/catalog.html")

def comparison(request: HttpRequest):
    return render(request, "core/comparison.html")

@login_required
def account(request):
    return render(request, 'core/account.html')

def cart(request):
    return render(request, 'core/cart.html')

def login(request):
    return render(request, 'core/login.html')

def registr(request):
    return render(request, 'core/registr.html')
