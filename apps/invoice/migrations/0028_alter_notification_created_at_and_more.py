# Generated by Django 4.0.5 on 2022-08-30 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0027_notification_icon_class_notification_icon_colour'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]