from django import template

register = template.Library()


@register.filter
def get_item(iterable, index):
    try:
        # Subtract 1 because current_step starts at 1 but index at 0
        return iterable[int(index) - 1]['name']
    except (IndexError, TypeError, ValueError, KeyError):
        return ""


@register.filter
def mul(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0
