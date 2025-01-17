# Generated by Django 3.2.14 on 2022-07-20 23:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("remrate_data", "0021_alter_infiltration_hours_per_day"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicalsimulation",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical REM/Rate Data Set",
                "verbose_name_plural": "historical REM/Rate Data Sets",
            },
        ),
        migrations.AlterField(
            model_name="historicalsimulation",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
    ]
