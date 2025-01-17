# Generated by Django 1.11.26 on 2020-06-19 17:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("qa", "0004_auto_20200415_1542"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalqastatusstatelog",
            name="from_state",
            field=models.CharField(
                choices=[
                    ("received", "Received"),
                    ("in_progress", "In Progress"),
                    ("correction_required", "Correction Required"),
                    ("correction_received", "Correction Received"),
                    ("complete", "Complete"),
                ],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="historicalqastatusstatelog",
            name="to_state",
            field=models.CharField(
                choices=[
                    ("received", "Received"),
                    ("in_progress", "In Progress"),
                    ("correction_required", "Correction Required"),
                    ("correction_received", "Correction Received"),
                    ("complete", "Complete"),
                ],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="qastatusstatelog",
            name="from_state",
            field=models.CharField(
                choices=[
                    ("received", "Received"),
                    ("in_progress", "In Progress"),
                    ("correction_required", "Correction Required"),
                    ("correction_received", "Correction Received"),
                    ("complete", "Complete"),
                ],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="qastatusstatelog",
            name="to_state",
            field=models.CharField(
                choices=[
                    ("received", "Received"),
                    ("in_progress", "In Progress"),
                    ("correction_required", "Correction Required"),
                    ("correction_received", "Correction Received"),
                    ("complete", "Complete"),
                ],
                max_length=100,
            ),
        ),
    ]
