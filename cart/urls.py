# cart/urls.py
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_summary, name='cart_summary'),  # View cart summary
    path('add/', views.cart_add, name='cart_add'),  # Add item to cart
    path('delete/', views.cart_delete, name='cart_delete'),  # Remove item from cart (using POST)
    path('update/', views.cart_update, name='cart_update'),  # Update cart item quantity

    #  path('esewa_payment/', views.esewa_payment, name='esewa_payment'),
    #  path('payment_success/', views.payment_success, name='payment_success'),
    # path('payment_failure/', views.payment_failure, name='payment_failure'),
]
