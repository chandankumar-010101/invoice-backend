# Generated by Django 4.0.5 on 2022-08-18 06:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0026_alter_alternatecontact_alternate_phone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='open_balance',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='outstanding_invoices',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='overdue_balance',
        ),
    ]
