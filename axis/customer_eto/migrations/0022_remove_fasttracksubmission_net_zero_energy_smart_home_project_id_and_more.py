# Generated by Django 4.0.8 on 2022-11-24 06:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("customer_eto", "0021_fasttracksubmission_estimated_annual_energy_costs_code_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="fasttracksubmission",
            name="net_zero_energy_smart_home_project_id",
        ),
        migrations.RemoveField(
            model_name="historicalfasttracksubmission",
            name="net_zero_energy_smart_home_project_id",
        ),
    ]