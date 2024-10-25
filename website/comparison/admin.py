from django.contrib import admin

from comparison.models import Comparison


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'product', )
    list_display_links = ('pk', 'user', 'product', )
    ordering = ('user', 'pk', )