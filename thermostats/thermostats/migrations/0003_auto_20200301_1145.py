# Generated by Django 3.0.3 on 2020-03-01 10:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('thermostats', '0002_thermostatlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thermostatlog',
            name='rule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='thermostats.Rule'),
        ),
    ]