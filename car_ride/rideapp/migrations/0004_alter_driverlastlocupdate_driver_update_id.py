# Generated by Django 4.2.2 on 2023-08-01 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rideapp', '0003_alter_carride_ride_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverlastlocupdate',
            name='driver_update_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
