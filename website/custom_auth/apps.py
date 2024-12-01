from django.apps import AppConfig


class CustomAuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "custom_auth"

    def ready(self):
        """Для работы сигналов"""
        import custom_auth.signals
