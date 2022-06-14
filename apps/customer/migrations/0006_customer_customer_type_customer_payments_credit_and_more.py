# Generated by Django 4.0.5 on 2022-06-13 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0005_alter_customer_created_on_alter_customer_updated_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='customer_type',
            field=models.CharField(choices=[(1, 'Business'), (2, 'Goverment'), (3, 'Individual'), (4, 'Other')], default='Other', max_length=30),
        ),
        migrations.AddField(
            model_name='customer',
            name='payments_credit',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='payments_term',
            field=models.CharField(choices=[(1, 'Net 15'), (2, 'Net 30'), (3, 'Net 45'), (4, 'Net 60'), (5, 'Net 90'), (6, 'Other')], default='Other', max_length=30),
        ),
    ]
