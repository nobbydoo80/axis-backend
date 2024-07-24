# Generated by Django 1.11.16 on 2018-10-08 18:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("company", "0001_initial"),
        ("floorplan", "0001_initial"),
        ("remrate_data", "0001_initial"),
        ("ekotrope", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalfloorplan",
            name="remrate_target",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="remrate_data.Simulation",
            ),
        ),
        migrations.AddField(
            model_name="floorplandocument",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="floorplan_document",
                to="company.Company",
            ),
        ),
        migrations.AddField(
            model_name="floorplandocument",
            name="floorplan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="floorplan.Floorplan",
            ),
        ),
        migrations.AddField(
            model_name="floorplan",
            name="documents",
            field=models.ManyToManyField(
                related_name="floorplan_documents",
                through="floorplan.FloorplanDocument",
                to="company.Company",
            ),
        ),
        migrations.AddField(
            model_name="floorplan",
            name="ekotrope_houseplan",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="ekotrope.HousePlan",
            ),
        ),
        migrations.AddField(
            model_name="floorplan",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="company.Company"
            ),
        ),
        migrations.AddField(
            model_name="floorplan",
            name="remrate_target",
            field=models.OneToOneField(
                blank=True,
                help_text="Type the first few letters of the name of the REM/Rate data set or subdivision and select the correct REM/Rate data set from the list presented.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="remrate_data.Simulation",
            ),
        ),
        migrations.AddField(
            model_name="floorplan",
            name="systems",
            field=models.ManyToManyField(
                related_name="floorplan_systems",
                through="floorplan.System",
                to="floorplan.SystemType",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="system",
            unique_together=set([("system_type", "floorplan")]),
        ),
        migrations.AlterUniqueTogether(
            name="floorplan",
            unique_together=set([("name", "remrate_target")]),
        ),
    ]