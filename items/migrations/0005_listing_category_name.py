# Generated by Django 5.1.7 on 2025-03-13 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0004_listing_seller_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='category_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
