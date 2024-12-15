from itertools import product
from django.shortcuts import render, redirect,get_object_or_404

from django.http import HttpResponseBadRequest, JsonResponse
from store.models import Product
from .cart import Cart

def cart_summary(request):
    """Display the cart summary."""
    cart = Cart(request)
    # return render(request, 'cart.html', {'cart': cart})
    return render(request, 'cart.html', {})

def cart_add(request):
    # Get the cart
    cart = Cart(request)
    
    # Check if the request is a POST with the correct action
    if request.method == "POST" and request.POST.get('action') == 'post':
        try:
            # Get product ID
            product_id = int(request.POST.get('product.id', 0))
            # Lookup product in the database
            product = get_object_or_404(Product, id=product_id)
            # Add the product to the cart
            cart.add(product=product)
            
            # Return the updated cart item count
            cart_count = cart.__len__()  # Get the number of items in the cart
            return JsonResponse({'Product Name': product.name, 'cart_count': cart_count})
        except (ValueError, TypeError):
            # Handle invalid product ID or missing product ID
            return HttpResponseBadRequest("Invalid product ID")
    
    # Default response for invalid or non-POST requests
    return HttpResponseBadRequest("Invalid request")
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
