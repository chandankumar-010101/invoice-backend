# Generated by Django 4.0.5 on 2022-08-10 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0019_alter_invoice_invoice_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoicetransaction',
            name='amount',
            field=models.FloatField(blank=True, default=0.0, max_length=255, null=True),
        ),
    ]
