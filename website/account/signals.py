from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser
from .models import Profile


@receiver(post_save, sender=CustomUser)
def create_superuser_profile(sender, instance, created, **kwargs):
    """
    Сигнал для создания профиля только для суперпользователей.
    """
    if created and instance.is_superuser:
        # Создаем профиль только для суперпользователя
        Profile.objects.create(user=instance)
