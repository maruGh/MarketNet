# Generated by Django 4.2.4 on 2023-08-18 12:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_rename_price_product_unit_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='created_at',
            new_name='placed_at',
        ),
    ]
