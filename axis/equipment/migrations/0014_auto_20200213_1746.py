# Generated by Django 1.11.26 on 2020-02-13 17:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("equipment", "0013_auto_20200128_1940"),
    ]

    operations = [
        migrations.AddField(
            model_name="equipmentsponsorstatus",
            name="state_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="historicalequipmentsponsorstatus",
            name="state_notes",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="equipment",
            name="calibration_cycle",
            field=models.PositiveSmallIntegerField(
                choices=[(3, "Annual"), (1, "Every 2 years"), (2, "Every 3 years")],
                default=3,
                verbose_name="Calibration Cycle",
            ),
        ),
        migrations.AlterField(
            model_name="equipment",
            name="equipment_type",
            field=models.PositiveSmallIntegerField(
                choices=[(3, "Manometer"), (1, "Blower Door Fan"), (2, "Laser Tape Measure")],
                default=3,
                verbose_name="Equipment Type",
            ),
        ),
    ]