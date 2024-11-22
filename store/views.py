from django.shortcuts import render
from .models import Product
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages

# Create your views here.
def home(request):
    products=Product.objects.all()
    return render(request ,'home.html',{'products':products})

def login_page(request):
    return render(request ,'login.html',{})

def logout_page(request):
    pass