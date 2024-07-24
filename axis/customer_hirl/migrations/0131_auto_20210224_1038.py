# Generated by Django 3.1.6 on 2021-02-24 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("eep_program", "0019_auto_20210205_0946"),
        ("customer_hirl", "0130_auto_20210212_2017"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hirlproject",
            name="eep_program",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="eep_program.eepprogram",
                verbose_name="Program",
            ),
        ),
        migrations.AlterField(
            model_name="hirlproject",
            name="green_energy_badges",
            field=models.ManyToManyField(
                blank=True,
                to="customer_hirl.HIRLGreenEnergyBadge",
                verbose_name="NGBS Green+ Badges",
            ),
        ),
        migrations.AlterField(
            model_name="historicalhirlproject",
            name="eep_program",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="eep_program.eepprogram",
                verbose_name="Program",
            ),
        ),
    ]