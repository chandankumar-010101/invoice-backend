# Generated by Django 4.0.5 on 2022-06-29 09:53

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0022_customer_industry_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='primary_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
    ]
