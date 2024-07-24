"""models.py: Django customer_eto"""


import datetime
import logging
from decimal import Decimal
from functools import cached_property, lru_cache

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.forms.models import model_to_dict
from django.urls import reverse
from simple_history.models import HistoricalRecords

from axis.core.fields import AxisJSONField
from axis.filehandling.utils import render_customer_document_from_template
from . import managers, strings
from .enumerations import ProjectTrackerSubmissionStatus, PrimaryHeatingEquipment2020, HeatType

__author__ = "Steven Klass"
__date__ = "9/4/13 10:20 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = ["Steven Klass"]

from .managers import ETOAccountQuerySet

log = logging.getLogger(__name__)
User = get_user_model()
app = apps.get_app_config("customer_eto")


class ETOAccount(models.Model):
    """Basic Account number support for ETO Companies"""

    company = models.OneToOneField(
        "company.Company", on_delete=models.CASCADE, related_name="eto_account"
    )
    account_number = models.CharField(
        max_length=64, help_text="ETO Account Number", blank=True, null=True
    )
    ccb_number = models.CharField(
        max_length=64,
        help_text="OR Construction Contractors Board license number",
        blank=True,
        null=True,
    )

    objects = ETOAccountQuerySet.as_manager()

    class Meta:
        verbose_name = "ETO Account Number"

    def can_be_edited(self, user):
        return self.company.show_ccb_number(user) or self.company.show_eto_account(user)


