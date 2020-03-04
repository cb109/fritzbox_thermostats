# Generated by Django 3.0.3 on 2020-03-04 21:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thermostats', '0004_auto_20200301_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='thermostat',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='thermostatlog',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='weekday',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]