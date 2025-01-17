# Generated by Django 4.0.7 on 2022-10-20 14:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "customer_hirl",
            "0216_hirlprojectregistration_are_all_homes_in_ld_seeking_certification_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="hirlproject",
            name="ld_phase_parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="ld_phased_projects",
                to="customer_hirl.hirlproject",
                verbose_name="Land Development Phase Project",
            ),
        ),
        migrations.AddField(
            model_name="historicalhirlproject",
            name="ld_phase_parent",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="customer_hirl.hirlproject",
                verbose_name="Land Development Phase Project",
            ),
        ),
    ]
