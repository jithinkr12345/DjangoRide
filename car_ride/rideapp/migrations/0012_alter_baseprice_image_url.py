# Generated by Django 4.2.2 on 2023-07-30 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rideapp', '0011_baseprice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseprice',
            name='image_url',
            field=models.CharField(null=True),
        ),
    ]
