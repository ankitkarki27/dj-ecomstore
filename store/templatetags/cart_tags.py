from django import template
from store.models import Cart

register = template.Library()

@register.simple_tag(takes_context=True)
def cart_item_count(context):
    user = context['request'].user
    if not user.is_authenticated:
        return 0
    cart = Cart.objects.filter(user=user).first()
    if not cart:
        return 0
    return cart.items.count()
