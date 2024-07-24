# Generated by Django 3.1.3 on 2021-01-28 15:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("remrate_data", "0014_auto_20201230_1218"),
    ]

    operations = [
        migrations.AddField(
            model_name="regionalcode",
            name="ny_design_costing",
            field=models.FloatField(blank=True, db_column="FNYDMVCT", null=True),
        ),
        migrations.AddField(
            model_name="regionalcode",
            name="ny_reference_costing",
            field=models.FloatField(blank=True, db_column="FNYRMVCT", null=True),
        ),
    ]