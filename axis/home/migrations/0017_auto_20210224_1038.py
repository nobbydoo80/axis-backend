# Generated by Django 3.1.6 on 2021-02-24 10:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("home", "0016_auto_20210212_1814"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eepprogramhomestatus",
            name="customer_hirl_final_verifier",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="final_verifier_epp_program_home_statuses",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Final Verifier",
            ),
        ),
        migrations.AlterField(
            model_name="eepprogramhomestatus",
            name="customer_hirl_rough_verifier",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="rough_verifier_epp_program_home_statuses",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Rough Verifier",
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogramhomestatus",
            name="customer_hirl_final_verifier",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Final Verifier",
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogramhomestatus",
            name="customer_hirl_rough_verifier",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Rough Verifier",
            ),
        ),
    ]
