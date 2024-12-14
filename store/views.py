from itertools import product
from django.shortcuts import render,redirect
from .models import Product
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages

# for registering new user
# import user model for registering new user 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from django import forms


# category_page
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Category, Product

def category_page(request, foo):
    """
    Handles requests for category pages.
    
    Args:
        request: The HTTP request object.
        foo: The category name from the URL, typically slugified (e.g., 'mens-fashion').

    Returns:
        Renders the category page with products under the given category.
        Redirects to the home page with an error message if the category doesn't exist.
    """
    # Replace hyphens with spaces to match the category name in the database
    category_name = foo.replace('-', ' ')

    try:
        # Fetch the category from the database, ignoring case differences
        category = get_object_or_404(Category, name__iexact=category_name)

        # Get all products that belong to the fetched category
        products = Product.objects.filter(Category=category)

        # Render the category page template and pass the products and category details
        return render(request, 'category.html', {
            'products': products,  # List of products in the selected category
            'category': category   # The current category being viewed
        })
        # return render(request, f'category/{category.name.lower()}.html', {'products': products, 'category': category})

    except Category.DoesNotExist:
        # If the category does not exist, show an error message
        messages.error(request, "The category you are looking for does not exist.")
        return redirect('home')  # Redirect to the home page


    
def product_page(request,pk):
    product=Product.objects.get(id=pk)
    return render(request ,'product.html', {'product':product})

# Create your views here.
def home(request):
    products=Product.objects.all()
    return render(request ,'home.html',{'products':products})

def login_page(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        
        user =authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request,{"you have been logged in"})
            return redirect('home')
        else:
            messages.success(request,{"There was an error."})
            return redirect('home')
    else:   
        return render(request ,'login.html',{})

def logout_page(request):
    logout(request)
    messages.success(request, ("You have been logged out..."))
    return redirect('home')


def register_page(request):
    form = SignUpForm
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
        
        # Authenticate the user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            User=authenticate(username=username,password=password)
            
            # Log in the user
            login(request,user)
            messages.success(request,("You are registered successfullly:"))
            return redirect('home')
        else:
            messages.success(request,("Invalid Registration.Please try again:"))
            return redirect('register')
    else:
        return render(request ,'register.html',{'form':form})

