from catalog.models import Category
from website.settings import CATEGORY_CASHING_TIME
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page


@cache_page(CATEGORY_CASHING_TIME)
def index(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.filter(archived=False)
    return render(request, "core/index.html", context={"categories": categories})


def about_view(request: HttpRequest):
    return render(request, "core/about.html")
