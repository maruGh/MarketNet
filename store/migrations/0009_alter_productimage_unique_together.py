# Generated by Django 4.2.7 on 2023-11-14 12:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0008_productimage"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="productimage",
            unique_together={("image", "product")},
        ),
    ]
