from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from django.utils.translation import gettext_lazy as _

from .forms import DiscountCreationForm
from .models import Discount
from cart.cart import Cart


class DiscountDetailView(UserPassesTestMixin, DetailView):
    model = Discount
    context_object_name = 'discount'
    template_name = "discount/discount_detail.html"

    def test_func(self) -> bool:
        """
        Метод test_func, чтобы не пропускать запросы
        не аутентифицированного пользователя без прав администратора
        """
        if not self.request.user.is_staff:
            return False

        return True

    def __get_description_type_discount(self):
        """Возвращает описание типа скидки"""
        if self.object.kind == "PT":
            return _("product discount")
        elif self.object.kind == "ST":
            return _("discount on a set of products")
        elif self.object.kind == "CT":
            cart = Cart(self.request)
            return _("discount on the shopping cart")

    def __get_description_method_discount(self):
        """Возвращает описание метода расчета скидки"""
        if self.object.method == "PT":
            return _("percentage discount")
        elif self.object.method == "SM":
            cost_discount = self.object.total_cost_l
            return _("the discount is valid from a certain cost {cost_discount}")
        elif self.object.method == "FD":
            return _("fixed discount amount")

    def __get_priority_discount(self):
        """Возвращает приоритетность скидки"""
        if self.object.priority == 1:
            return _("the lowest")
        elif self.object.priority == 2:
            return _("low")
        elif self.object.priority == 3:
            return _("middle")
        elif self.object.priority == 4:
            return _("high")
        elif self.object.priority == 5:
            return _("the highest")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        description_type = self.__get_description_type_discount()
        description_method = self.__get_description_method_discount()
        description_priority = self.__get_priority_discount()

        if self.object.kind == "PT":
            context["products"] = self.object.products
        elif self.object.kind == "ST":
            context["product_groups"] = self.object.product_groups
        elif self.object.kind == "CT":
            quantity_l = self.object.quantity_l
            quantity_g = self.object.quantity_g
            total_cost_l = self.object.total_cost_l
            context["cart_products"] = {
                "quantity_l": quantity_l,
                "quantity_g": quantity_g,
                "total_cost_l": total_cost_l,
            }

        if self.object.method == "PT":
            context['percent'] = self.object.percent
        elif self.object.method == "SM":
            context["sum_discount"] = self.object.price
        elif self.object.method == "FD":
            context["fixed_price"] = self.object.price

        context["description_type"] = description_type
        context["description_method"] = description_method
        context["description_priority"] = description_priority
        context["description"] = self.object.description
        context["start_date"] = self.object.start_date
        context["end_date"] = self.object.end_date
        context["is_active"] = self.object.is_active
        context["archived"] = self.object.archived
        return context


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
