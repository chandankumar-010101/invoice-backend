# Generated by Django 4.0.5 on 2022-06-16 10:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0005_alter_customer_primary_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='alternate_contact',
        ),
        migrations.AddField(
            model_name='alternatecontact',
            name='customer',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='customer', to='customer.customer'),
        ),
    ]
