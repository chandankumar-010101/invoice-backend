# Generated by Django 4.0.5 on 2022-06-23 09:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0013_remove_customer_email_remove_customer_phone_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PrimaryContact',
        ),
    ]