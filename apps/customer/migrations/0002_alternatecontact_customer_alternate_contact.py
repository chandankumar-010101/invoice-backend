# Generated by Django 4.0.5 on 2022-06-16 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlternateContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30, null=True)),
                ('role', models.CharField(blank=True, max_length=30, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='alternate_contact',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='alternate_contact', to='customer.alternatecontact'),
        ),
    ]
