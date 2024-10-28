from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.db import transaction
from django.views.generic import CreateView, DetailView, UpdateView

from .forms import CustomUserCreationForm, ProfileChangeForm
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
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, email=email, password=password)
        if user:
            login(self.request, user=user)

        return response

    def get_success_url(self):
        return reverse_lazy("core:index")


class ProfileView(LoginRequiredMixin, UpdateView):
    """
    CBV для обновления профиля пользователя

    model - модель, с которой работаем
    form_class - форма для редактирования профиля

    """
    template_name = "account/profile.html"
    context_object_name = "profile"
    model = Profile
    form_class = ProfileChangeForm

    def get_object(self, queryset=None):
        """
        Получаем профиль пользователя
        """
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        """
        Передаем в форму в качестве инстанса профиль пользователя
        """
        context = super().get_context_data(**kwargs)
        context["profile_form"] = ProfileChangeForm(instance=self.request.user.profile)
        return context

    def form_valid(self, form):
        if form.is_valid():
            profile = form.save()
            user = profile.user
            user.email = form.cleaned_data["email"]
            user.save()
            return redirect("account:profile")
        return redirect(self.request.path)

    def get_success_url(self):
        return reverse_lazy("account:profile")


class PersonalCabinet(LoginRequiredMixin, DetailView):
    """

    CBV личного кабинета профиля пользователя
    В шаблоне присутствуют ссылки на профиль,
    на все заказы профиля пользователя

    """
    template_name = "account/personal_cabinet.html"
    context_object_name = "profile"
    model = Profile

    def get_context_data(self, **kwargs):
        """
        Атрибуты:
        profile - профиль пользователя
        last_order - последний заказ
        """
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=self.request.user)

        # Передаем последний заказ текущего профиля
        profile_orders = profile.orders.all()
        context["profile"] = profile
        context["last_order"] = profile_orders.order_by('-created_at').first()
        return context

    def get_object(self, queryset=None):
        """ Возвращаем профиль пользователя """
        return Profile.objects.get(user=self.request.user)
