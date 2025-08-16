from itertools import product
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product, Cart, CartItem, Customer
from .models import Order, Payment, OrderItem
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, CustomerProfileForm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# Recommendation System
# =========================
_product_tfidf_matrix = None
_product_tfidf_vectorizer = None
_all_products = None

def _initialize_recommendation_system():
    global _product_tfidf_matrix, _product_tfidf_vectorizer, _all_products
    _all_products = list(Product.objects.select_related('category').all())
    if not _all_products:
        return
    text_data = []
    for p in _all_products:
        cat = p.category.name if p.category else ''
        desc = p.description if p.description else ''
        price = str(p.price) if p.price else '0'
        text_data.append(f"{cat} {desc} {price}")
    _product_tfidf_vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
    _product_tfidf_matrix = _product_tfidf_vectorizer.fit_transform(text_data)

def get_similar_products(product, num_recommendations=5):
    global _product_tfidf_matrix, _product_tfidf_vectorizer, _all_products
    if _product_tfidf_matrix is None:
        _initialize_recommendation_system()
    if not _all_products or not product.id:
        return []

    try:
        # Only consider products of the same gender or unisex
        filtered_products = [p for p in _all_products if (p.gender == product.gender or p.gender == 'Unisex') and p.id != product.id]
        # Always include the current product for index reference
        filtered_products = [product] + filtered_products
        text_data = []
        for p in filtered_products:
            category_weight = 3 if p.category == product.category else 1
            category_text = (p.category.name + " ") * category_weight if p.category else ""
            specs = f" {p.name} "
            text_data.append(f"{category_text}{specs}{p.description if p.description else ''}")

        _product_tfidf_vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b\w+\b|\b\d+[A-Za-z]+\b',
            stop_words='english'
        )
        _product_tfidf_matrix = _product_tfidf_vectorizer.fit_transform(text_data)
        product_index = 0
    except Exception as e:
        print(f"Recommendation error: {e}")
        return []

    from sklearn.metrics.pairwise import cosine_similarity as _cs
    cosine_similarities = _cs(
        _product_tfidf_matrix[product_index:product_index+1],
        _product_tfidf_matrix
    ).flatten()

    similar_indices = cosine_similarities.argsort()[::-1][1:num_recommendations+1]
    return [
        (filtered_products[i], float(cosine_similarities[i]))
        for i in similar_indices if cosine_similarities[i] > 0.1
    ]
def home(request):
    products = Product.objects.all()
    featured_products = Product.objects.filter(is_sale=True)[:4]
    new_products = [p for p in products if p.is_new][:4]
    return render(request, 'home.html', {
        'products': products,
        'featured_products': featured_products,
        'new_products': new_products
    })

from django.db.models import Q
def search_products(request):
    query = request.GET.get('q','').strip()
    results = []
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(brand__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query)
        ).select_related('category')[:100]
    return render(request, 'search_results.html', { 'query': query, 'results': results })

def category_page(request, foo):
    category_name = foo.replace('-', ' ')
    try:
        category = get_object_or_404(Category, name__iexact=category_name)
        products = Product.objects.filter(category=category)
        gender_filter = request.GET.get('gender')  # ?gender=men
        if gender_filter in ['men', 'women']:
            products = products.filter(gender=gender_filter)
        return render(request, 'category.html', {
            'products': products,
            'category': category
        })
    except Category.DoesNotExist:
        messages.error(request, "The category you are looking for does not exist.")
        return redirect('store:home')

def product_page(request, pk):
    product = get_object_or_404(Product, id=pk)
    manual_related = list(product.related_products.all()[:8]) if hasattr(product, 'related_products') else []
    similar_products_with_percent = []
    if manual_related:
        # Manual relations get 100% badge visually (or skip percentage logic later)
        similar_products_with_percent = [(p, 1.0, 100) for p in manual_related]
    else:
        # Algorithmic recommendation
        similar_products = get_similar_products(product, num_recommendations=8)
        if not similar_products:
            similar_products_qs = Product.objects.filter(
                category=product.category
            ).exclude(id=product.id).order_by('?')[:8]
            similar_products = [(p, 0.0) for p in similar_products_qs]
        similar_products_with_percent = [
            (p, s, int(round(s * 100))) for p, s in similar_products if s > 0
        ]
        # If still empty (all zero), fallback to random but hide percent by using -1
        if not similar_products_with_percent:
            random_fallback = Product.objects.filter(category=product.category).exclude(id=product.id).order_by('?')[:4]
            similar_products_with_percent = [(p, 0.0, -1) for p in random_fallback]
    return render(request, 'product.html', { 'product': product, 'similar_products': similar_products_with_percent })

