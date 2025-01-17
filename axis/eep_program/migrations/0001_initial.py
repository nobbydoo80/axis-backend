# Generated by Django 1.11.16 on 2018-10-08 18:15

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

import simple_history.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("company", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("annotation", "0001_initial"),
        ("certification", "0001_initial"),
        ("checklist", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EEPProgram",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("is_qa_program", models.BooleanField(default=False)),
                ("opt_in", models.BooleanField(default=False)),
                ("workflow_default_settings", models.TextField(default=dict)),
                (
                    "viewable_by_company_type",
                    models.CharField(blank=True, max_length=70, null=True),
                ),
                ("min_hers_score", models.IntegerField(default=0, verbose_name="Min HERs Score")),
                ("max_hers_score", models.IntegerField(default=100, verbose_name="Max HERs Score")),
                (
                    "per_point_adder",
                    models.DecimalField(
                        decimal_places=2, default=0.0, max_digits=10, verbose_name="Per/Point Adder"
                    ),
                ),
                (
                    "builder_incentive_dollar_value",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=10,
                        verbose_name="Builder Incentive",
                    ),
                ),
                (
                    "rater_incentive_dollar_value",
                    models.DecimalField(
                        decimal_places=2, default=0.0, max_digits=10, verbose_name="Rater Incentive"
                    ),
                ),
                ("enable_standard_disclosure", models.BooleanField(default=False)),
                ("require_floorplan_approval", models.BooleanField(default=False)),
                ("comment", models.TextField(blank=True)),
                (
                    "require_input_data",
                    models.BooleanField(
                        default=True, verbose_name="Require at least one kind of input data"
                    ),
                ),
                (
                    "require_rem_data",
                    models.BooleanField(default=True, verbose_name="Require REM/Rate\u2122 Data"),
                ),
                (
                    "require_model_file",
                    models.BooleanField(
                        default=False, verbose_name="Require REM/Rate\u2122 Model File"
                    ),
                ),
                (
                    "require_ekotrope_data",
                    models.BooleanField(default=False, verbose_name="Require Ekotrope Data"),
                ),
                (
                    "allow_rem_input",
                    models.BooleanField(
                        default=True, verbose_name="Enable REM/Rate\u2122 attachments"
                    ),
                ),
                (
                    "allow_ekotrope_input",
                    models.BooleanField(default=False, verbose_name="Enable Ekotrope attachments"),
                ),
                (
                    "manual_transition_on_certify",
                    models.BooleanField(
                        default=False, verbose_name="Manually transition to certified state"
                    ),
                ),
                ("require_builder_epa_is_active", models.BooleanField(default=False)),
                ("require_rater_epa_is_active", models.BooleanField(default=False)),
                ("require_rater_of_record", models.BooleanField(default=False)),
                ("require_builder_relationship", models.BooleanField(default=True)),
                ("require_builder_assigned_to_home", models.BooleanField(default=True)),
                ("require_hvac_relationship", models.BooleanField(default=False)),
                ("require_hvac_assigned_to_home", models.BooleanField(default=False)),
                ("require_utility_relationship", models.BooleanField(default=False)),
                ("require_utility_assigned_to_home", models.BooleanField(default=False)),
                ("require_rater_relationship", models.BooleanField(default=False)),
                ("require_rater_assigned_to_home", models.BooleanField(default=False)),
                ("require_provider_relationship", models.BooleanField(default=False)),
                ("require_provider_assigned_to_home", models.BooleanField(default=False)),
                ("require_qa_relationship", models.BooleanField(default=False)),
                ("require_qa_assigned_to_home", models.BooleanField(default=False)),
                ("allow_sampling", models.BooleanField(default=True)),
                ("allow_metro_sampling", models.BooleanField(default=True)),
                ("require_resnet_sampling_provider", models.BooleanField(default=False)),
                ("is_legacy", models.BooleanField(default=False)),
                ("is_public", models.BooleanField(default=False)),
                (
                    "program_visibility_date",
                    models.DateField(default=datetime.date.today, verbose_name="Visibility date"),
                ),
                (
                    "program_start_date",
                    models.DateField(default=datetime.date.today, verbose_name="Start date"),
                ),
                (
                    "program_close_date",
                    models.DateField(blank=True, null=True, verbose_name="Close date"),
                ),
                (
                    "program_end_date",
                    models.DateField(blank=True, null=True, verbose_name="End date"),
                ),
                (
                    "program_close_warning_date",
                    models.DateField(blank=True, null=True, verbose_name="Close warning date"),
                ),
                ("program_close_warning", models.TextField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("slug", models.SlugField(unique=True)),
                (
                    "certifiable_by",
                    models.ManyToManyField(
                        blank=True, related_name="eep_programs_can_certify", to="company.Company"
                    ),
                ),
                (
                    "opt_in_out_list",
                    models.ManyToManyField(
                        blank=True,
                        related_name="eep_programs_opted_in_out_of",
                        to="company.Company",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="company.Company",
                    ),
                ),
                (
                    "required_annotation_types",
                    models.ManyToManyField(blank=True, to="annotation.Type"),
                ),
                (
                    "required_checklists",
                    models.ManyToManyField(blank=True, to="checklist.CheckList"),
                ),
                (
                    "workflow",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="certification.Workflow",
                    ),
                ),
            ],
            options={"ordering": ("name",), "verbose_name": "Program"},
        ),
        migrations.CreateModel(
            name="HistoricalEEPProgram",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("is_qa_program", models.BooleanField(default=False)),
                ("opt_in", models.BooleanField(default=False)),
                ("workflow_default_settings", models.TextField(default=dict)),
                (
                    "viewable_by_company_type",
                    models.CharField(blank=True, max_length=70, null=True),
                ),
                ("min_hers_score", models.IntegerField(default=0, verbose_name="Min HERs Score")),
                ("max_hers_score", models.IntegerField(default=100, verbose_name="Max HERs Score")),
                (
                    "per_point_adder",
                    models.DecimalField(
                        decimal_places=2, default=0.0, max_digits=10, verbose_name="Per/Point Adder"
                    ),
                ),
                (
                    "builder_incentive_dollar_value",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=10,
                        verbose_name="Builder Incentive",
                    ),
                ),
                (
                    "rater_incentive_dollar_value",
                    models.DecimalField(
                        decimal_places=2, default=0.0, max_digits=10, verbose_name="Rater Incentive"
                    ),
                ),
                ("enable_standard_disclosure", models.BooleanField(default=False)),
                ("require_floorplan_approval", models.BooleanField(default=False)),
                ("comment", models.TextField(blank=True)),
                (
                    "require_input_data",
                    models.BooleanField(
                        default=True, verbose_name="Require at least one kind of input data"
                    ),
                ),
                (
                    "require_rem_data",
                    models.BooleanField(default=True, verbose_name="Require REM/Rate\u2122 Data"),
                ),
                (
                    "require_model_file",
                    models.BooleanField(
                        default=False, verbose_name="Require REM/Rate\u2122 Model File"
                    ),
                ),
                (
                    "require_ekotrope_data",
                    models.BooleanField(default=False, verbose_name="Require Ekotrope Data"),
                ),
                (
                    "allow_rem_input",
                    models.BooleanField(
                        default=True, verbose_name="Enable REM/Rate\u2122 attachments"
                    ),
                ),
                (
                    "allow_ekotrope_input",
                    models.BooleanField(default=False, verbose_name="Enable Ekotrope attachments"),
                ),
                (
                    "manual_transition_on_certify",
                    models.BooleanField(
                        default=False, verbose_name="Manually transition to certified state"
                    ),
                ),
                ("require_builder_epa_is_active", models.BooleanField(default=False)),
                ("require_rater_epa_is_active", models.BooleanField(default=False)),
                ("require_rater_of_record", models.BooleanField(default=False)),
                ("require_builder_relationship", models.BooleanField(default=True)),
                ("require_builder_assigned_to_home", models.BooleanField(default=True)),
                ("require_hvac_relationship", models.BooleanField(default=False)),
                ("require_hvac_assigned_to_home", models.BooleanField(default=False)),
                ("require_utility_relationship", models.BooleanField(default=False)),
                ("require_utility_assigned_to_home", models.BooleanField(default=False)),
                ("require_rater_relationship", models.BooleanField(default=False)),
                ("require_rater_assigned_to_home", models.BooleanField(default=False)),
                ("require_provider_relationship", models.BooleanField(default=False)),
                ("require_provider_assigned_to_home", models.BooleanField(default=False)),
                ("require_qa_relationship", models.BooleanField(default=False)),
                ("require_qa_assigned_to_home", models.BooleanField(default=False)),
                ("allow_sampling", models.BooleanField(default=True)),
                ("allow_metro_sampling", models.BooleanField(default=True)),
                ("require_resnet_sampling_provider", models.BooleanField(default=False)),
                ("is_legacy", models.BooleanField(default=False)),
                ("is_public", models.BooleanField(default=False)),
                (
                    "program_visibility_date",
                    models.DateField(default=datetime.date.today, verbose_name="Visibility date"),
                ),
                (
                    "program_start_date",
                    models.DateField(default=datetime.date.today, verbose_name="Start date"),
                ),
                (
                    "program_close_date",
                    models.DateField(blank=True, null=True, verbose_name="Close date"),
                ),
                (
                    "program_end_date",
                    models.DateField(blank=True, null=True, verbose_name="End date"),
                ),
                (
                    "program_close_warning_date",
                    models.DateField(blank=True, null=True, verbose_name="Close warning date"),
                ),
                ("program_close_warning", models.TextField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("slug", models.SlugField()),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="company.Company",
                    ),
                ),
                (
                    "workflow",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="certification.Workflow",
                    ),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
                "verbose_name": "historical Program",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name="eepprogram",
            unique_together=set([("name", "owner")]),
        ),
    ]
