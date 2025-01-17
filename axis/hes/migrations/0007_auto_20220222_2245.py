# Generated by Django 3.2.12 on 2022-02-22 22:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hes", "0006_auto_20201230_1218"),
    ]

    operations = [
        migrations.AddField(
            model_name="hessimulation",
            name="estimated_annual_energy_cost",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="historicalhessimulation",
            name="estimated_annual_energy_cost",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="hescredentials",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hessimulation",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="hessimulationstatus",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalhescredentials",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalhessimulation",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalhessimulationstatus",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
    ]
