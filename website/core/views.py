from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

def home(request):
    return render(request, 'core/base.html')
@login_required
def profile(request):
    return render(request, 'core/base.html')

def login_view(request):
    return render(request, 'core/base.html')

def register_view(request):
    return render(request, 'core/base.html')

def logout_view(request):
    return render(request, 'core/base.html')

def about(request):
    return render(request, 'core/base.html')

def contact(request):
    return render(request, 'core/base.html')

def index(request):
    return render(request, "core/index.html")


def about_view(request: HttpRequest):
    return render(request, "core/about.html")

def catalog(request: HttpRequest):
    return render(request, "static/catalog.html")
