# Generated by Django 4.0.5 on 2022-08-04 07:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoice', '0011_paymentreminder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethods',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_method', to=settings.AUTH_USER_MODEL),
        ),
    ]
