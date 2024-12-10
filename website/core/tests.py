import os
from http import HTTPStatus

from catalog.models import Product, Seller
from core.models import Banner
from custom_auth.models import CustomUser
from django.test import TestCase
from django.urls import reverse


class BannersTestCase(TestCase):
    fixtures = ["custom_auth-fixtures.json", "catalog-fixtures.json", "banners-fixtures.json"]


    @classmethod
    def tearDownClass(cls):
        CustomUser.objects.all().delete()
        cls.product = Product.objects.all()
        cls.seller = Seller.objects.all()
        files_to_remove = list()
        for i in cls.product:
            files_to_remove.append(i.preview.path)
        for i in cls.seller:
            files_to_remove.append(i.image.path)

        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_get_banners_page(self):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_banner_on_page(self):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        banners = Banner.objects.select_related("product").filter(active=True)
        for number, banner in enumerate(banners):
            if number in range(0, 3):
                banners_ = response.context["banners"]
                self.assertContains(response, banner.text)
                self.assertContains(response, banner.product.name[:19])
                continue
            self.assertNotContains(response, banner.text)
            self.assertNotContains(response, banner.product.name[:19])
