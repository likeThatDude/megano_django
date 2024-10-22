from django.apps import AppConfig

app_name = "core"


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        from catalog import signals
