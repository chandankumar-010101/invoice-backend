# Generated by Django 4.0.5 on 2022-06-16 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_rename_email_alternatecontact_alternate_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alternatecontact',
            name='alternate_role',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Business'), (2, 'Goverment'), (3, 'Individual'), (4, 'Other')], default=4),
        ),
    ]
