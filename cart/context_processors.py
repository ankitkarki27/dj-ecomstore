from .models import Cart, CartItem

def cart_context(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(cart__user=request.user).count()
    else:
        cart_count = sum(request.session.get('cart', {}).values())
    return {'cart_item_count': cart_count}