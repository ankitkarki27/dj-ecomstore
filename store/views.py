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

