from catalog.models import Product
from django.core.cache import cache
from django.db import IntegrityError
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView
from django.views.generic import TemplateView

from website.settings import anonymous_comparison_key
from website.settings import user_comparison_key

from . import utils
from .models import Comparison
from .utils import create_categorization


class ComparisonView(TemplateView):
    """
    Представление для отображения страницы сравнения товаров.

    Атрибуты:
        template_name (str): Путь к шаблону, который будет использоваться для отображения.
    """

    template_name = "comparison/comparison.html"

    def get_context_data(self, **kwargs):
        """
        Получает контекст для рендеринга шаблона.

        Параметры:
            **kwargs: Дополнительные параметры, передаваемые в контекст.

        Возвращает:
            dict: Контекст, содержащий товары для сравнения и спецификации категорий.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            comparison_products = utils.get_products_with_auth_user(user.pk)
            data = create_categorization(comparison_products[1])
            context["comparison_products"] = data
            context["correct_spec"] = comparison_products[0]
        else:
            comparison_products = utils.get_products_with_unauth_user(self.request)
            data = create_categorization(comparison_products[1], False)
            context["comparison_products"] = data
            context["correct_spec"] = comparison_products[0]
        return context


# Переписать при помощи DRF пока так пока не готовы зависимые элементы.
class ComparisonDeleteView(DeleteView):
    """
    View для удаления товара из списка сравнения.

    Этот класс обрабатывает POST-запросы для удаления товара из списка
    сравнения как для аутентифицированных, так и для неаутентифицированных
    пользователей.

    Атрибуты:
        model (Comparison): Модель, связанная с данной View для удаления.
        success_url (str): URL-адрес, на который будет перенаправлен
        пользователь после успешного удаления товара.

    Параметры:
        request (HttpRequest): Объект HTTP-запроса, содержащий информацию о запросе.
        *args: Неименованные аргументы, переданные в метод.
        **kwargs: Именованные аргументы, переданные в метод, включая идентификатор товара.

    Возвращает:
        HttpResponseRedirect: Перенаправление на страницу успешного удаления или
        на страницу сравнения, в зависимости от статуса аутентификации пользователя.
    """

    model = Comparison
    success_url = reverse_lazy("comparison:comparison_page")

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Обрабатывает POST-запрос на удаление товара из списка сравнения.

        Если пользователь аутентифицирован, товар удаляется из базы данных,
        и кэш для этого пользователя очищается. Если пользователь не аутентифицирован,
        товар удаляется из сессии пользователя, и соответствующий кэш очищается.

        Параметры:
            request (HttpRequest): Объект HTTP-запроса, содержащий информацию о запросе.
            *args: Неименованные аргументы, переданные методу.
            **kwargs: Именованные аргументы, переданные методу, включая идентификатор товара.

        Возвращает:
            HttpResponseRedirect: Перенаправление на страницу успешного удаления
            или на страницу сравнения.
        """
        if request.user.is_authenticated:
            self.object = self.get_object()
            self.object.delete()

            cache_key = f"{user_comparison_key}{request.user.id}"
            cache.delete(cache_key)

            return HttpResponseRedirect(self.get_success_url())
        else:
            product_session_id = request.session.get("products_ids", [])
            if product_session_id:
                product_session_id.remove(str(kwargs["pk"]))
            request.session["products_ids"] = product_session_id

            cache_key = f"{anonymous_comparison_key}{request.session.session_key}"
            cache.delete(cache_key)

        return HttpResponseRedirect(reverse_lazy("comparison:comparison_page"))


# Переписать при помощи DRF пока так пока не готовы зависимые элементы.
class ComparisonAddView(View):
    """
    View для обработки добавления товара в список сравнения.

    Этот класс обрабатывает POST-запросы для добавления товара в
    список сравнения как для аутентифицированных, так и для
    неаутентифицированных пользователей.

    Параметры:
    ----------
        request (HttpRequest): Объект HTTP-запроса, содержащий данные о
        пользователе и продукте.
        *args: Неименованные аргументы, переданные в метод.
        **kwargs: Именованные аргументы, переданные в метод.

    Возвращает:
    ----------
        HttpResponseRedirect: Перенаправление на предыдущую страницу,
        указанную в заголовке "HTTP_REFERER", или на главную страницу ("/")
        по умолчанию.
    """

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос на добавление товара в сравнение.

        Если пользователь аутентифицирован, товар добавляется в базу данных, и
        кэш для этого пользователя очищается. Если пользователь не аутентифицирован,
        товар добавляется в сессию пользователя, и соответствующий кэш очищается.

        Параметры:
        ----------
            request (HttpRequest): Объект HTTP-запроса, содержащий информацию о запросе.
            *args: Неименованные аргументы, переданные методу.
            **kwargs: Именованные аргументы, переданные методу.

        Возвращает:
        ----------
            HttpResponseRedirect: Перенаправление на предыдущую страницу, указанную
            в заголовке "HTTP_REFERER", или на главную страницу ("/") по умолчанию.
        """
        if request.user.is_authenticated:
            product_id = request.POST.get("product")
            product = get_object_or_404(Product, pk=product_id)
            try:
                Comparison.objects.create(user=request.user, product=product)

                cache_key = f"{user_comparison_key}{request.user.id}"
                cache.delete(cache_key)

            except IntegrityError:
                pass
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
        else:
            product_id = request.POST.get("product")
            product_session_id = request.session.get("products_ids", [])

            if product_id not in product_session_id:
                product_session_id.append(product_id)

            request.session["products_ids"] = product_session_id

            cache_key = f"{anonymous_comparison_key}{request.session.session_key}"
            cache.delete(cache_key)

            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
