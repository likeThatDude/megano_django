from django.http import HttpRequest
from django.shortcuts import render


def index(request):
    return render(request, "core/index.html")


def about_view(request: HttpRequest):
    return render(request, "core/about.html")
