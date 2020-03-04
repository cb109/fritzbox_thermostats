# Generated by Django 3.0.3 on 2020-03-04 21:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('thermostats', '0006_auto_20200304_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thermostatlog',
            name='rule',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='thermostats.Rule'),
        ),
        migrations.AlterField(
            model_name='thermostatlog',
            name='thermostat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='thermostats.Thermostat'),
        ),
    ]