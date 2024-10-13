from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render


def index(request):
    return render(request, "core/index.html")

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
