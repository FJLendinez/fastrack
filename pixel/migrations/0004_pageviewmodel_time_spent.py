# Generated by Django 3.0.8 on 2020-07-15 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pixel', '0003_auto_20200713_0522'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageviewmodel',
            name='time_spent',
            field=models.FloatField(default=0),
        ),
    ]
