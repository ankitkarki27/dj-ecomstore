# Generated by Django 5.1.1 on 2025-01-13 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_cart_cartitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='product',
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]