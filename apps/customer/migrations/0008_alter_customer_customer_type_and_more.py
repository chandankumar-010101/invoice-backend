# Generated by Django 4.0.5 on 2022-06-13 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0007_alter_customer_customer_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='customer_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Business'), (2, 'Goverment'), (3, 'Individual'), (4, 'Other')], default=4),
        ),
        migrations.AlterField(
            model_name='customer',
            name='payments_term',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Net 15'), (2, 'Net 30'), (3, 'Net 45'), (4, 'Net 60'), (5, 'Net 90'), (6, 'Other')], default=6),
        ),
    ]
