from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import UpdateView

from .forms import DiscountCreationForm
from .models import Discount


class DiscountCreateView(UserPassesTestMixin, CreateView):
    """
    Представление для отображения формы создания скидок:
        - скидка на товары
        - скидка на корзину
        - скидка на группу товаров

    Доступно только аутентифицированному пользователя, у которого есть права админа.
    """

    template_name = "discount/discount_create.html"
    form_class = DiscountCreationForm

    def test_func(self) -> bool:
        """
        Метод test_func, чтобы не пропускать запросы
        не аутентифицированного пользователя без прав администратора
        """
        if not self.request.user.is_staff:
            return False

        return True

    def form_valid(self, form):
        """
        Если форма валидна, сохраняем объект и выполняем перенаправление.
        """
        with transaction.atomic():
            self.object = form.save()

        return super().form_valid(form)


class DiscountUpdateView(UserPassesTestMixin, UpdateView):
    """
    Представление для обновления записи скидки

    Атрибуты:
        template_name - шаблон для отображения формы обновления скидки
        model - модель, которую обновляем
        form_class - форма для обновления записи о скидке
        success_url - путь для перенаправления после успешного обновления

    Применяем UserPassesTestMixin для того, чтобы только админ
    мог обновлять запись о скидке
    """

    template_name = "discount/discount_update.html"
    model = Discount
    form_class = DiscountCreationForm
    success_url = reverse_lazy("discount:discount-list")

    def get_object(self, queryset=None):
        """
        Получаем запись модели Discount из базы данных по полю slug
        """
        queryset = get_object_or_404(Discount, slug=self.kwargs["slug"])
        return queryset

    def test_func(self):
        """
        Метод test_func, чтобы не пропускать запросы
        не аутентифицированного пользователя без прав администратора
        """
        return self.request.user.is_staff

    def get_success_url(self):
        """
        Определяем путь для перенаправления после успешного обновления записи.
        """
        return reverse_lazy(
            "discount:discount-update",
            kwargs={"slug": self.object.slug},
        )
