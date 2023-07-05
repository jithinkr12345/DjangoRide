# Generated by Django 4.2.2 on 2023-06-06 07:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('driver_id', models.IntegerField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('dob', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=100)),
                ('license_no', models.CharField(max_length=100)),
                ('car_year', models.IntegerField()),
                ('car_model', models.IntegerField()),
                ('car_name', models.CharField(max_length=100)),
                ('car_no', models.CharField(max_length=100)),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('write_date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]