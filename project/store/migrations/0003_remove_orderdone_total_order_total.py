# Generated by Django 4.0.5 on 2022-07-08 10:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_alter_product_options_alter_size_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdone',
            name='total',
        ),
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]