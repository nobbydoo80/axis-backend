# Generated by Django 2.2 on 2020-12-22 20:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0112_auto_20201222_2022"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="hirlproject",
            name="multi_family_building_count",
        ),
        migrations.RemoveField(
            model_name="historicalhirlproject",
            name="multi_family_building_count",
        ),
    ]
