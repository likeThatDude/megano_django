from django.http import HttpRequest
from django.shortcuts import render


def index(request):
    context = {
        "random_banner": [
            {'name': 'TV',
             'model': '123',
             'manufacturer': 'SAMSUNG',
             'text': 'super TV'},
            {'name': 'CAMERA',
             'model': '000',
             'manufacturer': 'LG',
             'text': 'super Camera'},
    ]}
    return render(request, "core/base.html", context=context)


def about_view(request: HttpRequest):
    return render(request, "core/about.html")