# =========================
# Auth Views
# =========================
def login_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
        if user:
            login(request, user)
            messages.success(request, "You have been logged in")
            return redirect('store:home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('store:login')
    return render(request, 'login.html')

def logout_page(request):
    is_staff = request.user.is_authenticated and request.user.is_staff
    logout(request)
    messages.success(request, "You have been logged out")
    if is_staff:
        from django.urls import reverse
        return redirect('store:admin_login')
    return redirect('store:home')

def register_page(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create or update customer record with phone
            from .models import Customer
            phone = getattr(form, 'phone', '')
            Customer.objects.update_or_create(
                email=user.email,
                defaults={
                    'first_name': user.first_name or user.username,
                    'last_name': user.last_name or '',
                    'phone': phone,
                    'password': ''
                }
            )
            login(request, user)
            messages.success(request, "You are registered successfully")
            return redirect('store:home')
        messages.error(request, "Invalid registration. Please fix the errors below.")
    return render(request, 'register.html', {'form': form})

# =========================
# Cart Views
# =========================
def cart_page(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view your cart.")
        return redirect('store:login')

    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'cart.html', {'cart': cart, 'items': items, 'total': total})

def add_to_cart(request, product_id):
    from django.http import JsonResponse
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if request.method != 'POST':
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
        return redirect('store:home')

    if not request.user.is_authenticated:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'You must be logged in to add items to the cart.'}, status=403)
        # messages.error(request, "You must be logged in to add items to the cart.")
        return redirect('store:login')

    try:
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        import json
        qty = 1
        if is_ajax:
            try:
                raw = (request.body or b'').decode('utf-8')
                body = json.loads(raw) if raw else {}
                q_candidate = body.get('quantity') or body.get('qty')
                if q_candidate is not None:
                    qty = int(q_candidate)
            except Exception:
                qty = 1
        if qty < 1:
            qty = 1
        cart_item, created_ci = CartItem.objects.get_or_create(cart=cart, product=product)
        if created_ci:
            cart_item.quantity = qty
        else:
            cart_item.quantity += qty
        cart_item.save()
        if is_ajax:
            return JsonResponse({'success': True, 'product_name': product.name, 'cart_count': cart.items.count(), 'auth': True})
        messages.success(request, f"{product.name} added to cart")
        return redirect('store:product_page', pk=product_id)
    except Exception as e:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'An error occurred.', 'auth': request.user.is_authenticated}, status=500)
        messages.error(request, "An error occurred while adding to cart.")
        return redirect('store:product_page', pk=product_id)

