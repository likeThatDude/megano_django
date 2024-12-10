from http import HTTPStatus

from catalog.models import Price
from catalog.models import Product
from custom_auth.models import CustomUser
from django.http import HttpResponseNotFound
from django.template.response import TemplateResponse
from django.test import TestCase
from django.urls import reverse


class ProductDetailTestCase(TestCase):
    fixtures = ['catalog-fixtures.json']

    @classmethod
    def setUpClass(cls):
        cls.user = CustomUser.objects.create_user(username="testuser", password="testpassword",
                                                  email="test@test.com", login='test')
        for i in range(1, 10):
            cls.user = CustomUser.objects.create_user(username=f"testuser{i}", password=f"testpasswordi{i}",
                                                      email=f"test{i}@test.com", login=f'test{i}')
        super().setUpClass()
        cls.product = Product.objects.get(pk=1)
        cls.price = (Price.objects
                     .select_related('product', 'seller')
                     .filter(product_id=cls.product.id)
                     .only('product__id', 'product__name', 'seller__name', 'price')
                     )
        cls.min_price = min(cls.price, key=lambda x: x.price).price

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

    def test_get_product_detail_page(self):
        self.check_product_detail(1, HTTPStatus.OK)
        self.check_product_detail(999, HTTPStatus.NOT_FOUND)

    def test_get_product_on_page(self):
        self.check_product_on_page(1, self.product.name)
    #
    def test_check_review_create(self):
        self.check_review_on_product_page(1, False)
        response = self.client.force_login(self.user)
        self.check_review_on_product_page(1, True)
        self.client.logout()
    #
    def test_seller_on_product_page(self) -> None:
        for all_data in self.price:
            response = self.create_get_request(all_data.product.pk)
            self.assertContains(response, all_data.seller.name)
            self.assertContains(response, self.min_price)


    @classmethod
    def tearDownClass(cls):
        CustomUser.objects.all().delete()
