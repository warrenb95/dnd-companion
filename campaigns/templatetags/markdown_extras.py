import markdown as md

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def markdown(value):
    return mark_safe(md.markdown(value, extensions=["extra"]))


@register.filter
def split(value, separator):
    """Split a string by separator and return a list."""
    if not value:
        return []
    return value.split(separator)
