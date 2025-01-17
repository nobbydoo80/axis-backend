# Generated by Django 3.2.12 on 2022-03-08 18:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_eto", "0016_auto_20211206_1937"),
    ]

    operations = [
        migrations.AddField(
            model_name="fasttracksubmission",
            name="cobid_builder_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="fasttracksubmission",
            name="cobid_verifier_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="cobid_builder_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name="historicalfasttracksubmission",
            name="cobid_verifier_incentive",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
