from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    try:
        existing = field.field.widget.attrs.get('class', '')
        combined = (existing + ' ' + css).strip()
        return field.as_widget(attrs={**field.field.widget.attrs, 'class': combined})
    except Exception:
        return field

@register.filter(name='attr')
def set_attr(field, arg):
    # arg format: "key:value,key2:value2"
    try:
        parts = [p.strip() for p in arg.split(',') if ':' in p]
        attrs = {k.strip(): v.strip() for k,v in (p.split(':',1) for p in parts)}
        return field.as_widget(attrs={**field.field.widget.attrs, **attrs})
    except Exception:
        return field
