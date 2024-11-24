from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
    path('login/',views.login_page, name='login'),
    path('register/',views.register_page, name='register'),
    path('logout/',views.logout_page, name='logout'),
    path('product/<int:pk>',views.product_page, name='product'),
]
