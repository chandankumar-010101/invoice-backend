# Generated by Django 4.0.5 on 2022-07-25 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0004_alter_invoice_options_alter_invoice_invoice_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='reminder',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]