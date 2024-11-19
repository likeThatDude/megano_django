from catalog.models import Category
from django.core.cache import cache
from django.db.models import Count
from django.db.models import Q
from django.utils import timezone
from django.views.generic import TemplateView

from website.settings import BANNERS_KEY
from website.settings import CATEGORY_CASHING_TIME
from website.settings import CATEGORY_KEY

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

        # Загрузка категорий
        categories = cache.get(CATEGORY_KEY)
        if categories is None:
            categories = (
                Category.objects.filter(archived=False)
                .annotate(products_count=Count("products", filter=Q(products__archived=False)))
                .filter(products_count__gt=0)
            )
            cache.set(CATEGORY_KEY, categories, timeout=CATEGORY_CASHING_TIME)

        # Загрузка случайных баннеров
        random_banners = cache.get(BANNERS_KEY)
        if random_banners is None:
            random_banners = (
                Banner.objects.select_related("product")
                .filter(Q(active=True) & Q(deadline_data__gt=timezone.now().date()))
                .order_by("?")[:3]
                .only("product__name", "product__preview", "product__short_description", "text")
            )
            cache.set(BANNERS_KEY, random_banners, timeout=3600)

        context["categories"] = categories
        context["banners"] = random_banners

        return context

