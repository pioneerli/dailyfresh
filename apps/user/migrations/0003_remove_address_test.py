# Generated by Django 4.0.3 on 2022-04-15 13:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_address_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='test',
        ),
    ]
