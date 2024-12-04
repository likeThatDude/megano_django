from http import HTTPStatus

from core.models import Banner
from custom_auth.models import CustomUser
from django.test import TestCase
from django.urls import reverse


class BannersTestCase(TestCase):
    fixtures = ["catalog-fixtures.json", "banners-fixtures.json"]

    @classmethod
    def setUpClass(cls):
        (
            CustomUser.objects.create_superuser(
                username="testuser", password="testpassword", email="test@test.com", login="testuser"
            )
        )
        (
            CustomUser.objects.create_user(
                username="testuser2", password="testpassword2", email="test2@test.com", login="testuser1"
            )
        )
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        CustomUser.objects.all().delete()

    def test_get_banners_page(self):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_banner_on_page(self):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        banners = Banner.objects.select_related("product").filter(active=True)
        for number, banner in enumerate(banners):
            if number in range(0, 3):
                self.assertContains(response, banner.text)
                self.assertContains(response, banner.product.name[:19])
                continue
            self.assertNotContains(response, banner.text)
            self.assertNotContains(response, banner.product.name[:19])
