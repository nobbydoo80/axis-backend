# Generated by Django 1.11.17 on 2018-12-30 17:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eep_program", "0003_historicaleepprogram_history_change_reason_foo"),
        ("eep_program", "0005_auto_20181130_1905"),
    ]

    operations = [
        migrations.AddField(
            model_name="eepprogram",
            name="program_submit_date",
            field=models.DateField(
                blank=True,
                help_text="Last day the home can be submitted for certification.",
                null=True,
                verbose_name="Submission date",
            ),
        ),
        migrations.AddField(
            model_name="eepprogram",
            name="program_submit_warning",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="eepprogram",
            name="program_submit_warning_date",
            field=models.DateField(blank=True, null=True, verbose_name="Submit warning date"),
        ),
        migrations.AddField(
            model_name="historicaleepprogram",
            name="program_submit_date",
            field=models.DateField(
                blank=True,
                help_text="Last day the home can be submitted for certification.",
                null=True,
                verbose_name="Submission date",
            ),
        ),
        migrations.AddField(
            model_name="historicaleepprogram",
            name="program_submit_warning",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="historicaleepprogram",
            name="program_submit_warning_date",
            field=models.DateField(blank=True, null=True, verbose_name="Submit warning date"),
        ),
        migrations.AlterField(
            model_name="eepprogram",
            name="program_close_date",
            field=models.DateField(
                blank=True,
                help_text="Last day program can be added to home.",
                null=True,
                verbose_name="Close date",
            ),
        ),
        migrations.AlterField(
            model_name="eepprogram",
            name="program_end_date",
            field=models.DateField(
                blank=True,
                help_text="Last day program can be certified.",
                null=True,
                verbose_name="End date",
            ),
        ),
        migrations.AlterField(
            model_name="eepprogram",
            name="program_start_date",
            field=models.DateField(
                default=datetime.date.today,
                help_text="First date a program can be submitted for certification.",
                verbose_name="Start date",
            ),
        ),
        migrations.AlterField(
            model_name="eepprogram",
            name="program_visibility_date",
            field=models.DateField(
                default=datetime.date.today,
                help_text="Date program is available for use on a home.",
                verbose_name="Visibility date",
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogram",
            name="program_close_date",
            field=models.DateField(
                blank=True,
                help_text="Last day program can be added to home.",
                null=True,
                verbose_name="Close date",
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogram",
            name="program_end_date",
            field=models.DateField(
                blank=True,
                help_text="Last day program can be certified.",
                null=True,
                verbose_name="End date",
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogram",
            name="program_start_date",
            field=models.DateField(
                default=datetime.date.today,
                help_text="First date a program can be submitted for certification.",
                verbose_name="Start date",
            ),
        ),
        migrations.AlterField(
            model_name="historicaleepprogram",
            name="program_visibility_date",
            field=models.DateField(
                default=datetime.date.today,
                help_text="Date program is available for use on a home.",
                verbose_name="Visibility date",
            ),
        ),
    ]
