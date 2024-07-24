# Generated by Django 1.11.26 on 2020-01-28 19:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("equipment", "0012_auto_20191113_1650"),
    ]

    operations = [
        migrations.AlterField(
            model_name="equipment",
            name="calibration_company",
            field=models.CharField(max_length=255, verbose_name="Calibration Company"),
        ),
        migrations.AlterField(
            model_name="equipment",
            name="calibration_cycle",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "Annual"), (1, "Every 2 years"), (2, "Every 3 years")],
                default=0,
                verbose_name="Calibration Cycle",
            ),
        ),
        migrations.AlterField(
            model_name="equipment",
            name="calibration_date",
            field=models.DateField(verbose_name="Calibration Date"),
        ),
        migrations.AlterField(
            model_name="equipment",
            name="equipment_model",
            field=models.CharField(max_length=255, verbose_name="Model"),
        ),
        migrations.AlterField(
            model_name="equipment",
            name="equipment_type",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "Manometer"), (1, "Blower Door Fan"), (2, "Laser Tape Measure")],
                default=0,
                verbose_name="Equipment Type",
            ),
        ),
    ]