# Generated by Django 4.0.5 on 2022-08-10 05:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoice', '0016_rename_industry_rolesandpermissions_roles'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.PositiveSmallIntegerField(choices=[(1, 'Credit/Debit/Atm'), (2, 'Bank Transfer')])),
                ('holder_name', models.CharField(max_length=50, null=True)),
                ('card_number', models.CharField(max_length=16, null=True)),
                ('expiry_date', models.DateField()),
                ('cvv_code', models.CharField(max_length=3, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='card_details_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
