from itertools import product
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product, Cart, CartItem
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm
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
    _all_products = list(Product.objects.select_related('Category').all())
    if not _all_products:
        return
    text_data = []
    for p in _all_products:
        cat = p.Category.name if p.Category else ''
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
        text_data = []
        for p in _all_products:
            category_weight = 3 if p.Category == product.Category else 1
            category_text = (p.Category.name + " ") * category_weight if p.Category else ""
            specs = f" {p.name} "
            text_data.append(f"{category_text}{specs}{p.description if p.description else ''}")

        _product_tfidf_vectorizer = TfidfVectorizer(
            token_pattern=r'(?u)\b\w+\b|\b\d+[A-Za-z]+\b',
            stop_words='english'
        )
        _product_tfidf_matrix = _product_tfidf_vectorizer.fit_transform(text_data)
        product_index = next(i for i, p in enumerate(_all_products) if p.id == product.id)
    except Exception as e:
        print(f"Recommendation error: {str(e)}")
        return []

    cosine_similarities = cosine_similarity(
        _product_tfidf_matrix[product_index:product_index+1],
        _product_tfidf_matrix
    ).flatten()

    similar_indices = cosine_similarities.argsort()[::-1][1:num_recommendations+1]
    return [
        (_all_products[i], float(cosine_similarities[i]))
        for i in similar_indices
        if cosine_similarities[i] > 0.1
    ]

# =========================
# Home & Product Views
# =========================
def home(request):
    products = Product.objects.all()
    featured_products = Product.objects.filter(is_sale=True)[:4]
    new_products = [p for p in products if p.is_new][:4]
    return render(request, 'home.html', {
        'products': products,
        'featured_products': featured_products,
        'new_products': new_products
    })

def category_page(request, foo):
    category_name = foo.replace('-', ' ')
    try:
        category = get_object_or_404(Category, name__iexact=category_name)
        products = Product.objects.filter(Category=category)
        return render(request, 'category.html', {
            'products': products,
            'category': category
        })
    except Category.DoesNotExist:
        messages.error(request, "The category you are looking for does not exist.")
        return redirect('store:home')

def product_page(request, pk):
    product = get_object_or_404(Product, id=pk)
    similar_products = get_similar_products(product, num_recommendations=4)
    if not similar_products:
        similar_products = list(Product.objects
                                .filter(Category=product.Category)
                                .exclude(id=product.id)
                                .order_by('?')[:4])
        similar_products = [(p, 0.0) for p in similar_products]
    return render(request, 'product.html', {
        'product': product,
        'similar_products': similar_products
    })

# =========================
# Auth Views
# =========================
def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "You have been logged in")
            return redirect('store:home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('store:login')
    return render(request, 'login.html')

def logout_page(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('store:home')

def register_page(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "You are registered successfully")
            return redirect('store:home')
        else:
            messages.error(request, "Invalid registration. Please try again.")
            return redirect('store:register')
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
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add items to the cart.")
        return redirect('store:login')

    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.name} added to cart")
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
from .models import Order, Payment

# =========================
# Order / Checkout Views
# =========================

def checkout(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to checkout.")
        return redirect('store:login')

    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    total = sum(item.product.price * item.quantity for item in items)

    if request.method == 'POST':
        # Collect user info from form
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        payment_method = request.POST.get('payment_method', 'cash')

        # Create orders for each cart item
        for item in items:
            order = Order.objects.create(
                product=item.product,
                customer=request.user.customer,  # Assuming you have a Customer linked to User
                quantity=item.quantity,
                address=address,
                phone=phone,
                status=False  # default pending
            )

            # Create Payment
            Payment.objects.create(
                order=order,
                method=payment_method,
                amount=item.product.price * item.quantity,
                status='pending'
            )

        # Clear cart
        cart.items.all().delete()
        messages.success(request, "Your order has been placed successfully!")
        return redirect('store:order_history')

    return render(request, 'checkout.html', {'cart': cart, 'items': items, 'total': total})

def order_history(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view your orders.")
        return redirect('store:login')

    orders = Order.objects.filter(customer=request.user.customer).order_by('-date')
    return render(request, 'order_history.html', {'orders': orders})

def order_detail(request, order_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to view this order.")
        return redirect('store:login')

    order = get_object_or_404(Order, id=order_id, customer=request.user.customer)
    return render(request, 'order_detail.html', {'order': order})
