# Generated by Django 4.0.6 on 2025-04-08 05:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_customer_meal_preference'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='meal_preference',
        ),
    ]
