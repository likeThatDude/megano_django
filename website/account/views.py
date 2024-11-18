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
from django.views.generic import ListView
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import SetPasswordForm
from django.db.models import Prefetch

from order.models import Order, OrderItem
from .forms import CustomUserChangeForm
from .forms import CustomUserCreationForm
from .forms import ProfileChangeForm
from .forms import ProfileRegistrationForm
from .models import Profile


class LogInView(LoginView):
    template_name = "account/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse_lazy("core:index")


class LogOutView(LogoutView):
    pass


class RegisterView(CreateView):
    """
    CBV регистрации профиля пользователя
    """
    template_name = "account/register.html"
    form_class = CustomUserCreationForm
    context_object_name = "register_form"

    def get_context_data(self, **kwargs):
        """
        Передаем в шаблон контекст с формой ProfileRegistrationForm для ввода ФИО и номера телефона
        """
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context["profile_registration_form"] = ProfileRegistrationForm(self.request.POST)
        else:
            context["profile_registration_form"] = ProfileRegistrationForm()
        return context

    def form_valid(self, form):
        """
        Получаем экземпляр формы ProfileRegistrationForm, проверяем две формы на валидность
        Если проверку прошли: то сохраняем основную форму, привязываем пользователя к профилю,
        аутентифицируем пользователя, логиним
        """
        profile_form = ProfileRegistrationForm(self.request.POST)

        if profile_form.is_valid() and form.is_valid():
            user = form.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            user = authenticate(self.request, email=email, password=password)
            if user:
                login(self.request, user=user)

            return redirect(self.get_success_url())

        return self.form_invalid(form)

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
        user = self.request.user
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user=user)

        # Передаем последний заказ текущего профиля
        user_orders = user.orders.all()
        if user_orders:
            context["last_order"] = user_orders.order_by("-created_at").first()

        context["profile"] = profile
        return context

    def get_object(self, queryset=None):
        """Возвращаем профиль пользователя"""
        user = self.request.user
        queryset = Profile.objects.get(user=user)
        return queryset
        # return Profile.objects.get(user=self.request.)


class ProfileOrdersView(LoginRequiredMixin, ListView):
    """
    CBV для отображения заказов профиля.
    Доступно только аутентифицированным пользователям.
    Если у профиля имеются заказы, то отображаются, иначе
    отображается текст "У вас пустая история заказов"

    Атрибуты:
        template_name - шаблон для отображения заказов профиля пользователя

    """
    template_name = "account/profile_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        """
        Получаем queryset заказов пользователя

        Этот метод используется в представлении для загрузки всех заказов пользователя.
        Подгружается связанная модель DeliveryPrice, связанная FK с моделью Order.
        Также, подгружаем связанные сущности модели OrderItem

        Возвращает:
            список заказов пользователя с информацией о ценах: цена доставки, общая стоимость заказа,
            статус, оплачен заказ или нет.

        Примечание:
            Этот метод использует `select_related` и `prefetch_related` для оптимизации запросов, загружая только
            нужные поля и избегая ненужных запросов к базе данных.

        """
        user = self.request.user
        user_orders = Order.objects.filter(
            user=user
        ).select_related(
            "delivery_price",
        ).prefetch_related(
            Prefetch(
                "order_items",
                queryset=OrderItem.objects.select_related(
                    "delivery",
                    "payment_type",
                ).only(
                    "delivery__name",
                    "payment_type__name",
                ),
            )
        ).only(
            "delivery_price",
            "paid_status",
        )
        return user_orders


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """
    Класс представления для ввода нового пароля.

    Атрибуты:
        template_name - шаблон для отображения формы ввода нового пароля
        success_url - путь, по которому после ввода нового пароля перенаправим пользователя
        form_class - используемая форма в шаблоне
    """
    template_name = "account/password_reset_confirm.html"
    success_url = reverse_lazy("account:password_reset_complete")
    form_class = SetPasswordForm
