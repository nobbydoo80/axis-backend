# Generated by Django 4.0.7 on 2022-10-24 14:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0219_hirlproject_land_development_project_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirlproject",
            name="land_development_phase_number",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="land_development_phase_number",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="land_development_project_type",
            field=models.CharField(
                blank=True,
                choices=[("letter", "Letter of Approval"), ("phase", "Phase")],
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="land_development_project_type",
            field=models.CharField(
                blank=True,
                choices=[("letter", "Letter of Approval"), ("phase", "Phase")],
                max_length=255,
                null=True,
            ),
        ),
    ]