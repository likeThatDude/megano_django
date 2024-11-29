from catalog.models import Product
from comparison.models import Comparison
from comparison.serializers import AnswerAddSerializer
from comparison.serializers import ComparisonAddSerializer
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import SuspiciousOperation
from django.db import DatabaseError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from website.settings import anonymous_comparison_key
from website.settings import user_comparison_key


class ComparisonServices:

    @staticmethod
    def return_fatal_error() -> Response:
        """
        Возвращает стандартный ответ при возникновении фатальной ошибки.

        Returns:
            Response: JSON-ответ с сообщением об ошибке и статусом HTTP 500.
        """
        data = {"status": False, "title": _("Возникла ошибка"), "text": _("Не удалось добавить к сравнению")}
        serializer = AnswerAddSerializer(data=data)
        return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def __add_product_to_auth_user_comparison(user_id: int, product: Product) -> bool | None:
        """
        Добавляет товар в список сравнения для аутентифицированного пользователя.

        Args:
            user_id (int): ID пользователя.
            product (Product): Экземпляр продукта для добавления.

        Returns:
            bool | None:
                - True: Товар успешно добавлен.
                - False: Ошибка при добавлении товара.
                - None: Товар уже существует в сравнении.
        """
        try:
            comparison, created = Comparison.objects.get_or_create(user_id=user_id, product=product)
            if created:
                ComparisonServices.delete_cache(auth_flag=True, user_id=user_id)
                return True
            return None
        except DatabaseError:
            return False
        except Exception:
            return False

    @staticmethod
    def __add_product_to_unauth_user_comparison(request: HttpRequest, product_id: int) -> bool | None:
        """
        Добавляет товар в список сравнения для неаутентифицированного пользователя.

        Args:
            request (HttpRequest): Объект запроса.
            product_id (int): ID товара.

        Returns:
            bool | None:
                - True: Товар успешно добавлен.
                - False: Ошибка при добавлении товара.
                - None: Товар уже существует в сравнении.
        """
        try:
            product_session_id: list[int] = request.session.get("products_ids", [])
            if product_id not in product_session_id:
                product_session_id.append(product_id)
            else:
                return None
            request.session["products_ids"] = product_session_id
            ComparisonServices.delete_cache(request)
            return True
        except SuspiciousOperation:
            return False
        except Exception:
            return False

    @staticmethod
    def add_product_final(request: HttpRequest) -> bool | None:
        """
        Проверяет валидность данных, статус пользователя и добавляет товар в список сравнения.


        Args:
            request (HttpRequest): Запрос пользователя с данными о товаре.

        Returns:
            bool | None:
                - True: Товар успешно добавлен.
                - False: Ошибка при добавлении.
                - None: Товар уже существует.
        """
        product = ComparisonAddSerializer(data=request.data)
        if product.is_valid():
            product_data = product.validated_data["product_id"]
            if request.user.is_authenticated:
                service_answer = ComparisonServices.__add_product_to_auth_user_comparison(request.user.pk, product_data)
                return None if service_answer is None else (True if service_answer else False)
            else:
                service_answer = ComparisonServices.__add_product_to_unauth_user_comparison(request, product_data.pk)
                return None if service_answer is None else (True if service_answer else False)
        return False

    @staticmethod
    def add_product_answer(flag: bool | None) -> Response:
        """
        Формирует ответ на результат добавления товара в сравнение.

        Args:
            flag (bool | None):
                - True: Товар добавлен успешно.
                - False: Ошибка добавления.
                - None: Товар уже существует.

        Returns:
            Response: JSON-ответ с соответствующим сообщением.
        """
        if flag or flag is None:
            data = {
                "status": None if flag is None else True,
                "title": _("Конфликт") if flag is None else _("Успешно"),
                "text": _("Товар уже добавлен к сравнению") if flag is None else _("Товар добавлен к сравнению"),
            }
            serializer = AnswerAddSerializer(data=data)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            data = {"status": False, "title": _("Возникла ошибка"), "text": _("Не удалось добавить к сравнению")}
            serializer = AnswerAddSerializer(data=data)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def delete_product_final(request: HttpRequest) -> bool | None:
        """
        Проверяет валидность данных, статус пользователя и удаляет товар из списка сравнения.

        Args:
            request (HttpRequest): Запрос пользователя с данными о товаре.

        Returns:
            bool | None:
                - True: Товар успешно удалён.
                - False: Ошибка удаления.
                - None: Товар уже отсутствует.
        """
        product = ComparisonAddSerializer(data=request.data)
        if product.is_valid():
            product_data = product.validated_data["product_id"]
            if request.user.is_authenticated:
                service_answer = ComparisonServices.__delete_product_to_auth_user_comparison(
                    request.user.pk, product_data
                )
                return None if service_answer is None else (True if service_answer else False)
            else:
                service_answer = ComparisonServices.__delete_product_to_unauth_user_comparison(request, product_data.pk)
                return None if service_answer is None else (True if service_answer else False)
        return False

    @staticmethod
    def __delete_product_to_auth_user_comparison(user_id: int, product: Product) -> bool | None:
        """
        Удаляет товар из списка сравнения для аутентифицированного пользователя.

        Args:
            user_id (int): ID пользователя.
            product (Product): Экземпляр продукта для удаления.

        Returns:
            bool | None:
                - True: Товар успешно удалён.
                - False: Ошибка при удалении.
                - None: Товар не найден в сравнении.
        """
        try:
            data_from_db = Comparison.objects.only("pk").get(user_id=user_id, product=product)
            data_from_db.delete()
            ComparisonServices.delete_cache(auth_flag=True, user_id=user_id)
            return True
        except ObjectDoesNotExist:
            return None
        except DatabaseError:
            return False
        except Exception:
            return False

    @staticmethod
    def __delete_product_to_unauth_user_comparison(request: HttpRequest, product_id: int) -> bool | None:
        """
        Удаляет товар из списка сравнения для неаутентифицированного пользователя.

        Args:
            request (HttpRequest): Объект запроса.
            product_id (int): ID товара.

        Returns:
            bool | None:
                - True: Товар успешно удалён.
                - False: Ошибка при удалении.
                - None: Товар не найден в сравнении.
        """
        try:
            product_session_id: list[int] = request.session.get("products_ids", [])
            if product_id not in product_session_id:
                print("Я НЕ НАШЁЛ КЛЮЧ")
                return None
            else:
                product_session_id.remove(product_id)
            request.session["products_ids"] = product_session_id
            ComparisonServices.delete_cache(request)
            return True
        except SuspiciousOperation:
            return False
        except Exception:
            return False

    @staticmethod
    def delete_product_answer(flag: bool | None) -> Response:
        """
        Формирует ответ на результат удаления товара из сравнения.

        Args:
            flag (bool | None):
                - True: Товар успешно удалён.
                - False: Ошибка удаления.
                - None: Товар уже отсутствует.

        Returns:
            Response: JSON-ответ с соответствующим сообщением.
        """
        if flag or flag is None:
            data = {
                "status": None if flag is None else True,
                "title": _("Конфликт") if flag is None else _("Успешно"),
                "text": _("Товар уже удалён из сравнения") if flag is None else _("Товар удалён из сравнения"),
            }
            serializer = AnswerAddSerializer(data=data)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            data = {"status": False, "title": _("Возникла ошибка"), "text": _("Не удалось удалить товар из сравнения")}
            serializer = AnswerAddSerializer(data=data)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def delete_cache(request: HttpRequest | None = None, auth_flag: bool = False, user_id: int | None = None) -> None:
        """
        Удаляет кеш для сравнения товаров.

        Args:
            request (HttpRequest | None): Объект запроса для неаутентифицированных пользователей.
            auth_flag (bool): Флаг аутентификации пользователя.
            user_id (int | None): ID пользователя (только для аутентифицированных).

        Returns:
            None
        """
        if auth_flag:
            cache_key_not_unic = f"{user_comparison_key}{user_id}None"
            cache.delete(cache_key_not_unic)
            cache_key_unic = f"{user_comparison_key}{user_id}on"
            cache.delete(cache_key_unic)
        else:
            cache_key_not_unic = f"{anonymous_comparison_key}{request.session.session_key}None"
            cache.delete(cache_key_not_unic)
            cache_key_unic = f"{anonymous_comparison_key}{request.session.session_key}on"
            cache.delete(cache_key_unic)
