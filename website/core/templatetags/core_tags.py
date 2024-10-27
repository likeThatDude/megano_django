from django import template

from catalog.models import Category

register = template.Library()


@register.simple_tag()
def get_categories():
    return Category.objects.filter(parent_category__isnull=True).all()
