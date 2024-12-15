from django.shortcuts import render, redirect
from django.http import JsonResponse
from store.models import Product
from .cart import Cart

def cart_summary(request):
    """Display the cart summary."""
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})

def cart_add(request):
    """Add an item to the cart."""
    product_id = request.GET.get('product_id')  # Get product ID from the request
    quantity = int(request.GET.get('quantity', 1))  # Get quantity (default to 1)
    cart = Cart(request)
    product = Product.objects.get(id=product_id)
    cart.add(product, quantity)
    return JsonResponse({'success': True, 'message': 'Item added to cart'})

def cart_delete(request):
    """Remove an item from the cart."""
    product_id = request.GET.get('product_id')  # Get product ID from the request
    cart = Cart(request)
    cart.remove(product_id)
    return JsonResponse({'success': True, 'message': 'Item removed from cart'})

def cart_update(request):
    """Update the quantity of an item in the cart."""
    product_id = request.GET.get('product_id')  # Get product ID from the request
    quantity = int(request.GET.get('quantity', 1))  # Get updated quantity
    cart = Cart(request)
    cart.update(product_id, quantity)
    return JsonResponse({'success': True, 'message': 'Cart updated'})
