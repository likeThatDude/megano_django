from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import path
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import models


@admin.action(description=_("Inactive old banners"))
def archive_old_banners(model_admin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    """
    Устанавливает значение active в False для всех баннеров,
    у которых дата истечения меньше текущей даты.
    """
    # Установить active в False для всех выбранных баннеров,
    # если их deadline_data меньше текущей даты
    current_date = timezone.now().date()
    queryset.filter(deadline_data__lt=current_date).update(active=False)
    # Отправка сообщения об успешном обновлении
    model_admin.message_user(request, _("The old banners have been deactivated."))


@admin.register(models.Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("pk", "product", "deadline_data", "active")
    list_display_links = ("pk", "product", "deadline_data", "active")
    ordering = ("pk", "active")
    list_per_page = 20
    actions = [
        archive_old_banners,
    ]

