from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(mapping, key):
    """Safely get a value from a dict in templates."""
    if not mapping:
        return None
    # try direct lookup, then int, then str
    try:
        return mapping.get(key)
    except Exception:
        try:
            return mapping.get(int(key))
        except Exception:
            return mapping.get(str(key))

@register.filter(name='get_range')
def get_range(value):
    """Return a range object for the given value."""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)

