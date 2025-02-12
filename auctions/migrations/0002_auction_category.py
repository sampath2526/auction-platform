# Generated by Django 5.0 on 2025-01-28 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='category',
            field=models.CharField(choices=[('electronics', 'Electronics'), ('furniture', 'Furniture'), ('art', 'Art'), ('fashion', 'Fashion'), ('vehicles', 'Vehicles')], default='electronics', max_length=50),
        ),
    ]
