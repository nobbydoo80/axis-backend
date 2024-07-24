# Generated by Django 1.11.16 on 2018-10-08 18:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ETOAccount",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "account_number",
                    models.CharField(
                        blank=True, help_text="ETO Account Number", max_length=64, null=True
                    ),
                ),
                (
                    "ccb_number",
                    models.CharField(
                        blank=True,
                        help_text="OR Construction Contractors Board license number",
                        max_length=64,
                        null=True,
                    ),
                ),
            ],
            options={"verbose_name": "ETO Account Number"},
        ),
        migrations.CreateModel(
            name="FastTrackSubmission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "project_id",
                    models.CharField(
                        blank=True,
                        help_text="Project Tracker assigned ID after submission",
                        max_length=20,
                    ),
                ),
                ("eps_score", models.IntegerField(blank=True, null=True)),
                ("eps_score_built_to_code_score", models.IntegerField(blank=True, null=True)),
                ("percent_improvement", models.FloatField(blank=True, null=True)),
                (
                    "builder_incentive",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "rater_incentive",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                ("carbon_score", models.FloatField(blank=True, null=True)),
                ("carbon_built_to_code_score", models.FloatField(blank=True, null=True)),
                (
                    "estimated_annual_energy_costs",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "estimated_monthly_energy_costs",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                ("similar_size_eps_score", models.IntegerField(blank=True, null=True)),
                ("similar_size_carbon_score", models.FloatField(blank=True, null=True)),
                (
                    "builder_gas_incentive",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "builder_electric_incentive",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "rater_gas_incentive",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "rater_electric_incentive",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "therm_savings",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "kwh_savings",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "mbtu_savings",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "eps_calculator_version",
                    models.DateField(
                        blank=True, null=True, verbose_name="EPS Calculator Version Date"
                    ),
                ),
            ],
            options={
                "verbose_name": "ProjectTracking Submission",
            },
        ),
        migrations.CreateModel(
            name="HistoricalFastTrackSubmission",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "project_id",
                    models.CharField(
                        blank=True,
                        help_text="Project Tracker assigned ID after submission",
                        max_length=20,
                    ),
                ),
                ("eps_score", models.IntegerField(blank=True, null=True)),
                ("eps_score_built_to_code_score", models.IntegerField(blank=True, null=True)),
                ("percent_improvement", models.FloatField(blank=True, null=True)),
                (
                    "builder_incentive",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "rater_incentive",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                ("carbon_score", models.FloatField(blank=True, null=True)),
                ("carbon_built_to_code_score", models.FloatField(blank=True, null=True)),
                (
                    "estimated_annual_energy_costs",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "estimated_monthly_energy_costs",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                ("similar_size_eps_score", models.IntegerField(blank=True, null=True)),
                ("similar_size_carbon_score", models.FloatField(blank=True, null=True)),
                (
                    "builder_gas_incentive",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "builder_electric_incentive",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "rater_gas_incentive",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "rater_electric_incentive",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "therm_savings",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "kwh_savings",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "mbtu_savings",
                    models.DecimalField(
                        blank=True, decimal_places=2, default=0, max_digits=8, null=True
                    ),
                ),
                (
                    "eps_calculator_version",
                    models.DateField(
                        blank=True, null=True, verbose_name="EPS Calculator Version Date"
                    ),
                ),
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
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
                "verbose_name": "historical ProjectTracking Submission",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
