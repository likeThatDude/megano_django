from django import template

register = template.Library()


@register.filter
def get_filename(value, arg):
    return str(value).split("/")[-1]
