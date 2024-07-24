# Generated by Django 1.11.26 on 2020-01-28 19:40

import axis.floorplan.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("floorplan", "0009_auto_20190925_1900"),
    ]

    operations = [
        migrations.AlterField(
            model_name="floorplan",
            name="comment",
            field=models.TextField(
                blank=True,
                help_text='Enter a comment for the floorplan if desired and click\non "Submit" to save the comment.',
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="floorplan",
            name="remrate_data_file",
            field=models.FileField(
                blank=True,
                help_text='Click on "Select file" and select a file from the\nfile browser.  Once selected, click on "Change" to select a new file or "Remove" to delete\nthe file.',
                max_length=512,
                null=True,
                upload_to=axis.floorplan.models.content_blgfile_name,
                verbose_name="REM/Rate™ File",
            ),
        ),
        migrations.AlterField(
            model_name="floorplan",
            name="remrate_target",
            field=models.OneToOneField(
                blank=True,
                help_text="Type the first few letters of the name of the REM/Rate data\nset or subdivision and select the correct REM/Rate data set from the list presented.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="remrate_data.Simulation",
                verbose_name="REM/Rate™ Data",
            ),
        ),
        migrations.AlterField(
            model_name="historicalfloorplan",
            name="comment",
            field=models.TextField(
                blank=True,
                help_text='Enter a comment for the floorplan if desired and click\non "Submit" to save the comment.',
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalfloorplan",
            name="remrate_data_file",
            field=models.TextField(
                blank=True,
                help_text='Click on "Select file" and select a file from the\nfile browser.  Once selected, click on "Change" to select a new file or "Remove" to delete\nthe file.',
                max_length=512,
                null=True,
                verbose_name="REM/Rate™ File",
            ),
        ),
        migrations.AlterField(
            model_name="historicalfloorplan",
            name="remrate_target",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Type the first few letters of the name of the REM/Rate data\nset or subdivision and select the correct REM/Rate data set from the list presented.",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="remrate_data.Simulation",
                verbose_name="REM/Rate™ Data",
            ),
        ),
    ]
