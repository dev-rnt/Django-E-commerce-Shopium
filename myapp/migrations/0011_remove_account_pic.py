# Generated by Django 5.0.1 on 2024-02-11 17:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_account_pic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='pic',
        ),
    ]
