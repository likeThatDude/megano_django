from django.http import HttpRequest
from django.shortcuts import render


def login_view(request: HttpRequest):
    return render(request, "account/login.html")


def register_view(request: HttpRequest):
    return render(request, "account/register.html")


def profile_view(request: HttpRequest):
    return render(request, "account/profile.html")
