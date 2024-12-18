from catalog.models import Category
from django import template

register = template.Library()


@register.simple_tag()
def get_categories():
    return Category.objects.filter(parent_category__isnull=True, archived=False).all()
