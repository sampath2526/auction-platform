# Generated by Django 5.0 on 2025-01-30 05:00

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_bookmark'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='bookmarked_by',
            field=models.ManyToManyField(blank=True, related_name='bookmarked_auctions', to=settings.AUTH_USER_MODEL),
        ),
    ]
