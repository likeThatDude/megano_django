from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import UpdateView

from .forms import CustomUserChangeForm
from .forms import CustomUserCreationForm
from .forms import ProfileChangeForm
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


class ProfileView(LoginRequiredMixin, View):
    """
    View для управления профилем пользователя.

    Этот класс позволяет пользователю изменять свои данные профиля и пароль.
    Доступ к этому представлению возможен только для аутентифицированных пользователей.
    """

    template_name = "account/profile.html"

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос.

        Отображает форму изменения профиля и форму изменения пароля.
        """
        profile_form = ProfileChangeForm(instance=request.user.profile)
        password_form = CustomUserChangeForm(instance=request.user)
        context = {
            "profile_form": profile_form,
            "password_form": password_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос.

        Обновляет данные профиля и пароль пользователя, если формы валидны.
        """
        profile_form = ProfileChangeForm(request.POST, request.FILES, instance=request.user.profile)
        password_form = CustomUserChangeForm(request.POST, instance=request.user)

        if profile_form.is_valid() and password_form.is_valid():
            profile_form.save()
            user = request.user
            user.email = profile_form.cleaned_data.get("email", user.email)
            user.save()
            # Обновляем сессию, чтобы не разлогинивать пользователя
            update_session_auth_hash(request, password_form.save())
            messages.success(request, "Профиль успешно сохранен!")
            return redirect(self.get_success_url())

        context = {
            "profile_form": profile_form,
            "password_form": password_form,
        }
        return render(request, self.template_name, context)

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
        context["last_order"] = profile_orders.order_by("-created_at").first()
        return context

    def get_object(self, queryset=None):
        """Возвращаем профиль пользователя"""
        return Profile.objects.get(user=self.request.user)
