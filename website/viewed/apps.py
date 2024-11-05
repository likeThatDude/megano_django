from django.apps import AppConfig


class ViewedConfig(AppConfig):
    """
    Сервис добавления в список просмотренных товаров
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "viewed"
