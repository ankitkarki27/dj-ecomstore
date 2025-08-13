from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),
    path('product/<int:pk>/', views.product_page, name='product_page'),
    path('category/<str:foo>/', views.category_page, name='category'),

    # Cart URLs
   path('cart/', views.cart_page, name='cart'),
   path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
   path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
   path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),

    # Order / Checkout URLs
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),

]
