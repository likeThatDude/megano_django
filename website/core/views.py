import random
import datetime

from django.db.models.functions import (
    Round,
)

from catalog.models import (
    Category,
    Product,
    Price,
)
from django.core.cache import cache
from django.db.models import (
    Count,
    Min,
)
from django.db.models import Q
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

from website.settings import BANNERS_KEY
from website.settings import CATEGORY_CASHING_TIME
from website.settings import CATEGORY_KEY
from website.settings import OFFER_KEY

from .models import Banner


class IndexView(TemplateView):
    """
    View для отображения главной страницы.

    Этот класс обрабатывает GET-запросы для главной страницы, загружая категории
    товаров и случайные баннеры. Если данные закэшированы, они будут извлечены
    из кеша, иначе будет выполнен запрос к базе данных.

    Атрибуты:
        template_name (str): Путь к шаблону, который будет использован для рендеринга страницы.

    Возвращает:
        HttpResponse: Рендерит главную страницу с контекстом, содержащим категории и баннеры.
    """

    template_name = "core/main_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["banners"] = self.get_banners()
        context["favorite_categories"] = self.get_categories()
        context["top_products"] = self.get_top_products()
        context["offers"] = self.get_daily_offer_and_limited_editions()

        return context

    def get_categories(self):
        """Получает случайные 3 случайные категории из кэша или базы данных."""
        categories = cache.get(CATEGORY_KEY)
        if categories is None:
            categories = (
                Category.objects
                .filter(archived=False)
                .annotate(products_count=Count("products", filter=Q(products__archived=False)))
                .filter(products_count__gt=0)
                .order_by("?")[:3]
                .prefetch_related("products")
            )
            cache.set(CATEGORY_KEY, categories, timeout=CATEGORY_CASHING_TIME)

        favorite_categories = []

        for item in categories:
            products = item.products.filter(archived=False)
            if products.exists():
                # Находим продукт с минимальной ценой
                min_price_product = products.annotate(min_price=Min('prices__price')).order_by('min_price').first()
                if min_price_product:
                    favorite_categories.append({
                        'category': item,
                        'min_price': min_price_product.prices.first().price if min_price_product.prices.exists() else None,
                        'image': min_price_product.preview.url if min_price_product.preview else None,
                    })
        return favorite_categories

    def get_banners(self):
        """Получает 3 случайных баннеров из кэша или базы данных."""
        random_banners = cache.get(BANNERS_KEY)
        if random_banners is None:
            random_banners = (
                Banner.objects.select_related("product")
                .filter(Q(active=True) & Q(deadline_data__gt=timezone.now().date()))
                .order_by("?")[:3]
                .only("product__name", "product__preview", "text")
            )
            cache.set(BANNERS_KEY, random_banners, timeout=3)
        return random_banners

    def get_top_products(self):
        """Получает топ-товары из базы данных.(первые 8 товаров по индексу сортировки)"""
        top_products = (
            Product.objects
            .filter(archived=False)
            .annotate(
                price=Min("prices__price")
            )
            .order_by("?")[:8]
        )
        return top_products

    def get_daily_offer_and_limited_editions(self):
        """Получает случайный товар с ограниченным тиражом для блока 'Предложение дня'
         и оставшиеся 15 предложений для слайдера Ограниченый тираж
         """
        offers = cache.get(OFFER_KEY)
        if offers is None:
            limited_edition_products = (
                Price.objects
                .select_related('product')
                .filter(product__limited_edition=True)
            )
            if limited_edition_products.exists():
                daily_offer = limited_edition_products.order_by("?").first()
                last_limited_editions_products = limited_edition_products.exclude(id=daily_offer.id)[:16]
                today = datetime.datetime.now() + datetime.timedelta(days=2)
                today_formatted = today.strftime("%d.%m.%Y %H:%M")
                offers = {
                    "daily_offer": daily_offer,
                    "last_limited_editions_products": last_limited_editions_products,
                    "today": today_formatted,
                }
            cache.set(OFFER_KEY, offers, timeout=10)
        return offers

