from django.core.files.storage import default_storage
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from website import settings
from website.s3_storage import OptimizationStorage
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

@receiver(pre_delete, sender=Profile)
def delete_photo_on_delete(sender, instance, **kwargs):
    """
    Удаляем фото из хранилища при удалении профиля
    """
    if instance.photo:
        if default_storage.exists(instance.photo.name):
            default_storage.delete(instance.photo.name)


@receiver(pre_save, sender=Profile)
def delete_old_photo_on_update(sender, instance, **kwargs):
    """
    Удаляем старое фото при обновлении или удалении аватарки
    """
    if instance.pk:
        old_instance = Profile.objects.get(pk=instance.pk)
        if old_instance.photo != instance.photo:
            if old_instance.photo:
                if settings.USE_S3:
                    storage = OptimizationStorage()
                    if storage.exists(old_instance.photo.name):
                        storage.delete(old_instance.photo.name)
                else:
                    if default_storage.exists(old_instance.photo.name):
                        default_storage.delete(old_instance.photo.name)
