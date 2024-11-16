from django.apps import AppConfig


class DiscountConfig(AppConfig):
    """
    Сервис просмотра и редактирования скидок
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "discount"
