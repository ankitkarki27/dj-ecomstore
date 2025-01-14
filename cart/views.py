from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from store.models import Product
from .cart import Cart
from django.contrib import messages

def cart_summary(request):
    """Display the cart summary with calculated totals."""
    cart = Cart(request)
    cart_items = []
    total_amount = 0

    for item in cart:
        product = item['product']
        quantity = item['quantity']
        item_total = product.price * quantity
        total_amount += item_total

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': item_total,
        })

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
           
            cart.add(product=product)
            
           
            cart_count = cart.__len__() 
            return JsonResponse({'Product Name': product.name, 'cart_count': cart_count})
        except (ValueError, TypeError):
        
            return HttpResponseBadRequest("Invalid product ID")
    
    
    return HttpResponseBadRequest("Invalid request")



def cart_delete(request):
    """Remove an item from the cart."""
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required.'})

        cart = Cart(request)
        cart.remove(product_id)

        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart.',
            'cart_total': cart.get_total_price(),
        })
    return HttpResponseBadRequest("Invalid request method.")

def cart_update(request):
    """Update the quantity of an item in the cart."""
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        # Ensure the product ID and quantity are provided
        if not product_id or not quantity:
            return JsonResponse({'success': False, 'message': 'Product ID and quantity are required.'})

        try:
            quantity = int(quantity)  # Ensure quantity is an integer
            if quantity < 1:
                return JsonResponse({'success': False, 'message': 'Quantity must be at least 1.'})

            # Get the cart instance and update the quantity
            cart = Cart(request)
            cart.update(product_id, quantity)  # The update method in Cart class updates the quantity

            # Calculate the new total prices
            item_total = cart.get_item_total(product_id)  # Get the updated total for this item
            cart_total = cart.get_total_price()  # Get the updated total cart price

            # Return the updated information in the response
            return JsonResponse({
                'success': True,
                'message': 'Cart updated successfully.',
                'cart_total': cart_total,
                'item_total': item_total,
            })
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid quantity value.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})