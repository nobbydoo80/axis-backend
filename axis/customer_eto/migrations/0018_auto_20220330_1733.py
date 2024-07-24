# Generated by Django 3.2.12 on 2022-03-30 17:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_eto", "0017_auto_20220308_1820"),
    ]

    operations = [
        migrations.AddField(
            model_name="fasttracksubmission",
            name="percent_generation_kwh",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="percent_generation_kwh",
            field=models.FloatField(default=0.0),
        ),
    ]