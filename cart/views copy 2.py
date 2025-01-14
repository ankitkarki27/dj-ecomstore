from itertools import product
from django.shortcuts import render, redirect,get_object_or_404

from django.http import HttpResponseBadRequest, JsonResponse
from store.models import Product
from .cart import Cart
from django.contrib import messages

# def cart_summary(request):
#     """Display the cart summary."""
#     cart = Cart(request)  # Get the cart from the session
#     return render(request, 'cart/cart.html', {'cart': cart})
def cart_summary(request):
    """Display the cart summary with calculated totals."""
    cart = Cart(request)  # Get the cart from the session

    # Prepare the cart items with total for each
    cart_items = []
    total_amount = 0

    for item in cart:
        product = item['product']  # Access the product object
        quantity = item['quantity']  # Quantity of the product
        item_total = product.price * quantity  # Calculate total for the item
        total_amount += item_total  # Add to the overall total amount
        
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': item_total,  # Include the item total for the template
        })

    # Pass the updated cart items and total amount to the template
    context = {
        'cart': cart_items,
        'total_amount': total_amount,
    }
    return render(request, 'cart/cart.html', context)

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

from django.http import JsonResponse
from .cart import Cart


def cart_delete(request):
    """Remove an item from the cart."""
    product_id = request.GET.get('product_id')  # Get product ID from the request
    cart = Cart(request)
    
    # Check if product exists in the cart
    if product_id:
        cart.remove(product_id)  # Remove the item from the cart
        
        # Calculate the new total
        cart_total = cart.get_total_price()  # This method should return the total price of all items in the cart
        
        # Return the updated total amount and a success message
        return JsonResponse({'success': True, 'message': 'Item removed from cart', 'cart_total': cart_total})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid product ID'})
    
def cart_update(request):
    """Update the quantity of an item in the cart."""
    product_id = request.GET.get('product_id')  # Get product ID from the request
    quantity = int(request.GET.get('quantity', 1))  # Get updated quantity
    cart = Cart(request)
    cart.update(product_id, quantity)
    return JsonResponse({'success': True, 'message': 'Cart updated'})


def get_total_price(self):
        """Calculate the total price of all items in the cart."""
        total = 0
        for item in self.cart.values():
            total += item['price'] * item['quantity']
        return total

from .models import CartItem  # Adjust based on your model

# In your views.py

from django.http import JsonResponse
from .models import CartItem  # Adjust based on your model

def update_quantity(request):
    if request.method == "GET":
        product_id = request.GET.get("product_id")
        quantity = int(request.GET.get("quantity"))

        try:
            # Get the cart item and update the quantity
            cart_item = CartItem.objects.get(product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()

            # Recalculate the total
            total_amount = sum(item.product.price * item.quantity for item in CartItem.objects.all())

            return JsonResponse({"success": True, "cart_total": total_amount})

        except CartItem.DoesNotExist:
            return JsonResponse({"success": False, "message": "Item not found"})
    return JsonResponse({"success": False})
