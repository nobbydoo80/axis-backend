# Generated by Django 4.0.8 on 2022-11-03 14:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer_hirl", "0220_hirlproject_land_development_phase_number_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="hirlproject",
            name="is_require_final_inspection",
            field=models.BooleanField(
                default=True, verbose_name="Will this project require a Final inspection?"
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="is_require_final_inspection",
            field=models.BooleanField(
                default=True, verbose_name="Will this project require a Final inspection?"
            ),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="is_require_rough_inspection",
            field=models.BooleanField(
                default=True, verbose_name="Will this remodel project require a Rough inspection?"
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="is_require_rough_inspection",
            field=models.BooleanField(
                default=True, verbose_name="Will this remodel project require a Rough inspection?"
            ),
        ),
    ]