def remove_from_cart(request, item_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to remove items from the cart.")
        return redirect('store:login')

    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart")
    return redirect('store:cart')

def update_cart_item(request, item_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to update cart items.")
        return redirect('store:login')

    if request.method == "POST":
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            item.quantity = quantity
            item.save()
            messages.success(request, "Cart updated successfully")
        else:
            item.delete()
            messages.success(request, "Item removed from cart")
    return redirect('store:cart')

from .models import Order, Payment

# =========================
# Order / Checkout Views
# =========================

def checkout(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to checkout.")
        return redirect('store:login')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    total = sum(item.product.price * item.quantity for item in items)

    def _get_or_create_customer(user):
        email = user.email or f"{user.username}@example.com"
        customer = Customer.objects.filter(email=email).first()
        if not customer:
            customer = Customer.objects.create(
                first_name=user.first_name or user.username,
                last_name=user.last_name or '',
                phone='',
                email=email,
                password=''
            )
        return customer

    if request.method == 'POST':
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        payment_method = request.POST.get('payment_method', 'cash')
        customer_obj = _get_or_create_customer(request.user)

        if not items:
            messages.error(request, "Your cart is empty.")
            return redirect('store:cart')

        order = Order.objects.create(
            customer=customer_obj,
            address=address,
            phone=phone,
            status=False,
            total_amount=0
        )
        running_total = 0
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            if item.product.stock >= item.quantity:
                item.product.stock -= item.quantity
                item.product.save(update_fields=['stock'])
            running_total += item.product.price * item.quantity
        order.total_amount = running_total
        order.save(update_fields=['total_amount'])
        Payment.objects.create(
            order=order,
            method=payment_method,
            amount=running_total,
            status='pending'
        )
        cart.items.all().delete()
        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('store:order_detail', order_id=order.id)

    return render(request, 'checkout.html', {'cart': cart, 'items': items, 'total': total})

def order_history(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view your orders.")
        return redirect('store:login')

    # Get or create a mapped Customer record
    email = request.user.email or f"{request.user.username}@example.com"
    customer_obj = Customer.objects.filter(email=email).first()
    if not customer_obj:
        customer_obj = Customer.objects.create(
            first_name=request.user.first_name or request.user.username,
            last_name=request.user.last_name or '',
            phone='',
            email=email,
            password=''
        )
    orders = Order.objects.filter(customer=customer_obj).order_by('-date')
    # Legacy backfill: create OrderItem if older order has product but no items
    for o in orders:
        if o.product_id and not o.items.exists():
            OrderItem.objects.create(order=o, product=o.product, quantity=o.quantity or 1, price=o.product.price)
            # set total_amount if zero
            if not o.total_amount:
                o.total_amount = o.product.price * (o.quantity or 1)
                o.save(update_fields=['total_amount'])
    return render(request, 'order_history.html', {'orders': orders})

def order_detail(request, order_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view this order.")
        return redirect('store:login')
    email = request.user.email or f"{request.user.username}@example.com"
    customer_obj = Customer.objects.filter(email=email).first()
    order = get_object_or_404(Order, id=order_id, customer=customer_obj)
    if order.product_id and not order.items.exists():
        OrderItem.objects.create(order=order, product=order.product, quantity=order.quantity or 1, price=order.product.price)
        if not order.total_amount:
            order.total_amount = order.product.price * (order.quantity or 1)
            order.save(update_fields=['total_amount'])
    return render(request, 'order_detail.html', {'order': order})

# =========================
# Profile View
# =========================
def profile(request):
    """Display profile information for the logged-in user.

    Shows basic auth user data, an attached Customer record if present, recent orders,
    and simple cart statistics. Gracefully handles absence of a related Customer object.
    """
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view your profile.")
        return redirect('store:login')

    user = request.user

    # Attempt to get related Customer (if a OneToOne/ForeignKey relation exists under 'customer')
    # Map to existing or newly created Customer record
    email = user.email or f"{user.username}@example.com"
    customer_obj = Customer.objects.filter(email=email).first()
    if not customer_obj:
        customer_obj = Customer.objects.create(
            first_name=user.first_name or user.username,
            last_name=user.last_name or '',
            phone='',
            email=email,
            password=''
        )

    # Recent orders (limit 5) if customer relation present
    recent_orders = []
    if customer_obj:
        recent_orders = Order.objects.filter(customer=customer_obj).order_by('-date')[:5]

    # Cart statistics
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_items = cart.items.select_related('product')
    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    cart_count = cart_items.count()

    form = CustomerProfileForm(data=request.POST or None, user=user, customer=customer_obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('store:profile')
    context = {
        'user_obj': user,
        'customer_obj': customer_obj,
        'recent_orders': recent_orders,
        'cart_total': cart_total,
        'cart_count': cart_count,
        'profile_form': form,
    }
    return render(request, 'profile.html', context)

# =========================
# Simple Custom Admin (lightweight, not Django admin)
# =========================
from django.contrib.admin.views.decorators import staff_member_required

def _admin_stats():
    completed_orders = Order.objects.filter(status=True, canceled=False)
    income = sum(o.total_amount for o in completed_orders)
    return {
        'product_count': Product.objects.count(),
        'order_count': Order.objects.count(),
        'pending_orders': Order.objects.filter(status=False, canceled=False).count(),
        'canceled_orders': Order.objects.filter(canceled=True).count(),
        'customer_count': Customer.objects.count(),
        'income': income,
    }

@staff_member_required(login_url='/adminpanel/login/')
def admin_dashboard(request):
    stats = _admin_stats()
    latest_orders = Order.objects.order_by('-date')[:5]
    return render(request, 'admin/dashboard.html', { 'stats': stats, 'latest_orders': latest_orders })

@staff_member_required(login_url='/adminpanel/login/')
def admin_products(request):
    products = Product.objects.select_related('category').order_by('-id')
    return render(request, 'admin/view_products.html', { 'products': products })

@staff_member_required(login_url='/adminpanel/login/')
def admin_add_product(request):
    from django import forms
    class _ProductForm(forms.ModelForm):
        class Meta:
            model = Product
            fields = ['name','category','gender','brand','price','stock','description','image','is_new','is_sale','related_products']
    if request.method == 'POST':
        form = _ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added')
            return redirect('store:admin_products')
    else:
        form = _ProductForm()
    return render(request, 'admin/add_product.html', { 'form': form })

@staff_member_required(login_url='/adminpanel/login/')
def admin_edit_product(request, product_id):
    from django import forms
    product = get_object_or_404(Product, id=product_id)
    class _ProductForm(forms.ModelForm):
        class Meta:
            model = Product
            fields = ['name','category','gender','brand','price','stock','description','image','is_new','is_sale','related_products']
    if request.method == 'POST':
        form = _ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated')
            return redirect('store:admin_products')
    else:
        form = _ProductForm(instance=product)
    return render(request, 'admin/add_product.html', { 'form': form, 'editing': True, 'product_obj': product })

@staff_member_required(login_url='/adminpanel/login/')
def admin_delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted')
    return redirect('store:admin_products')

@staff_member_required(login_url='/adminpanel/login/')
def admin_categories(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'admin/view_categories.html', { 'categories': categories })

@staff_member_required(login_url='/adminpanel/login/')
def admin_add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name','').strip()
        if name:
            Category.objects.get_or_create(name=name)
            messages.success(request, 'Category saved')
            return redirect('store:admin_categories')
        messages.error(request, 'Name is required')
    return render(request, 'admin/add_category.html')

@staff_member_required(login_url='/adminpanel/login/')
def admin_edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        name = request.POST.get('name','').strip()
        if name:
            category.name = name
            category.save(update_fields=['name'])
            messages.success(request, 'Category updated')
            return redirect('store:admin_categories')
        messages.error(request, 'Name required')
    return render(request, 'admin/add_category.html', { 'editing': True, 'category_obj': category })

@staff_member_required(login_url='/adminpanel/login/')
def admin_delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted')
    return redirect('store:admin_categories')

@staff_member_required(login_url='/adminpanel/login/')
def admin_orders(request):
    orders = Order.objects.select_related('customer').order_by('-date')
    return render(request, 'admin/view_orders.html', { 'orders': orders })

@staff_member_required(login_url='/adminpanel/login/')
def admin_toggle_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    action = request.GET.get('action')
    if action == 'complete':
        order.status = True
        order.canceled = False
    elif action == 'cancel':
        order.canceled = True
        order.status = False
    order.save(update_fields=['status','canceled'])
    messages.success(request, f'Order {order.id} updated')
    return redirect('store:admin_orders')

def admin_login(request):
    # Allow either email or username in a single input field
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('store:admin_dashboard')
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '')
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        user = None
        if '@' in identifier:
            # treat as email
            try:
                uobj = UserModel.objects.get(email__iexact=identifier)
                user = authenticate(request, username=uobj.username, password=password)
            except UserModel.DoesNotExist:
                user = None
        else:
            # treat as username
            user = authenticate(request, username=identifier, password=password)
        if user and user.is_staff:
            login(request, user)
            messages.success(request, 'Welcome admin')
            return redirect('store:admin_dashboard')
        messages.error(request, 'Invalid admin credentials')
    return render(request, 'admin/login.html')

@staff_member_required(login_url='/adminpanel/login/')
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order.objects.select_related('customer').prefetch_related('items__product'), id=order_id)
    payment = getattr(order, 'payment', None)
    return render(request, 'admin/order_detail.html', {
        'order': order,
        'payment': payment,
    })
