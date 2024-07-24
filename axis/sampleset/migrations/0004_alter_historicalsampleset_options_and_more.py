# Generated by Django 4.0.6 on 2022-07-22 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("sampleset", "0003_auto_20190725_1619"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicalsampleset",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical sample set",
                "verbose_name_plural": "historical sample sets",
            },
        ),
        migrations.AlterModelOptions(
            name="historicalsamplingproviderapproval",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical sampling provider approval",
                "verbose_name_plural": "historical Provider Sampling Approvals",
            },
        ),
        migrations.AlterField(
            model_name="historicalsampleset",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalsampleset",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalsamplingproviderapproval",
            name="history_date",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="historicalsamplingproviderapproval",
            name="id",
            field=models.BigIntegerField(
                auto_created=True, blank=True, db_index=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="historicalsamplingproviderapproval",
            name="provider",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="company.company",
            ),
        ),
        migrations.AlterField(
            model_name="sampleset",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="samplesethomestatus",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="samplingproviderapproval",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="samplingproviderapproval",
            name="provider",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sampling_approver",
                to="company.company",
            ),
        ),
    ]
