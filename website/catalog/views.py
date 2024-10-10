from django.http import HttpRequest
from django.shortcuts import render


def catalog_view(request: HttpRequest):
    return render(request, "catalog/catalog.html")
