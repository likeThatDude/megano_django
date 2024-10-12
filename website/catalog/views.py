from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import DetailView


def catalog_view(request: HttpRequest):
    return render(request, "catalog/catalog.html")


class CategoryDetailView(DetailView):
    pass
