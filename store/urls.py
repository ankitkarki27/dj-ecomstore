from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),
    path('product/<int:pk>/', views.product_page, name='product_page'),
    path('search/', views.search_products, name='search'),
    path('category/<str:foo>/', views.category_page, name='category'),

    # Cart
   path('cart/', views.cart_page, name='cart'),
   path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
   path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
   path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),

    # Order&Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('profile/', views.profile, name='profile'),

    # admin panel
    path('adminpanel/login/', views.admin_login, name='admin_login'),
    path('adminpanel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('adminpanel/products/', views.admin_products, name='admin_products'),
    path('adminpanel/products/add/', views.admin_add_product, name='admin_add_product'),
    path('adminpanel/categories/', views.admin_categories, name='admin_categories'),
    path('adminpanel/categories/add/', views.admin_add_category, name='admin_add_category'),
    path('adminpanel/orders/', views.admin_orders, name='admin_orders'),
    path('adminpanel/orders/update/<int:order_id>/', views.admin_toggle_order_status, name='admin_toggle_order_status'),
    path('adminpanel/orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('adminpanel/products/edit/<int:product_id>/', views.admin_edit_product, name='admin_edit_product'),
    path('adminpanel/products/delete/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),
    path('adminpanel/categories/edit/<int:category_id>/', views.admin_edit_category, name='admin_edit_category'),
    path('adminpanel/categories/delete/<int:category_id>/', views.admin_delete_category, name='admin_delete_category'),

]
