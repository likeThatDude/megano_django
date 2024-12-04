from http import HTTPStatus
from random import choices
from string import ascii_letters

from catalog.models import Category
from catalog.models import Delivery
from catalog.models import Payment
from catalog.models import Price
from catalog.models import Product
from catalog.models import Seller
from custom_auth.models import CustomUser
from django.core.files.base import ContentFile
from django.http import HttpResponseNotFound
from django.template.response import TemplateResponse
from django.test import TestCase
from django.urls import reverse


class ProductDetailTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        CustomUser.objects.all().delete()
        Category.objects.all().delete()
        Product.objects.all().delete()
        cls.user = CustomUser.objects.create_user(username="testuser", password="testpassword", email="test@test.com")
        cls.icon_content = ContentFile(b"dummy content", name="test_icon.png")
        cls.product_name = "".join(choices(ascii_letters, k=10))
        cls.category_name = "".join(choices(ascii_letters, k=10))
        cls.seller_name = "".join(choices(ascii_letters, k=10))
        cls.category = Category.objects.create(name=cls.category_name)
        cls.product = Product.objects.create(
            name=cls.product_name,
            product_type="Смартфон",
            manufacture="Китай",
            category=cls.category,
            preview=cls.icon_content,
        )
        cls.delivery = Delivery.objects.create(name=Delivery.PICKUP_POINT)
        cls.payment = Payment.objects.create(name=Payment.CARD_COURIER)
        cls.seller = Seller.objects.create(
            name=cls.seller_name,
            phone="9809379992",
            email="seller@seller.com",
            image=cls.icon_content,
        )
        cls.seller.delivery_methods.set([cls.delivery])
        cls.seller.payment_methods.set([cls.payment])
        cls.price = Price.objects.create(
            seller=cls.seller, product=cls.product, quantity=1, sold_quantity=12, price=2500
        )

    def create_get_request(self, pk: int) -> TemplateResponse | HttpResponseNotFound:
        response = self.client.get(reverse("catalog:product_detail", kwargs={"pk": pk}))
        return response

    def check_product_detail(self, pk: int, expected_status: HTTPStatus) -> None:
        response = self.create_get_request(pk)
        self.assertEqual(response.status_code, expected_status)

    def check_product_on_page(self, pk: int, product_name: str) -> None:
        response = self.create_get_request(pk)
        self.assertContains(response, product_name)

    def check_review_on_product_page(self, pk: int, login: bool) -> None:
        response = self.create_get_request(pk)
        login_link = reverse("custom_auth:login")
        if login:
            self.assertContains(response, "Отправить отзыв")
        else:
            self.assertContains(response, login_link)
            self.assertNotContains(response, "Отправить отзыв")

    def check_login(self, login: bool) -> None:
        response = self.client.get(reverse("custom_auth:login"))
        if login:
            self.assertRedirects(response, reverse("core:index"))
        else:
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.client.logout()

    def test_get_product_detail_page(self):
        self.check_product_detail(1, HTTPStatus.OK)
        self.check_product_detail(2, HTTPStatus.NOT_FOUND)

    def test_get_product_on_page(self):
        self.check_product_on_page(1, self.product.name)

    def test_check_review_create(self):
        self.check_login(False)
        self.check_review_on_product_page(1, False)
        response = self.client.login(email="test@test.com", password="testpassword")
        self.check_login(True)
        self.check_review_on_product_page(1, True)

    def test_seller_on_product_page(self) -> None:
        response = self.create_get_request(1)
        self.assertContains(response, self.seller_name)
        self.assertContains(response, self.price.price)

    @classmethod
    def tearDownClass(cls):
        cls.seller.delete()
        cls.payment.delete()
        cls.delivery.delete()
        cls.product.delete()
        cls.category.delete()
        cls.user.delete()
