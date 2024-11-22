import datetime

from catalog.models import (
    Category,
    Product,
    Price,
)
from django.core.cache import cache
from django.db.models import (
    Count,
    Min,
    Sum,
    OuterRef,
    Subquery,
)
from django.db.models import Q
from django.utils import timezone
from django.views.generic import TemplateView

from website.settings import BANNERS_KEY
from website.settings import CATEGORY_CASHING_TIME
from website.settings import CATEGORY_KEY
from website.settings import OFFER_KEY
from website.settings import HOT_OFFER_KEY

from .models import Banner
from discount.utils import get_discounted_products


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
        context["hot_offers"] = self.get_hot_offers()

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
                .only("product__name", "product__preview", "product__short_description", "text")
            )
            cache.set(BANNERS_KEY, random_banners, timeout=CATEGORY_CASHING_TIME)
        return random_banners

    def get_top_products(self):
        """Получает топ-товары из базы данных.(первые 8 товаров по индексу сортировки)"""
        price_subquery = Price.objects.filter(product=OuterRef("pk")).values("pk")
        top_products = (
            Product.objects
            .filter(archived=False)
            .annotate(
                price=Min("prices__price"),
                total_sold=Sum('prices__sold_quantity'),
                price_pk=Subquery(price_subquery),
            )
            .order_by('sorting_index', '-total_sold')[:8]
        )
        return top_products

    def get_daily_offer_and_limited_editions(self):
        """Получает случайный товар с ограниченным тиражом для блока 'Предложение дня'
         и оставшиеся 15 предложений для слайдера Ограниченный тираж
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
                daily_offer_product = daily_offer.product
                daily_offer_product_with_new_price = daily_offer_product.prices.order_by("price").first()
                daily_offer_new_price = daily_offer_product_with_new_price.price

                last_limited_editions_products = limited_edition_products.exclude(id=daily_offer.id)[:16]
                today = datetime.datetime.now() + datetime.timedelta(days=2)
                today_formatted = today.strftime("%d.%m.%Y %H:%M")
                offers = {
                    "daily_offer": daily_offer,
                    "daily_offer_new_price": daily_offer_new_price,
                    "last_limited_editions_products": last_limited_editions_products,
                    "today": today_formatted,
                }
            cache.set(OFFER_KEY, offers, timeout=CATEGORY_CASHING_TIME)

        print(offers["daily_offer"])
        return offers

    def get_hot_offers(self):
        """ В слайдер с горячими предложениями попадает до девяти случайных товаров,
        на которые действует какая-нибудь акция"""
        hot_offers = cache.get(HOT_OFFER_KEY)
        if hot_offers is None:
            hot_offers = get_discounted_products(8)
            print(hot_offers)
        cache.set(HOT_OFFER_KEY, hot_offers, timeout=CATEGORY_CASHING_TIME)
        return hot_offers
