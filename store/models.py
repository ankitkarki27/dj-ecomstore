from django.db import models
import datetime
# Create your models here.

# category,customer,product,order

from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)  # Category name (max 50 chars)

    def __str__(self):
        return self.name  # Returns category name as string

    class Meta:
        verbose_name_plural = 'categories'  # Admin plural name

        
class Customer(models.Model):
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone=models.CharField(max_length=10)
    email=models.EmailField(max_length=100)
    password=models.CharField(max_length=128)   
    
    def __str__(self):
        return f'{self.first_name}{self.last_name}'


class Product(models.Model):
    name=models.CharField(max_length=100)
    price=models.DecimalField(default=0,decimal_places=2,max_digits=6)
    Category=models.ForeignKey(Category,on_delete=models.CASCADE,default=1)
    description=models.CharField(max_length=250,default='',blank=True,null=True)
    image=models.ImageField(upload_to='uploads/product/')
    
    def __str__(self):
        return self.name
    
class Order(models.Model):
    Product=models.ForeignKey(Product,on_delete=models.CASCADE)
    Customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    address=models.CharField(max_length=100,default='',blank=True)
    phone=models.CharField(max_length=10)
    date=models.DateField(default=datetime.datetime.today)
    status=models.BooleanField(default=False)
    
    def __str__(self):
        return self.product
    
