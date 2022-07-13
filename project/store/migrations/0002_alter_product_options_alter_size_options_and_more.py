# Generated by Django 4.0.5 on 2022-07-08 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='size',
            options={'ordering': ['size']},
        ),
        migrations.AddField(
            model_name='orderdone',
            name='total',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]