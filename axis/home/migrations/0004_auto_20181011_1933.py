# Generated by Django 1.11.16 on 2018-10-11 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("company", "0003_auto_20181010_2316"),
        ("subdivision", "0002_historicalsubdivision_history_change_reason_foo"),
        ("home", "0003_auto_20181010_2316"),
    ]

    operations = [
        migrations.AlterField(
            model_name="standarddisclosuresettings",
            name="company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="company.Company",
            ),
        ),
        migrations.AlterField(
            model_name="standarddisclosuresettings",
            name="home_status",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="home.EEPProgramHomeStatus",
            ),
        ),
        migrations.AlterField(
            model_name="standarddisclosuresettings",
            name="subdivision",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="subdivision.Subdivision",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="standarddisclosuresettings",
            unique_together=set(
                [("owner", "home_status"), ("owner", "company"), ("owner", "subdivision")]
            ),
        ),
    ]
