from django import template
from django.template.defaultfilters import safe

register = template.Library()

@register.filter(name='from_list')
def from_list(value):
    print("value", value.replace("'", ""))
    return value.replace("'", "")
