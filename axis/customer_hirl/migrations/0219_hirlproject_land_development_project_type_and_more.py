# Generated by Django 4.0.7 on 2022-10-21 09:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0218_remove_hirlproject_ld_phase_parent_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirlproject",
            name="land_development_project_type",
            field=models.CharField(
                blank=True,
                choices=[("main", "Main"), ("letter", "Letter of Approval"), ("phase", "Phase")],
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="land_development_project_type",
            field=models.CharField(
                blank=True,
                choices=[("main", "Main"), ("letter", "Letter of Approval"), ("phase", "Phase")],
                max_length=255,
                null=True,
            ),
        ),
    ]