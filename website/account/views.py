from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm
from .models import Profile


class LogInView(LoginView):
    template_name = "account/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("core:index")


class LogOutView(LogoutView):
    pass


class RegisterView(CreateView):
    template_name = "account/register.html"
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        response = super().form_valid(form)
        # Реализовать создание профиля пользователя

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")

        return response

    def get_success_url(self):
        return reverse_lazy("core:index")


def profile_view(request: HttpRequest):
    return render(request, "account/profile.html")