class FastTrackSubmission(models.Model):
    objects = managers.FastTrackSubmissionManager()

    home_status = models.OneToOneField("home.EEPProgramHomeStatus", on_delete=models.CASCADE)
    project_id = models.CharField(
        max_length=20,
        blank=True,
        help_text="ENH Project ID",
    )

    solar_project_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="SLE Project ID",
    )

    # These are the calculated values at the time of submission.
    eps_score = models.IntegerField(blank=True, null=True)
    eps_score_built_to_code_score = models.IntegerField(blank=True, null=True)
    percent_improvement = models.FloatField(blank=True, null=True)
    percent_improvement_kwh = models.FloatField(blank=True, null=True)
    percent_improvement_therms = models.FloatField(blank=True, null=True)

    builder_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True, null=True
    )
    rater_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True, null=True
    )

    carbon_score = models.FloatField(blank=True, null=True)
    carbon_built_to_code_score = models.FloatField(blank=True, null=True)

    estimated_annual_energy_costs = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True, null=True
    )
    estimated_monthly_energy_costs = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True, null=True
    )
    # New for 2022
    estimated_annual_energy_costs_code = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True, null=True
    )
    estimated_monthly_energy_costs_code = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True, null=True
    )

    similar_size_eps_score = models.IntegerField(blank=True, null=True)
    similar_size_carbon_score = models.FloatField(blank=True, null=True)

    builder_gas_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True, null=True
    )
    builder_electric_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True, null=True
    )

    rater_gas_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True, null=True
    )
    rater_electric_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True, null=True
    )

    therm_savings = models.FloatField(default=0.0, blank=True, null=True)
    kwh_savings = models.FloatField(default=0.0, blank=True, null=True)
    mbtu_savings = models.FloatField(default=0.0, blank=True, null=True)

    original_therm_savings = models.FloatField(default=0.0, blank=True, null=True)
    original_kwh_savings = models.FloatField(default=0.0, blank=True, null=True)
    original_mbtu_savings = models.FloatField(default=0.0, blank=True, null=True)

    eps_calculator_version = models.DateField(
        verbose_name="EPS Calculator Version Date", null=True, blank=True
    )

    original_builder_electric_incentive = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    original_builder_gas_incentive = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    original_builder_incentive = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )

    original_rater_electric_incentive = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    original_rater_gas_incentive = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    original_rater_incentive = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )

    payment_change_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    payment_change_datetime = models.DateTimeField(blank=True, null=True)
    payment_revision_comment = models.TextField(
        verbose_name="Payment change comment", blank=True, null=True
    )

    net_zero_eps_incentive = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        blank=True,
        help_text="Net Zero EPS Incentive",
    )
    energy_smart_homes_eps_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True
    )
    net_zero_solar_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True
    )
    energy_smart_homes_solar_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True
    )

    original_net_zero_eps_incentive = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        blank=True,
        help_text="Net Zero EPS Incentive",
    )
    original_energy_smart_homes_eps_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True
    )
    original_net_zero_solar_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True
    )
    original_energy_smart_homes_solar_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True
    )
    # EPS Report Fields
    electric_cost_per_month = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    natural_gas_cost_per_month = models.DecimalField(default=0, max_digits=8, decimal_places=2)

    improved_total_kwh = models.FloatField(default=0.0)
    improved_total_therms = models.FloatField(default=0.0)

    solar_hot_water_kwh = models.FloatField(default=0.0)
    solar_hot_water_therms = models.FloatField(default=0.0)

    pv_kwh = models.FloatField(default=0.0)
    percent_generation_kwh = models.FloatField(default=0.0)

    projected_carbon_consumption_electric = models.FloatField(default=0.0)
    projected_carbon_consumption_natural_gas = models.FloatField(default=0.0)

    # Washington Code Credits Program
    required_credits_to_meet_code = models.FloatField(default=0.0, help_text="WA Code Credits")
    achieved_total_credits = models.FloatField(default=0.0)
    eligible_gas_points = models.FloatField(default=0.0)
    code_credit_incentive = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    thermostat_incentive = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    fireplace_incentive = models.DecimalField(default=0, max_digits=8, decimal_places=2)

    # ETO 2022
    solar_ready_builder_incentive = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    solar_ready_verifier_incentive = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    ev_ready_builder_incentive = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    solar_storage_builder_incentive = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    heat_pump_water_heater_incentive = models.DecimalField(
        default=0, max_digits=8, decimal_places=2
    )

    cobid_builder_incentive = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    cobid_verifier_incentive = models.DecimalField(default=0, max_digits=8, decimal_places=2)

    # Fire Rebuild Program
    triple_pane_window_incentive = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    rigid_insulation_incentive = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    sealed_attic_incentive = models.DecimalField(default=0, max_digits=8, decimal_places=2)

    submit_user = models.ForeignKey(
        "core.User", on_delete=models.SET_NULL, blank=True, null=True, related_name="pt_submissions"
    )
    submit_status = models.CharField(
        max_length=50, choices=ProjectTrackerSubmissionStatus.choices, null=True, blank=True
    )
    solar_submit_status = models.CharField(
        max_length=50, choices=ProjectTrackerSubmissionStatus.choices, null=True, blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    submission_count = models.IntegerField(blank=True, null=True, default=0)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "ProjectTracking Submission"
        ordering = ("id",)

    def __str__(self):
        msg = "ProjectTracker:"
        if self.is_locked():
            project_types = self.get_project_types()
            if "ENH" in project_types:
                msg += " ENH:"
                if self.project_id:
                    msg += f" {self.project_id}"
                else:
                    msg += f" {self.get_submit_status_display()}"
            if "SLE" in project_types:
                msg += " SLE:"
                if self.solar_project_id:
                    msg += f" {self.solar_project_id}"
                else:
                    msg += f" {self.get_solar_submit_status_display()}"
        else:
            msg += f" Not Locked: EPS ({self.eps_score})"
        return msg

    def get_absolute_url(self) -> str:
        return reverse("api_v3:project_tracker-xml", kwargs={"pk": self.home_status_id})

    def is_locked(self) -> bool:
        return bool(
            self.home_status.state == "complete"
            and self.home_status.certification_date
            and self.eps_score is not None
        )

    def get_project_types(self) -> list:
        """Returns the available project types"""
        project_types = ["ENH"]
        if any(
            (
                self.net_zero_solar_incentive,  # EPSNZ
                self.solar_storage_builder_incentive,  # EPSESH
                self.solar_ready_builder_incentive,  # SOLRDYCON,
                self.solar_ready_verifier_incentive,  # SOLRDYCON,
            )
        ):
            project_types.append("SLE")
        return project_types

    def get_project_id(self) -> str:
        if "ENH" not in self.get_project_types():
            return "N/A"
        return self.project_id or ""

    def get_solar_project_id(self) -> str:
        if "SLE" not in self.get_project_types():
            return "N/A"
        return self.solar_project_id or ""

    def can_be_sent_to_fastrack(self) -> bool:
        project_types = self.get_project_types()
        if "ENH" in project_types:
            if self.submit_status in [
                ProjectTrackerSubmissionStatus.SUBMITTED,
                ProjectTrackerSubmissionStatus.PENDING,
                ProjectTrackerSubmissionStatus.SUCCESS,
            ]:
                return False
            if self.project_id:
                return False
        if "SLE" in project_types:
            if self.solar_submit_status in [
                ProjectTrackerSubmissionStatus.SUBMITTED,
                ProjectTrackerSubmissionStatus.PENDING,
                ProjectTrackerSubmissionStatus.SUCCESS,
            ]:
                return False
            if self.solar_project_id:
                return False
        return self.is_locked()

    def can_payment_be_updated(self, user) -> bool:
        if user.company.slug in ["eto", "peci"] or user.is_superuser:
            return (
                user.has_perm("customer_eto.change_fasttracksubmission")
                and self.home_status.certification_date
            )
        return False

    @cached_property
    def estimated_annual_energy_savings_cost(self) -> Decimal:
        """New for 2022 we store the code costs.  This allows us to pull the annual savings"""
        return max(
            [
                Decimal(0.0),
                self.estimated_annual_energy_costs_code - self.estimated_annual_energy_costs,
            ]
        )

    @cached_property
    def _checklist_answers(self) -> dict:
        home_status = self.home_status
        context = {"user__company": home_status.company}
        from axis.checklist.collection.excel import ExcelChecklistCollector

        collector = ExcelChecklistCollector(home_status.collection_request, **context)
        instrument_lookup = collector.get_instruments()
        return {i.measure_id: collector.get_data_display(i) for i in instrument_lookup}

    @cached_property
    def heat_type(self) -> HeatType:
        primary_heating_class = self._checklist_answers["primary-heating-equipment-type"]
        if primary_heating_class in [
            PrimaryHeatingEquipment2020.GAS_FIREPLACE.value,
            PrimaryHeatingEquipment2020.GAS_UNIT_HEATER.value,
            PrimaryHeatingEquipment2020.GAS_FURNACE.value,
            PrimaryHeatingEquipment2020.GAS_BOILER.value,
            PrimaryHeatingEquipment2020.OTHER_GAS.value,
        ]:
            return HeatType.GAS
        if primary_heating_class is not None:
            return HeatType.ELECTRIC

    @cached_property
    def _heat_pump_allocation_pct(self) -> Decimal:
        if self.heat_pump_water_heater_incentive:
            return self.builder_electric_incentive / (
                self.builder_electric_incentive + self.builder_gas_incentive
            )
        return Decimal("0.0")

    @cached_property
    def builder_heat_pump_water_heater_electric_incentive(self) -> Decimal:
        value = self._heat_pump_allocation_pct * self.heat_pump_water_heater_incentive
        return Decimal(round(value, 0))

    @cached_property
    def builder_heat_pump_water_heater_gas_incentive(self) -> Decimal:
        value = (
            self.heat_pump_water_heater_incentive
            - self.builder_heat_pump_water_heater_electric_incentive
        )
        return Decimal(round(value, 0))

    @cached_property
    def builder_electric_baseline_incentive(self) -> Decimal:
        value = (
            self.builder_electric_incentive
            - self.ev_ready_builder_incentive
            - self.builder_heat_pump_water_heater_electric_incentive
        )
        if self.heat_type == HeatType.ELECTRIC:
            value -= self.cobid_builder_incentive
            value -= self.triple_pane_window_incentive
            value -= self.rigid_insulation_incentive
            value -= self.sealed_attic_incentive
        return max([Decimal("0.0"), value])

    @cached_property
    def builder_gas_baseline_incentive(self) -> Decimal:
        value = self.builder_gas_incentive - self.builder_heat_pump_water_heater_gas_incentive
        if self.heat_type == HeatType.GAS:
            value -= self.cobid_builder_incentive
            value -= self.triple_pane_window_incentive
            value -= self.rigid_insulation_incentive
            value -= self.sealed_attic_incentive
        return max([Decimal("0.0"), value])

    @cached_property
    def total_builder_sle_incentive(self) -> Decimal:
        return (
            self.net_zero_solar_incentive
            + self.solar_ready_builder_incentive
            + self.solar_storage_builder_incentive
        )

    @cached_property
    def total_builder_incentive(self) -> Decimal:
        return max(
            [
                Decimal("0.0"),
                (
                    self.builder_electric_incentive
                    + self.builder_gas_incentive
                    + self.total_builder_sle_incentive
                ),
            ]
        )

    @cached_property
    def rater_electric_baseline_incentive(self) -> Decimal:
        value = self.rater_electric_incentive
        if self.heat_type == HeatType.ELECTRIC:
            value -= self.cobid_verifier_incentive
        return value

    @cached_property
    def rater_gas_baseline_incentive(self) -> Decimal:
        value = self.rater_gas_incentive
        if self.heat_type == HeatType.GAS:
            value -= self.cobid_verifier_incentive
        return value

    @cached_property
    def total_rater_sle_incentive(self) -> Decimal:
        return self.solar_ready_verifier_incentive

    @cached_property
    def total_rater_incentive(self) -> Decimal:
        return (
            self.rater_electric_incentive
            + self.rater_gas_incentive
            + self.total_rater_sle_incentive
        )


class PermitAndOccupancySettings(models.Model):
    """ETO Building Permit and Certificate of Occupancy data.

    This model can be assigned by setting one of the available ForeignKeys to create a
    contextual tier of its use, where more specific tiers can override the broader ones.
    """

    objects = managers.PermitAndOccupancySettingsQuerySet.as_manager()

    owner = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="ownedpermitandoccupancy_set",
    )

    # Exactly one of these three FKs must be set
    company = models.ForeignKey("company.Company", on_delete=models.CASCADE, blank=True, null=True)
    subdivision = models.ForeignKey(
        "subdivision.Subdivision", on_delete=models.CASCADE, blank=True, null=True
    )
    home = models.ForeignKey("home.Home", on_delete=models.CASCADE, blank=True, null=True)

    data = AxisJSONField(default=dict)
    signed_building_permit = models.ForeignKey(
        "filehandling.CustomerDocument",
        related_name="+",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    signed_certificate_of_occupancy = models.ForeignKey(
        "filehandling.CustomerDocument",
        related_name="+",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    # Data fields
    reeds_crossing_compliance_option = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=strings.REEDS_CROSSING_COMPLIANCE_CHOICES,
    )
    rosedale_parks_compliance_option = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=strings.ROSEDALE_PARKS_COMPLIANCE_CHOICES,
    )

    HEADERS = {}

    class Meta:
        unique_together = (
            ("owner", "company"),
            ("owner", "subdivision"),
            ("owner", "home"),
        )

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        """Enforce one of the required FKs before super()."""

        if not any((self.company, self.subdivision, self.home)):
            raise ValueError("Need one of 'company', 'subdivision', 'home' set.")
        super(PermitAndOccupancySettings, self).save(*args, **kwargs)

    def as_dict(self, raw_values=True, display_values=False):
        """Return field values, either directly or as `get_FOO_display()` values."""

        raw = model_to_dict(self)
        display = {}

        if display_values:
            for k in raw:
                full_key = k
                if raw_values:  # When both are true, differentiate keys to avoid overlap
                    full_key += "_display"

                getter_name = "get_{field}_display".format(field=k)
                if hasattr(self, getter_name):
                    if self.company and raw[k] is None:
                        display[full_key] = "Not set"
                    else:
                        display[full_key] = getattr(self, getter_name)()

        data = {}
        if raw_values:
            data.update(raw)
        if display_values:
            data.update(display)
        return data

    def should_get_latest_docusign_status(self, data_name="building_permit", now=None):
        """Return true if we need to poll.  We used to poll for everything but we can't as
        we hit API limits this backs off the the time we hit to the following schedule
        > 45 days we don't consider it
        30 days - 45 days - 1/wk
        7 days - 30 days - 1/day
        24 hours - 7 days - 2/day
        < 24 hours - every 3 hours
        """
        if data_name not in self.data:
            return True

        if (
            "latest_result" not in self.data[data_name]
            or "source" not in self.data[data_name]["latest_result"]
        ):
            return True

        if self.data[data_name]["latest_result"].get("status") in [
            "completed",
            "voided",
        ]:
            return False

        # Default string for sentDateTime
        default_sent = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") + "0Z"

        # Add this if we don't have it as we need somethimg to compare to.
        initial = self.data[data_name].get("initial_request_date")
        if initial is None:
            self.data[data_name].update({"initial_request_date": default_sent})
            self.save()
            self.refresh_from_db()
            initial = default_sent

        initial = datetime.datetime.strptime(initial[:-2], "%Y-%m-%dT%H:%M:%S.%f").replace(
            tzinfo=datetime.timezone.utc
        )
        last = self.data[data_name]["latest_result"]["source"].get("sentDateTime", default_sent)
        last = datetime.datetime.strptime(last[:-2], "%Y-%m-%dT%H:%M:%S.%f").replace(
            tzinfo=datetime.timezone.utc
        )

        if now is None:
            now = datetime.datetime.now(datetime.timezone.utc)
        # If more than 45 days stop
        if now - initial > datetime.timedelta(hours=24 * 45):
            return False
        # Between 30 days and 45 days 1/week
        if now - initial > datetime.timedelta(hours=24 * 30):
            # More than 30 days 1 per week
            if now - last > datetime.timedelta(hours=24 * 7):
                return True
            return False
        # Between 7 days and 30 days 1/day
        if now - initial > datetime.timedelta(hours=24 * 7):
            # More that 7 days 1 per day
            if now - last > datetime.timedelta(hours=24):
                return True
            return False
        # Between 1 days and 7 days 2/day
        if now - initial > datetime.timedelta(hours=24):
            # More than 24 hours but < 7 days 2 per day
            if now - last > datetime.timedelta(hours=12):
                return True
            return False
        # For under 24 hours check every 3 hours
        if now - last > datetime.timedelta(hours=3):
            return True
        return False

    def post_building_permit(self, user):
        """Render fields onto the community's PDF template and store on docusign."""

        from .docusign import BuildingPermit
        from .utils import populate_building_permit_template

        if self.signed_building_permit:
            raise ValueError("Signing is already done for Builder Permit.")
        elif self.data.setdefault("building_permit", {}).get("envelope_id"):
            if self.home.customer_documents.filter(description=app.PERMIT_DESCRIPTION):
                raise ValueError("Signing is already started.")

        signer = self.get_building_permit_signer()
        if signer is None:
            msg = "No user associated with %s authorized for signatures"
            raise ValueError(msg % self.home.get_builder())

        filename = "Building Permit Report - {company}.pdf".format(company=user.company)
        description = app.PERMIT_DESCRIPTION

        customer_document = render_customer_document_from_template(
            self.home,
            filename,
            description,
            owner=user.company,
            f_populate=populate_building_permit_template,
            user=user,
        )
        document_obj = BuildingPermit()
        envelope = document_obj.create_envelope(
            customer_document,
            user=signer,
            company=user.company,
            address=self.home.get_addr(include_city_state_zip=True, company=user.company),
        )
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") + "0Z"
        self.data.update(
            {
                "building_permit": {
                    "envelope_id": envelope["envelopeId"],
                    "request_user": user.pk,
                    "initial_request_date": now,
                }
            }
        )
        self.save(update_fields=["data"])

    def post_certificate_of_occupancy(self, user):
        """Render fields onto the community's PDF template and store on docusign."""

        from .docusign import CertificateOfOccupancy
        from .utils import populate_certificate_of_occupancy_template

        if self.signed_certificate_of_occupancy:
            raise ValueError("Signing is already for COO.")
        elif self.data.setdefault("certificate_of_occupancy", {}).get("envelope_id"):
            if self.home.customer_documents.filter(description=app.OCCUPANCY_DESCRIPTION):
                raise ValueError("Signing is already started.")

        signer = self.get_building_permit_signer()
        if signer is None:
            msg = "No user associated with %s authorized for signatures"
            raise ValueError(msg % self.home.get_builder())

        if self.signed_building_permit is None:
            raise ValueError("You need a signed permit to proceed")

        filename = "Compliance Report - {company}.pdf".format(company=user.company)
        description = app.OCCUPANCY_DESCRIPTION
        customer_document = render_customer_document_from_template(
            self.home,
            filename,
            description,
            owner=user.company,
            f_populate=populate_certificate_of_occupancy_template,
            user=user,
        )
        document_obj = CertificateOfOccupancy()
        envelope = document_obj.create_envelope(
            customer_document,
            user=signer,
            company=user.company,
            address=self.home.get_addr(include_city_state_zip=True, company=user.company),
        )
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") + "0Z"
        self.data.update(
            {
                "certificate_of_occupancy": {
                    "envelope_id": envelope["envelopeId"],
                    "request_user": user.pk,
                    "initial_request_date": now,
                }
            }
        )
        self.save(update_fields=["data"])

    def get_building_permit_signer(self):
        """Gets the building siging user"""
        builder = self.home.get_builder()
        user = builder.users.filter(is_company_admin=True, is_active=True).first()
        if user is None:
            user = builder.users.all().first()  # TODO:  We need to review this
        return user

    def sign_building_permit(self, signed_document, certificate, for_user=None):
        """Attach the signed permit here"""

        user = for_user or User.objects.get(pk=self.data["building_permit"]["request_user"])

        filename = "Building Permit Report - {company} SIGNED.pdf".format(company=user.company)
        description = app.PERMIT_DESCRIPTION

        # Remove unsigned document, store the signed one
        existing = self.home.customer_documents.filter(
            company=user.company, description=app.PERMIT_DESCRIPTION
        ).first()

        log.debug("Attaching signed Building Permit Report")
        self.signed_building_permit = self.home.customer_documents.store(
            self.home,
            company=user.company,
            filename=filename,
            description=description,
            document=signed_document,
            pk=existing.pk if existing else None,
        )

    def sign_certificate_of_occupancy(self, signed_document, certificate, for_user=None):
        """Attach the occupancy report"""

        _user_pk = self.data["building_permit"]["request_user"]
        user = for_user if for_user else User.objects.get(pk=_user_pk)

        filename = "Compliance Report - {company} SIGNED.pdf".format(company=user.company)
        description = app.OCCUPANCY_DESCRIPTION

        # Remove unsigned document, store the signed one
        existing = self.home.customer_documents.filter(
            company=user.company, description=app.OCCUPANCY_DESCRIPTION
        ).first()

        log.debug("Attaching signed Certificate Of Occupancy Report")
        self.signed_certificate_of_occupancy = self.home.customer_documents.store(
            self.home,
            company=user.company,
            filename=filename,
            description=description,
            document=signed_document,
            pk=existing.pk if existing else None,
        )
