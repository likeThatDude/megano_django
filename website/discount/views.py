from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db import transaction
from django.views.generic import CreateView
from django.contrib.auth.mixins import UserPassesTestMixin

from .forms import DiscountCreationForm


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

    def post(self, request, *args, **kwargs):
        """
        Создаем запись в таблице Discount в случае, если форма валидна,
        иначе возвращаем пользователя к текущей странице
        """
        form = self.form_class(self.request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

        return self.form_invalid(form)
