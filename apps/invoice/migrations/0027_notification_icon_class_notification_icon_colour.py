# Generated by Django 4.0.5 on 2022-08-30 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0026_notification_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='icon_class',
            field=models.CharField(blank=True, default='fa fa-clock-o', max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='icon_colour',
            field=models.CharField(blank=True, default='red', max_length=150, null=True),
        ),
    ]
