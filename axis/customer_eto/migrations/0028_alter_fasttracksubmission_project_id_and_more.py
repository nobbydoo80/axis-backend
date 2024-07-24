# Generated by Django 4.1.7 on 2023-03-15 14:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_eto", "0027_fasttracksubmission_set_submission_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fasttracksubmission",
            name="project_id",
            field=models.CharField(blank=True, help_text="ENH Project ID", max_length=20),
        ),
        migrations.AlterField(
            model_name="fasttracksubmission",
            name="solar_project_id",
            field=models.CharField(
                blank=True, help_text="SLE Project ID", max_length=20, null=True
            ),
        ),
        migrations.AlterField(
            model_name="historicalfasttracksubmission",
            name="project_id",
            field=models.CharField(blank=True, help_text="ENH Project ID", max_length=20),
        ),
        migrations.AlterField(
            model_name="historicalfasttracksubmission",
            name="solar_project_id",
            field=models.CharField(
                blank=True, help_text="SLE Project ID", max_length=20, null=True
            ),
        ),
    ]