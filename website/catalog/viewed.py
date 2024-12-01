"""
Здесь хранится модель просмотренных пользователем товаров.
Модель хранится в сессии аналогично модели корзины.
"""

from django.db import transaction
from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone

from .models import Product


class ViewedSession:

    def __init__(self, request: HttpRequest):
        """
        Инициализация модели просмотренных неавторизованным пользователем товаров
        """
        self.session = request.session
        viewed = self.session.get(settings.VIEWED_SESSION_ID)

        if not viewed:
            viewed = self.session[settings.VIEWED_SESSION_ID] = {}

        self.viewed: dict = viewed

    def add(self, product_id: int) -> None:
        """
        Добавляет или обновляет товар в списке просмотренных неавторизованным пользователем.
        Если товар просматривается неавторизованным пользователем в первый раз,
        то увеличивается его количество просмотров.
        """

        if str(product_id) not in self.viewed:
            with transaction.atomic():
                product = Product.objects.select_for_update().get(id=product_id)
                product.views += 1
                product.save()

        self.viewed[product_id] = timezone.now().__str__()
        self.__save()

    def __save(self) -> None:
        self.session[settings.VIEWED_SESSION_ID] = self.viewed
        self.session.modified = True
