# Generated by Django 1.11.26 on 2020-01-28 19:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("subdivision", "0005_smart_thermostat_qty"),
    ]

    operations = [
        migrations.AlterField(
            model_name="floorplanapproval",
            name="thermostat_qty",
            field=models.IntegerField(choices=[(0, "0"), (1, "1"), (2, "2"), (3, "3")], default=0),
        ),
    ]