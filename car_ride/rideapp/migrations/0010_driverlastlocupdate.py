# Generated by Django 4.2.2 on 2023-07-04 11:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rideapp', '0009_alter_driver_car_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverLastLocUpdate',
            fields=[
                ('driver_update_id', models.IntegerField(primary_key=True, serialize=False)),
                ('longitude', models.CharField(max_length=100)),
                ('latitude', models.CharField(max_length=100)),
                ('driver_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rideapp.driver')),
            ],
        ),
    ]