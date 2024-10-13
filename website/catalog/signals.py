from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from website.settings import CATEGORY_KEY

from .models import Category


@receiver(post_save, sender=Category)
def category_post_save_handler(sender, **kwargs):
    cache.delete(CATEGORY_KEY)


@receiver(post_delete, sender=Category)
def category_post_delete_handler(sender, **kwargs):
    cache.delete(CATEGORY_KEY)
