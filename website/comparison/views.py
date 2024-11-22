from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from django.http import HttpRequest

from django.views.generic import TemplateView

from . import utils
from .srevices import ComparisonServices
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
        unic_spec = self.request.GET.get("unic_spec")
        if user.is_authenticated:
            comparison_products = utils.get_products_with_auth_user(user.pk, unic_spec)
            data = create_categorization(comparison_products[1])

        else:
            comparison_products = utils.get_products_with_unauth_user(self.request, unic_spec)
            data = create_categorization(comparison_products[1], False)
        context["comparison_products"] = data
        context["correct_spec"] = comparison_products[0]
        context["unic_spec"] = True if unic_spec else False
        return context


class ComparisonDeleteApiView(APIView):
    """
    API View для удаления товара из списка сравнения.

    Этот класс обрабатывает DELETE-запросы и вызывает сервисный метод
    для удаления товара из списка сравнения. Доступ к методу разрешен всем
    пользователям, включая неаутентифицированных.

    Атрибуты:
        permission_classes (tuple): Указывает, что доступ разрешен любому пользователю (AllowAny).

    Методы:
        delete(request, *args, **kwargs):
            Обрабатывает DELETE-запрос для удаления товара из списка сравнения.

    Параметры метода delete:
        request (HttpRequest): Объект HTTP-запроса.
        *args: Дополнительные позиционные аргументы.
        **kwargs: Дополнительные именованные аргументы.

    Возвращает:
        Response: HTTP-ответ с результатом операции:
            - Успешный результат удаления.
            - Сообщение об ошибке, если удаление завершилось неудачно.
            - Сообщение о фатальной ошибке в случае исключения.
    """
    permission_classes = (AllowAny,)

    def delete(self, request: HttpRequest, *args, **kwargs):
        try:
            service_answer = ComparisonServices.delete_product_final(request)
            return ComparisonServices.delete_product_answer(service_answer)
        except Exception:
            return ComparisonServices.return_fatal_error()


class ComparisonAddApiView(APIView):
    """
    API View для добавления товара в список сравнения.

    Этот класс обрабатывает POST-запросы и вызывает сервисный метод
    для добавления товара в список сравнения. Доступ к методу разрешен всем
    пользователям, включая неаутентифицированных.

    Атрибуты:
        permission_classes (tuple): Указывает, что доступ разрешен любому пользователю (AllowAny).

    Методы:
        post(request, *args, **kwargs):
            Обрабатывает POST-запрос для добавления товара в список сравнения.

    Параметры метода post:
        request (HttpRequest): Объект HTTP-запроса.
        *args: Дополнительные позиционные аргументы.
        **kwargs: Дополнительные именованные аргументы.

    Возвращает:
        Response: HTTP-ответ с результатом операции:
            - Успешный результат добавления.
            - Сообщение об ошибке, если добавление завершилось неудачно.
            - Сообщение о фатальной ошибке в случае исключения.
    """
    permission_classes = (AllowAny,)

    def post(self, request: HttpRequest, *args, **kwargs):
        try:
            service_answer = ComparisonServices.add_product_final(request)
            return ComparisonServices.add_product_answer(service_answer)
        except Exception:
            return ComparisonServices.return_fatal_error()
