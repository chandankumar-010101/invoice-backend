# Generated by Django 4.0.5 on 2022-07-14 06:30

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0025_alter_customer_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alternatecontact',
            name='alternate_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
    ]