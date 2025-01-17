# Generated by Django 1.11.16 on 2018-10-08 18:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("floorplan", "0002_auto_20181008_1815"),
    ]

    operations = [
        migrations.AlterField(
            model_name="floorplan",
            name="component_serialization",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="floorplan",
            name="simulation_result",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="historicalfloorplan",
            name="component_serialization",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="historicalfloorplan",
            name="simulation_result",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
