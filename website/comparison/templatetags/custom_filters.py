from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_spec(specifications, spec_name):
    for spec in specifications.all():
        if spec.name.name == spec_name:
            return spec.value
    return '—'