# Generated by Django 4.0.5 on 2022-09-01 05:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0028_alter_notification_created_at_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ('id',)},
        ),
    ]