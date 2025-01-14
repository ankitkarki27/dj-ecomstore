from django import templates

register = template.Library()

@register.filter
def times(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
