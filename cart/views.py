from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from store.models import Product
from .models import Cart, CartItem

@login_required
def cart_summary(request):
    """Display the cart summary with calculated totals."""
    if request.user.is_authenticated:
        # For logged-in users: use database cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()  # Get all related CartItem objects
    else:
        # For guests: use session cart
        session_cart = request.session.get('cart', {})
        product_ids = session_cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart_items = []
        for product in products:
            cart_items.append({
                'product': product,
                'quantity': session_cart[str(product.id)],
                'total': product.price * session_cart[str(product.id)]
            })

    total_amount = sum(
        item.product.price * item.quantity if hasattr(item, 'product') 
        else item['product'].price * item['quantity'] 
        for item in cart_items
    )

    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
    }
    return render(request, 'cart/cart.html', context)

def cart_add(request):
    if request.method == "POST":
        product_id = request.POST.get('product.id')
        if not product_id:
            return JsonResponse({'error': 'Product ID missing'}, status=400)
        
        try:
            product = Product.objects.get(id=product_id)
            response_data = {
                'success': True,
                'product_name': product.name,
                'product_id': product.id
            }

            if request.user.is_authenticated:
                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': 1}
                )
                if not created:
                    cart_item.quantity += 1
                    cart_item.save()
                response_data['cart_count'] = cart.items.count()
            else:
                cart = request.session.get('cart', {})
                cart_key = str(product.id)
                cart[cart_key] = cart.get(cart_key, 0) + 1
                request.session['cart'] = cart
                request.session.modified = True
                response_data['cart_count'] = sum(cart.values())

            return JsonResponse(response_data)

        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def cart_delete(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID required'})
        
        try:
            cart_item = CartItem.objects.get(
                cart__user=request.user,
                product_id=product_id
            )
            cart_item.delete()
            
            cart = Cart.objects.get(user=request.user)
            return JsonResponse({
                'success': True,
                'cart_total': sum(item.product.price * item.quantity for item in cart.items.all())
            })
            
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not in cart'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def cart_update(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        
        if not product_id or not quantity:
            return JsonResponse({'success': False, 'message': 'Missing parameters'})
        
        try:
            quantity = int(quantity)
            if quantity < 1:
                return JsonResponse({'success': False, 'message': 'Invalid quantity'})
            
            cart_item = CartItem.objects.get(
                cart__user=request.user,
                product_id=product_id
            )
            cart_item.quantity = quantity
            cart_item.save()
            
            cart = Cart.objects.get(user=request.user)
            item_total = cart_item.product.price * quantity
            cart_total = sum(item.product.price * item.quantity for item in cart.items.all())
            
            return JsonResponse({
                'success': True,
                'item_total': item_total,
                'cart_total': cart_total
            })
            
        except (ValueError, CartItem.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Invalid request'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)