# Generated by Django 3.1.9 on 2021-06-10 15:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("qa", "0013_auto_20210224_1038"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalqastatus",
            name="hirl_reviewer_wri_value_awarded",
            field=models.IntegerField(null=True, verbose_name="Reviewer WRI Value Awarded"),
        ),
        migrations.AddField(
            model_name="historicalqastatus",
            name="hirl_water_sense_confirmed",
            field=models.BooleanField(null=True, verbose_name="WaterSense Confirmed"),
        ),
        migrations.AddField(
            model_name="qastatus",
            name="hirl_reviewer_wri_value_awarded",
            field=models.IntegerField(null=True, verbose_name="Reviewer WRI Value Awarded"),
        ),
        migrations.AddField(
            model_name="qastatus",
            name="hirl_water_sense_confirmed",
            field=models.BooleanField(null=True, verbose_name="WaterSense Confirmed"),
        ),
        migrations.AlterField(
            model_name="historicalqastatus",
            name="hirl_verifier_points_awarded",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="Reviewer Points Awarded"
            ),
        ),
        migrations.AlterField(
            model_name="qastatus",
            name="hirl_verifier_points_awarded",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="Reviewer Points Awarded"
            ),
        ),
    ]