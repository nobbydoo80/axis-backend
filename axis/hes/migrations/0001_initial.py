# Generated by Django 1.11.26 on 2019-11-24 19:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("home", "0010_validationdata_remove"),
        ("company", "0004_auto_20190826_2024"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("remrate_data", "0009_auto_20190725_1619"),
    ]

    operations = [
        migrations.CreateModel(
            name="HESSimulation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "orientation",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("north", "North"),
                            ("east", "East"),
                            ("south", "South"),
                            ("west", "West"),
                        ],
                        max_length=64,
                        null=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "New (Not Dispatched for Simulation)"),
                            ("uploaded", "Uploaded HPXML to HES API"),
                            ("reported", "Simulated (Reports available)"),
                            ("active", "Active (Results obtained)"),
                            ("stale", "Stale (updating pending)"),
                            ("failed", "Failed"),
                        ],
                        default="new",
                        max_length=32,
                    ),
                ),
                ("error", models.TextField(blank=True, null=True)),
                ("building_id", models.CharField(blank=True, max_length=64, null=True)),
                ("address", models.CharField(blank=True, max_length=128, null=True)),
                ("city", models.CharField(blank=True, max_length=32, null=True)),
                ("state", models.CharField(blank=True, max_length=4, null=True)),
                ("zip_code", models.CharField(blank=True, max_length=16, null=True)),
                ("conditioned_floor_area", models.IntegerField(blank=True, null=True)),
                ("year_built", models.CharField(blank=True, max_length=16, null=True)),
                ("cooling_present", models.BooleanField(null=True)),
                ("base_score", models.IntegerField(blank=True, null=True)),
                ("package_score", models.IntegerField(blank=True, null=True)),
                ("cost_savings", models.FloatField(blank=True, null=True)),
                (
                    "assessment_type",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                ("assessment_date", models.DateField(blank=True, null=True)),
                (
                    "label_number",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                (
                    "qualified_assessor_id",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                (
                    "hescore_version",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                ("utility_electric", models.FloatField(blank=True, null=True)),
                ("utility_natural_gas", models.FloatField(blank=True, null=True)),
                ("utility_fuel_oil", models.FloatField(blank=True, null=True)),
                ("utility_lpg", models.FloatField(blank=True, null=True)),
                ("utility_cord_wood", models.FloatField(blank=True, null=True)),
                ("utility_pellet_wood", models.FloatField(blank=True, null=True)),
                ("utility_generated", models.FloatField(blank=True, null=True)),
                ("source_energy_total_base", models.FloatField(blank=True, null=True)),
                ("source_energy_asset_base", models.FloatField(blank=True, null=True)),
                ("average_state_cost", models.FloatField(blank=True, null=True)),
                ("average_state_eui", models.FloatField(blank=True, null=True)),
                (
                    "weather_station_location",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                ("create_label_date", models.DateField(blank=True, null=True)),
                (
                    "source_energy_total_package",
                    models.FloatField(blank=True, null=True),
                ),
                (
                    "source_energy_asset_package",
                    models.FloatField(blank=True, null=True),
                ),
                ("base_cost", models.FloatField(blank=True, null=True)),
                ("package_cost", models.FloatField(blank=True, null=True)),
                ("site_energy_base", models.FloatField(blank=True, null=True)),
                ("site_energy_package", models.FloatField(blank=True, null=True)),
                ("site_eui_base", models.FloatField(blank=True, null=True)),
                ("site_eui_package", models.FloatField(blank=True, null=True)),
                ("source_eui_base", models.FloatField(blank=True, null=True)),
                ("source_eui_package", models.FloatField(blank=True, null=True)),
                ("carbon_base", models.FloatField(blank=True, null=True)),
                ("carbon_package", models.FloatField(blank=True, null=True)),
                ("utility_electric_base", models.FloatField(blank=True, null=True)),
                ("utility_electric_package", models.FloatField(blank=True, null=True)),
                ("utility_natural_gas_base", models.FloatField(blank=True, null=True)),
                (
                    "utility_natural_gas_package",
                    models.FloatField(blank=True, null=True),
                ),
                ("utility_fuel_oil_base", models.FloatField(blank=True, null=True)),
                ("utility_fuel_oil_package", models.FloatField(blank=True, null=True)),
                ("utility_lpg_base", models.FloatField(blank=True, null=True)),
                ("utility_lpg_package", models.FloatField(blank=True, null=True)),
                ("utility_cord_wood_base", models.FloatField(blank=True, null=True)),
                ("utility_cord_wood_package", models.FloatField(blank=True, null=True)),
                ("utility_pellet_wood_base", models.FloatField(blank=True, null=True)),
                (
                    "utility_pellet_wood_package",
                    models.FloatField(blank=True, null=True),
                ),
                ("utility_generated_base", models.FloatField(blank=True, null=True)),
                ("utility_generated_package", models.FloatField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hes_simulations",
                        to="company.Company",
                    ),
                ),
                (
                    "home_status",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hes_simulations",
                        to="home.EEPProgramHomeStatus",
                    ),
                ),
                (
                    "rem_simulation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hes_simulations",
                        to="remrate_data.Simulation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HESSimulationStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_certified", models.BooleanField(default=False)),
                ("building_id", models.CharField(blank=True, max_length=64, null=True)),
                ("state_changed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "Calculation Requested"),
                            ("north", "North In-Progress"),
                            ("south", "South In-Progress"),
                            ("east", "East In-Progress"),
                            ("west", "West In-Progress"),
                            ("complete", "Complete"),
                        ],
                        default="new",
                        max_length=32,
                    ),
                ),
                (
                    "worst_case_orientation",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("north", "North"),
                            ("east", "East"),
                            ("south", "South"),
                            ("west", "West"),
                        ],
                        max_length=64,
                        null=True,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hes_score_statuses",
                        to="company.Company",
                    ),
                ),
                (
                    "east_orientation",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="east_status",
                        to="hes.HESSimulation",
                    ),
                ),
                (
                    "home_status",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hes_score_statuses",
                        to="home.EEPProgramHomeStatus",
                    ),
                ),
                (
                    "hpxml",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hpxml.HPXMLConversion",
                    ),
                ),
                (
                    "north_orientation",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="north_status",
                        to="hes.HESSimulation",
                    ),
                ),
                (
                    "rem_simulation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hes_score_statuses",
                        to="remrate_data.Simulation",
                    ),
                ),
                (
                    "south_orientation",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="south_status",
                        to="hes.HESSimulation",
                    ),
                ),
                (
                    "west_orientation",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="west_status",
                        to="hes.HESSimulation",
                    ),
                ),
                (
                    "worst_case_simulation",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="worst_case_status",
                        to="hes.HESSimulation",
                    ),
                ),
            ],
            options={"verbose_name": "HES Simulation"},
        ),
        migrations.CreateModel(
            name="HistoricalHESSimulation",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "orientation",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("north", "North"),
                            ("east", "East"),
                            ("south", "South"),
                            ("west", "West"),
                        ],
                        max_length=64,
                        null=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "New (Not Dispatched for Simulation)"),
                            ("uploaded", "Uploaded HPXML to HES API"),
                            ("reported", "Simulated (Reports available)"),
                            ("active", "Active (Results obtained)"),
                            ("stale", "Stale (updating pending)"),
                            ("failed", "Failed"),
                        ],
                        default="new",
                        max_length=32,
                    ),
                ),
                ("error", models.TextField(blank=True, null=True)),
                ("building_id", models.CharField(blank=True, max_length=64, null=True)),
                ("address", models.CharField(blank=True, max_length=128, null=True)),
                ("city", models.CharField(blank=True, max_length=32, null=True)),
                ("state", models.CharField(blank=True, max_length=4, null=True)),
                ("zip_code", models.CharField(blank=True, max_length=16, null=True)),
                ("conditioned_floor_area", models.IntegerField(blank=True, null=True)),
                ("year_built", models.CharField(blank=True, max_length=16, null=True)),
                ("cooling_present", models.BooleanField(null=True)),
                ("base_score", models.IntegerField(blank=True, null=True)),
                ("package_score", models.IntegerField(blank=True, null=True)),
                ("cost_savings", models.FloatField(blank=True, null=True)),
                (
                    "assessment_type",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                ("assessment_date", models.DateField(blank=True, null=True)),
                (
                    "label_number",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                (
                    "qualified_assessor_id",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                (
                    "hescore_version",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                ("utility_electric", models.FloatField(blank=True, null=True)),
                ("utility_natural_gas", models.FloatField(blank=True, null=True)),
                ("utility_fuel_oil", models.FloatField(blank=True, null=True)),
                ("utility_lpg", models.FloatField(blank=True, null=True)),
                ("utility_cord_wood", models.FloatField(blank=True, null=True)),
                ("utility_pellet_wood", models.FloatField(blank=True, null=True)),
                ("utility_generated", models.FloatField(blank=True, null=True)),
                ("source_energy_total_base", models.FloatField(blank=True, null=True)),
                ("source_energy_asset_base", models.FloatField(blank=True, null=True)),
                ("average_state_cost", models.FloatField(blank=True, null=True)),
                ("average_state_eui", models.FloatField(blank=True, null=True)),
                (
                    "weather_station_location",
                    models.CharField(blank=True, max_length=32, null=True),
                ),
                ("create_label_date", models.DateField(blank=True, null=True)),
                (
                    "source_energy_total_package",
                    models.FloatField(blank=True, null=True),
                ),
                (
                    "source_energy_asset_package",
                    models.FloatField(blank=True, null=True),
                ),
                ("base_cost", models.FloatField(blank=True, null=True)),
                ("package_cost", models.FloatField(blank=True, null=True)),
                ("site_energy_base", models.FloatField(blank=True, null=True)),
                ("site_energy_package", models.FloatField(blank=True, null=True)),
                ("site_eui_base", models.FloatField(blank=True, null=True)),
                ("site_eui_package", models.FloatField(blank=True, null=True)),
                ("source_eui_base", models.FloatField(blank=True, null=True)),
                ("source_eui_package", models.FloatField(blank=True, null=True)),
                ("carbon_base", models.FloatField(blank=True, null=True)),
                ("carbon_package", models.FloatField(blank=True, null=True)),
                ("utility_electric_base", models.FloatField(blank=True, null=True)),
                ("utility_electric_package", models.FloatField(blank=True, null=True)),
                ("utility_natural_gas_base", models.FloatField(blank=True, null=True)),
                (
                    "utility_natural_gas_package",
                    models.FloatField(blank=True, null=True),
                ),
                ("utility_fuel_oil_base", models.FloatField(blank=True, null=True)),
                ("utility_fuel_oil_package", models.FloatField(blank=True, null=True)),
                ("utility_lpg_base", models.FloatField(blank=True, null=True)),
                ("utility_lpg_package", models.FloatField(blank=True, null=True)),
                ("utility_cord_wood_base", models.FloatField(blank=True, null=True)),
                ("utility_cord_wood_package", models.FloatField(blank=True, null=True)),
                ("utility_pellet_wood_base", models.FloatField(blank=True, null=True)),
                (
                    "utility_pellet_wood_package",
                    models.FloatField(blank=True, null=True),
                ),
                ("utility_generated_base", models.FloatField(blank=True, null=True)),
                ("utility_generated_package", models.FloatField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField()),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "company",
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
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "home_status",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="home.EEPProgramHomeStatus",
                    ),
                ),
                (
                    "rem_simulation",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="remrate_data.Simulation",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical hes simulation",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalHESSimulationStatus",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("is_certified", models.BooleanField(default=False)),
                ("building_id", models.CharField(blank=True, max_length=64, null=True)),
                ("state_changed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "Calculation Requested"),
                            ("north", "North In-Progress"),
                            ("south", "South In-Progress"),
                            ("east", "East In-Progress"),
                            ("west", "West In-Progress"),
                            ("complete", "Complete"),
                        ],
                        default="new",
                        max_length=32,
                    ),
                ),
                (
                    "worst_case_orientation",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("north", "North"),
                            ("east", "East"),
                            ("south", "South"),
                            ("west", "West"),
                        ],
                        max_length=64,
                        null=True,
                    ),
                ),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField()),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "company",
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
                    "east_orientation",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="hes.HESSimulation",
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
                    "home_status",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="home.EEPProgramHomeStatus",
                    ),
                ),
                (
                    "hpxml",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="hpxml.HPXMLConversion",
                    ),
                ),
                (
                    "north_orientation",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="hes.HESSimulation",
                    ),
                ),
                (
                    "rem_simulation",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="remrate_data.Simulation",
                    ),
                ),
                (
                    "south_orientation",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="hes.HESSimulation",
                    ),
                ),
                (
                    "west_orientation",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="hes.HESSimulation",
                    ),
                ),
                (
                    "worst_case_simulation",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="hes.HESSimulation",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical HES Simulation",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
