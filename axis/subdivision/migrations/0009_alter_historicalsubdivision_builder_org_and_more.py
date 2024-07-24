# Generated by Django 4.0.6 on 2022-07-22 16:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("subdivision", "0008_alter_historicalsubdivision_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalsubdivision",
            name="builder_org",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text='Type the first few letters of the name of the Builder that is building all homes in this subdivision, and select the correct company from the list presented.  If the correct company is not available, click "Add New" to add a new Builder or Builder association.',
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="company.company",
                verbose_name="Builder",
            ),
        ),
        migrations.AlterField(
            model_name="subdivision",
            name="builder_org",
            field=models.ForeignKey(
                help_text='Type the first few letters of the name of the Builder that is building all homes in this subdivision, and select the correct company from the list presented.  If the correct company is not available, click "Add New" to add a new Builder or Builder association.',
                on_delete=django.db.models.deletion.CASCADE,
                related_name="builder_org_subdivisions",
                to="company.company",
                verbose_name="Builder",
            ),
        ),
    ]
