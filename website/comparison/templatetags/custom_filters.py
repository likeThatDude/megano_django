from django import template
from django.db.models import QuerySet

register = template.Library()


@register.filter
def get_item(dictionary: dict, key: str) -> str:
    """
    Фильтр для получения значения из словаря по указанному ключу.

    Этот фильтр используется для извлечения значения из переданного словаря
    с помощью ключа, что позволяет работать со словарями в шаблонах Django.

    Параметры:
        dictionary (dict): Словарь, содержащий данные.
        key (str): Ключ, по которому нужно получить значение из словаря.

    Возвращает:
        Any: Значение, соответствующее указанному ключу в словаре, или None, если ключ отсутствует.
    """
    return dictionary.get(key)


@register.filter
def get_spec(specifications: QuerySet, spec_name: str) -> str:
    """
    Фильтр для поиска значения спецификации по имени в QuerySet.

    Этот фильтр итерирует по QuerySet, содержащему спецификации, и возвращает
    значение первой спецификации, имя которой совпадает с переданным.
    Если спецификация не найдена, возвращает символ "—".

    Параметры:
        specifications (QuerySet): QuerySet объектов спецификаций с атрибутами `name` и `value`.
        spec_name (str): Имя спецификации, которую нужно найти в QuerySet.

    Возвращает:
        str: Значение найденной спецификации. Если спецификация с указанным именем не найдена, возвращает "—".
    """
    for spec in specifications.all():
        if spec.name.name == spec_name:
            return spec.value
    return "—"
