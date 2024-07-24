# Generated by Django 2.2 on 2020-07-28 12:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("floorplan", "0010_auto_20200128_1940"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="floorplan",
            options={
                "ordering": ("name", "number"),
                "permissions": (("can_simulate", "Ability to simulate"),),
                "verbose_name": "Floorplan",
            },
        ),
    ]
