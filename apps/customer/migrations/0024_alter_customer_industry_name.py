# Generated by Django 4.0.5 on 2022-06-29 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0023_alter_customer_primary_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='industry_name',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]