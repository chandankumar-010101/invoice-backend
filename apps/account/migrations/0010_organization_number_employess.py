# Generated by Django 4.0.5 on 2022-09-14 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_user_parent_alter_user_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='number_employess',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
