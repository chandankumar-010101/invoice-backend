# Generated by Django 4.0.5 on 2022-06-16 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_alternatecontact_customer_alternate_contact'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alternatecontact',
            old_name='email',
            new_name='alternate_email',
        ),
        migrations.RenameField(
            model_name='alternatecontact',
            old_name='name',
            new_name='alternate_name',
        ),
        migrations.RenameField(
            model_name='alternatecontact',
            old_name='phone',
            new_name='alternate_phone',
        ),
        migrations.RenameField(
            model_name='alternatecontact',
            old_name='role',
            new_name='alternate_role',
        ),
    ]
