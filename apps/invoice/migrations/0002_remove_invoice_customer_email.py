# Generated by Django 4.0.5 on 2022-06-08 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='customer_email',
        ),
    ]
