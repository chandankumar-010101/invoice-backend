# Generated by Django 4.0.5 on 2022-09-14 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0038_remove_carddetail_payment_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='invoice',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
