from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_remove_product_created_at_remove_product_sale_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='canceled',
            field=models.BooleanField(default=False),
        ),
    ]
