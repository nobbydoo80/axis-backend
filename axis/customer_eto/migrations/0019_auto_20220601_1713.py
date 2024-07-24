# Generated by Django 3.2.13 on 2022-06-01 17:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_eto", "0018_auto_20220330_1733"),
    ]

    operations = [
        migrations.AddField(
            model_name="fasttracksubmission",
            name="ev_ready_builder_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="heat_pump_water_heater_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="solar_ready_builder_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="solar_ready_verifier_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="solar_storage_builder_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="ev_ready_builder_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="heat_pump_water_heater_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="solar_ready_builder_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="solar_ready_verifier_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="solar_storage_builder_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]