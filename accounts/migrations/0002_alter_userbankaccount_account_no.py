# Generated by Django 4.2.7 on 2024-01-23 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbankaccount',
            name='account_no',
            field=models.IntegerField(unique=True),
        ),
    ]
