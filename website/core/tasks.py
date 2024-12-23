from celery import shared_task
from django.utils import timezone

from core.models import Banner
from website.celery import app


@app.task
def check_actual_banners():
    """
    Задача которая выполняется раз в день, обновляет статус баннеров у которых вышел дедлайн
    """
    current_date = timezone.now().date()
    Banner.objects.filter(deadline_data__lt=current_date).update(active=False)