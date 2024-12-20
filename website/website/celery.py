import os

from celery.schedules import crontab
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

app = Celery("website")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send_three_random_discount_category_friday": {
        "task": "discount.tasks.send_three_random_discount_category_friday",
        "schedule": crontab(minute="0", hour="14", day_of_week="5"),
    },
    "send_new_year_message": {
        "task": "custom_auth.tasks.send_new_year_message",
        "schedule": crontab(minute="0", hour="0", day_of_month="25-31", month_of_year="12"),
    },
    "send_user_happy_birthday": {
        "task": "custom_auth.tasks.send_user_happy_birthday",
        "schedule": crontab(minute="0", hour="0"),
    }
}
