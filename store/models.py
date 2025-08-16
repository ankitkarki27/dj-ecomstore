from django.db import models
from django.core.validators import MinValueValidator
import datetime
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User


# =====================
# Category Model
# =====================
class Category(models.Model):
    name = models.CharField(max_length=50)  # Category name (max 50 chars)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


# =====================
# Customer Model
# =====================
class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=128)  # Should be hashed in production

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


# =====================
# Product Model
# =====================
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=10, choices=[('Men','Men'),('Women','Women'),('Kids','Kids'),('Unisex','Unisex')])
    brand = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])  # quantity available
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    is_new = models.BooleanField(default=False)
    is_sale = models.BooleanField(default=False)
    related_products = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='related_to', help_text="Manually picked similar products")

    def __str__(self):
        return self.name

    @property
    def out_of_stock(self):
        return self.stock <= 0

# =====================
# Order Model
# =====================
class Order(models.Model):
    """Master order (may contain multiple items). Existing product/quantity kept optional for legacy compatibility."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)  # legacy unused going forward
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, blank=True)  # legacy
    address = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=15, blank=True, default='')
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    canceled = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} for {self.customer}" 

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot unit price

    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order_id})"


# =====================
# Cart Model
# =====================
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user}"


# =====================
# CartItem Model
# =====================
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def line_total(self):
        try:
            return self.product.price * self.quantity
        except Exception:
            return 0

# =====================
# Payment Model
# =====================
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash on Delivery'),
        ('esewa', 'eSewa'),
        ('khalti', 'Khalti'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.method} payment for Order #{self.order.id} - {self.status}"
