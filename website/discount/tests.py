from django.test import TestCase
from django.utils.timezone import datetime, timedelta
from django.contrib.auth import get_user_model

from typing import Any, Dict

from catalog.models import Category, Product
from .forms import DiscountCreationForm
from .models import Discount


class TestDiscount(TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Создаем суперпользователя и обычного пользователя

        """
        super().setUpClass()

        User = get_user_model()
        cls.superuser = User.objects.create_superuser(
            email="admin@mail.com",
            password="adminpassword"
        )
        cls.user = User.objects.create_user(
            login="mynickname",
            email="user@mail.com",
            password="userpassword"
        )
        cls.category = Category.objects.create(name="Test Category")
        cls.product1 = Product.objects.create(
            name="Test Product 1",
            category=cls.category
        )
        cls.product2 = Product.objects.create(
            name="Test Product 2",
            category=cls.category
        )

    def test_discount_creation_success(self):
        """
        Тест на успешное создание инстанса модели Discount
        Модель Discount определена в приложении /discount/models.py

        Атрибуты:
            name - название скидки
            kind - тип скидки
            method - принцип действия скидки
            priority - приоритет скидки
            percent - процент скидки (если выбрали тип скидки Discount Percentage)
            end_date - дата окончания действия скидки

        """
        data: Dict[str, Any] = {
            "name": "Скидки на Новый Год!",
            "kind": "PT",
            "method": "PT",
            "priority": 3,
            "percent": 5,
            "end_date": datetime(
                year=2024,
                month=12,
                day=31,
                hour=23,
                minute=59,
                second=59
            ),
        }
        self.discount: Discount = Discount.objects.create(**data)
        self.assertTrue(
            Discount.objects.filter(pk=self.discount.pk).exists(),
            "Инстанс модели Discount был успешно создан!"
        )

    def test_discount_creation_form_success(self):
        """
        Тест на успешное создание инстанса модели Discount
        с использованием формы DiscountCreationForm

        Атрибуты:
            name - название скидки
            kind - вид скидки
            method - метод скидки
            value - значение скидки
            priority - приоритет скидки
            percent - процент скидки (если method - процент)
            is_active - активна ли скидка
            archived - архивирована ли скидка
            start_date - дата начала действия скидки
            end_date - дата окончания действия скидки

        """
        data: Dict[str, Any] = {
            "name": "Скидки на Новый Год!",
            "kind": Discount.PRODUCT,
            "method": Discount.PERCENT,
            "value": 5,
            "priority": 3,
            "percent": 5,
            "is_active": True,
            "archived": False,
            "start_date": datetime.now(),
            "end_date": datetime(
                year=2024,
                month=12,
                day=31,
                hour=23,
                minute=59,
                second=59
            ),
        }
        form = DiscountCreationForm(data=data)
        self.assertTrue(
            form.is_valid(),
            "Успешно создали инстанс модели Discount с помощью формы DiscountCreationForm"
        )

    def test_discount_creation_form_fail(self):
        """
        Тест на неуспешное создание инстанса модели Discount
        с использованием формы DiscountCreationForm

        Атрибуты:
            name - название скидки
            kind - вид скидки
            method - метод скидки
            start_date - дата начала действия скидки
            end_date - дата окончания действия скидки

        """
        data = {
            "name": "",
            "kind": "Invalid kind",
            "method": "Invalid method",
            "start_date": datetime.now(),
            "end_date": datetime.now() - timedelta(days=1),
        }
        form = DiscountCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("kind", form.errors)
        self.assertIn("method", form.errors)
        self.assertIn("end_date", form.errors)
