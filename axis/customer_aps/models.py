"""models.py: Django aps"""


import logging

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords

from axis.geographic.placedmodels import LotAddressedPlacedModel
from axis.incentive_payment.models import IPPItem
from .managers import APSManager

__author__ = "Steven Klass"
__date__ = "11/18/11 2:08 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class APSHome(LotAddressedPlacedModel):
    """
    Specific to APS.  This is the data we get from APS.  We are
    going to try to validate this to our records.

    This is referred to by the frontend as a "meterset" upload.

    """

    aps_id = models.CharField(max_length=32, unique=True, null=True, blank=True)  # APS Specific ID
    premise_id = models.CharField(
        max_length=32, unique=True, null=True, blank=True
    )  # new APS specific ID

    # The data we got from APS.
    raw_lot_number = models.CharField(max_length=32, null=True, blank=True)
    raw_street_number = models.CharField(max_length=64, null=True, blank=True)
    raw_prefix = models.CharField(max_length=64, null=True, blank=True)
    raw_street_name = models.CharField(max_length=255, null=True, blank=True)
    raw_suffix = models.CharField(max_length=64, null=True, blank=True)
    raw_street_line_1 = models.CharField(max_length=100, null=True, blank=True)
    raw_street_line_2 = models.CharField(max_length=64, null=True, blank=True)
    raw_city = models.CharField(max_length=64, null=True, blank=True)
    raw_state = models.CharField(max_length=16, null=True, blank=True)
    raw_zip = models.CharField(max_length=12, null=True, blank=True)

    home = models.OneToOneField("home.Home", null=True, blank=True, on_delete=models.SET_NULL)

    meterset_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = APSManager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = "APS Exported Home"

    def get_raw_addr(self):
        """Return the raw address"""
        if self.raw_street_line_1:
            return self.raw_street_line_1

        # TODO: Remove this completely
        addr = [
            self.raw_street_number,
            self.raw_prefix,
            self.raw_street_name,
            self.raw_suffix,
            self.street_line2,
        ]
        return " ".join(["{}".format(x) for x in addr if x is not None])

    def __str__(self):
        """Return some thing nice"""
        addr = [self.get_raw_addr(), self.raw_city, self.raw_zip]
        addr = " ".join(["{}".format(x) for x in addr if x is not None])
        return addr

    def get_absolute_url(self):
        """Absolute URL"""
        return reverse("aps_homes_detail_view", kwargs={"pk": self.pk})

    def can_be_deleted(self, user):
        """Can a user delete the object"""
        if user.is_superuser:
            return True
        if self.has_paid_incentives():
            return False
        return hasattr(user, "company") and user.company.slug == "aps" and user.is_company_admin

    def can_be_edited(self, user):
        """Can a user edit the object"""
        if user.is_superuser:
            return True
        if self.has_paid_incentives():
            return False
        return hasattr(user, "company") and user.company.slug == "aps" and user.is_company_admin

    @classmethod
    def can_be_added(cls, requesting_user):
        return requesting_user.has_perm("customer_aps.add_apshome")

    def has_paid_incentives(self):
        """Does the object have incentives paid"""
        lookup_id = self.aps_id or self.premise_id
        if LegacyAPSHome.objects.filter(aps_id__in=lookup_id).count():
            return True
        if self.home:
            return bool(
                IPPItem.objects.filter(
                    home_status__home=self.home, incentive_distribution__is_paid=True
                ).count()
            )
        return False

    def get_geocoding_type(self):
        """Indicates which type of geocoding logic is required for the templates."""
        # This is overridden from its default "apshome" to be just "home", since the data types
        # should be identical from the geocoder's point of view.
        return "home"


class LegacyAPSBuilder(models.Model):
    """Maps the legacy id to the builder"""

    aps_id = models.CharField(max_length=32)
    active = models.BooleanField(default=False)
    bldr_comment = models.CharField(max_length=255, blank=True, null=True)
    bldr_id = models.CharField(max_length=5, blank=True, null=True)
    charge_no = models.CharField(max_length=7, blank=True, null=True)
    dba = models.CharField(max_length=32, blank=True, null=True)
    fax = models.CharField(max_length=12, blank=True, null=True)
    mail_addr1 = models.CharField(max_length=32, blank=True, null=True)
    mail_addr2 = models.CharField(max_length=16, blank=True, null=True)
    mail_city = models.CharField(max_length=32, blank=True, null=True)
    mail_state = models.CharField(max_length=4, blank=True, null=True)
    mail_zip = models.CharField(max_length=16, blank=True, null=True)
    pay_point = models.CharField(max_length=5, blank=True, null=True)
    phone = models.CharField(max_length=16, blank=True, null=True)
    phone2 = models.CharField(max_length=5, blank=True, null=True)
    site_addr = models.CharField(max_length=32, blank=True, null=True)
    site_city = models.CharField(max_length=32, blank=True, null=True)
    site_state = models.CharField(max_length=5, blank=True, null=True)
    site_zip = models.CharField(max_length=9, blank=True, null=True)
    soalr_charge_no = models.CharField(max_length=12, blank=True, null=True)
    vendor_no = models.CharField(max_length=8, blank=True, null=True)
    web_address = models.CharField(max_length=64, blank=True, null=True)
    builder = models.ForeignKey("company.Company", on_delete=models.CASCADE)
    objects = APSManager()

    class Meta:
        verbose_name = "Legacy APS Builder"

    def __str__(self):
        return "{} ({})".format(self.builder, self.aps_id)

    def get_absolute_url(self):
        """Return the absolute url for this model"""
        return reverse("aps_legacy_builder_detail_view", kwargs={"pk": self.id})

    def can_be_deleted(self, user):
        """Can the object be deleted by the user"""
        return user.has_perm("customer_aps.delete_legacyapsbuilder")


class LegacyAPSSubdivision(models.Model):
    """Maps the legacy id to the subdivision"""

    aps_id = models.CharField(max_length=32, blank=True, null=True)
    active = models.BooleanField(default=False)
    addendum_date = models.DateField(blank=True, null=True)
    addendum_lots = models.CharField(max_length=8, blank=True, null=True)
    ammended_date = models.DateField(blank=True, null=True)
    ammended_lots = models.CharField(max_length=8, blank=True, null=True)
    legacy_builder = models.ForeignKey(
        "LegacyAPSBuilder", on_delete=models.CASCADE, blank=True, null=True
    )
    contract_date = models.DateField(blank=True, null=True)
    exp_date = models.DateField(blank=True, null=True)
    lots_paid = models.CharField(max_length=8, blank=True, null=True)
    lots_signed = models.CharField(max_length=8, blank=True, null=True)
    mstr_plan = models.CharField(max_length=64, blank=True, null=True)
    parcel = models.CharField(max_length=24, blank=True, null=True)
    solar_community = models.CharField(max_length=3, blank=True, null=True)
    sub = models.CharField(max_length=64, blank=True, null=True)
    sub_comment = models.CharField(max_length=96, blank=True, null=True)
    sub_loc_city = models.CharField(max_length=32, blank=True, null=True)
    sub_loc_zip = models.CharField(max_length=9, blank=True, null=True)
    sub_location = models.CharField(max_length=64, blank=True, null=True)
    legacy_rater = models.ForeignKey(
        "company.Company", on_delete=models.CASCADE, blank=True, null=True
    )
    legacy_import_comment = models.CharField(max_length=256, blank=True, null=True)
    is_legacy = models.BooleanField(default=True)
    objects = APSManager()

    class Meta:
        verbose_name = "Legacy APS Subdivision"

    def __str__(self):
        return "{} ({})".format(self.sub, self.aps_id)

    def get_absolute_url(self):
        """Return the absolute url for this model"""
        return reverse("aps_legacy_subdivision_detail_view", kwargs={"pk": self.id})


class LegacyAPSHome(models.Model):
    """Legacy APS Homes - Brought in as a one time dump."""

    addr_dir = models.CharField(max_length=4, blank=True, null=True)
    addr_name = models.CharField(max_length=32, blank=True, null=True)
    addr_no = models.CharField(max_length=16, blank=True, null=True)
    addr_sufx = models.CharField(max_length=8, blank=True, null=True)
    amt_pd = models.DecimalField(default=0, max_digits=8, decimal_places=2, blank=True, null=True)
    amt_pd_sr = models.CharField(max_length=16, blank=True, null=True)
    append_date = models.DateField(blank=True, null=True)
    ck_numb = models.CharField(max_length=16, blank=True, null=True)
    ck_req_date = models.DateField(blank=True, null=True)
    comments = models.CharField(max_length=128, blank=True, null=True)
    compliance_date = models.DateField(blank=True, null=True)
    dev = models.CharField(max_length=64, blank=True, null=True)
    h2_opv_pd = models.DecimalField(
        default=0, max_digits=8, decimal_places=2, blank=True, null=True
    )
    initial_meter_set = models.CharField(max_length=32, blank=True, null=True)
    lot_no = models.CharField(max_length=16, blank=True, null=True)
    lot_recno = models.CharField(max_length=16, blank=True, null=True)
    lot_status = models.CharField(max_length=16, blank=True, null=True)
    lt_city = models.CharField(max_length=32, blank=True, null=True)
    lt_state = models.CharField(max_length=12, blank=True, null=True)
    lt_zip = models.CharField(max_length=16, blank=True, null=True)
    pd_date = models.DateField(blank=True, null=True)
    pd_date_sr = models.DateField(blank=True, null=True)
    plan_no = models.CharField(max_length=12, blank=True, null=True)
    aps_id = models.CharField(max_length=32, blank=True, null=True)
    solar_ready = models.CharField(max_length=4, blank=True, null=True)
    solar_type = models.CharField(max_length=8, blank=True, null=True)
    legacy_subdivision = models.ForeignKey(
        "LegacyAPSSubdivision", on_delete=models.CASCADE, blank=True, null=True
    )
    legacy_builder = models.ForeignKey(
        "LegacyAPSBuilder", on_delete=models.CASCADE, blank=True, null=True
    )
    legacy_import_comment = models.CharField(max_length=256, blank=True, null=True)
    aps_home = models.ForeignKey("APSHome", on_delete=models.CASCADE, blank=True, null=True)
    eep_program = models.ForeignKey(
        "eep_program.EEPProgram", on_delete=models.CASCADE, blank=True, null=True
    )
    is_legacy = models.BooleanField(default=True)
    objects = APSManager()

    class Meta:
        verbose_name = "Legacy APS Home"

    def __str__(self):
        return self.aps_id

    def get_street_line_1(self):
        """Return the street line 1 equiv."""
        addr = [self.addr_no, self.addr_dir, self.addr_name, self.addr_sufx]
        return " ".join(filter(None, addr))

    def get_absolute_url(self):
        """Return the absolute url for this model"""
        return reverse("aps_legacy_home_detail_view", kwargs={"pk": self.id})


SMART_TSTAT_ELIGIBILITY = (
    ("ineligible", "Not Eligible"),
    ("partial", "Eligible and partial participation"),
    ("complete", "Eligible and 100% participation"),
)


SMART_TSTAT_ELIGIBILITY_DEFAULT = "ineligible"

SMART_TSTAT_MODELS = (
    (1, "ecobee3"),
    (2, "ecobee3 lite"),
    (3, "ecobee Smart Si"),
    (4, "ecobee Smart"),
    (5, "ecobee4"),
    (6, "Lyric Round Wi-Fi Thermostat – RCH9310WF"),
    (7, "Lyric T5 Wi-Fi Thermostat – RCHT8610WF"),
    (8, "Lyric T6 Pro Wi-Fi Thermostat – TH6320WF2003/TH6220WF2006 "),
    (9, "Wi-Fi Smart Thermostat – RTH9580WF"),
    (10, "Wi-Fi Smart Color Thermostat – RTH9585WF"),
    (11, "Wi-Fi Smart Thermostat with Voice Control – RTH9590WF"),
    (12, "Wi-Fi 7-Day Programmable Thermostat – RTH6580WF "),
    (13, "Wi-Fi 7-Day Programmable Touchscreen Thermostat – RTH8580WF"),
    (14, "Wi-Fi 9000 – TH9320WF5003"),
    (15, "Wi-Fi 9000 with Voice Control – TH9320WFV6007"),
    (16, "Wi-Fi Focus Pro (Wi-Fi 6000) – RTH6580WF"),
    (17, "Wi-Fi Vision Pro (Wi-Fi 8000) – TH8321WF1001"),
    (18, "LUX/GEO-BL "),
    (19, "LUX/GEO-WH"),
    (20, "KONO"),
    (21, "Nest Learning Thermostat"),
    (22, "Nest Thermostat E"),
    (23, "Radio Thermostat Wi-Fi CT50"),
    (24, "Radio Thermostat Wi-Fi CT80"),
    (25, "Radio Thermostat CT100 with Vivint Go! Control Panel"),
    (26, "Sensi™ Wi-Fi Thermostat"),
    (27, "Sensi™ Touch Wi-Fi Thermostat"),
    (28, "Radio Thermostat CT30"),
    (29, "Radio Thermostat CT80"),
    (30, "Radio Thermostat CT100"),
    (31, "Trane ComfortLink Control"),
    (32, "RCS Z-Wave Communicating Thermostat"),
    (33, "GoControl Z-Wave Thermostat"),
    (34, "Alarm.com Smart Thermostat"),
    (35, "T6 Z-Wave® Thermostat – TH6320ZW2003"),
    (36, "Trane Comfortlink 2 XL850"),
    (37, "T6 Pro Wifi Model TH6220WF Touch Screen"),
    (38, "Carrier Cor7C WiFi TSTWRH01"),
    (39, "APRILAIRE 8840"),
    (40, "Lennox M30 WiFi Thermostat"),
    (41, "Trane XL824/624"),
    (42, "T10 Smart Thermostat – THX321WFS2001W/U"),
)


class APSSmartThermostatOption(models.Model):
    """Represents the smart thermostat options for a subdivision"""

    subdivision = models.OneToOneField(
        "subdivision.Subdivision", on_delete=models.CASCADE, related_name="aps_thermostat_option"
    )

    eligibility = models.CharField(
        choices=SMART_TSTAT_ELIGIBILITY, max_length=14, default=SMART_TSTAT_ELIGIBILITY_DEFAULT
    )
    models = models.CharField(
        validators=[validate_comma_separated_integer_list],
        choices=SMART_TSTAT_ELIGIBILITY,
        max_length=64,
        blank=True,
        null=True,
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "APS Smart Thermostat Option"

    def __str__(self):
        return "{subdivision} - {eligibility}".format(
            subdivision=self.subdivision, eligibility=self.get_eligibility_display()
        )

    def get_models_pretty(self):
        """Get a pretty model names"""
        _models = self.models
        if not isinstance(_models, set):
            _models = eval(_models)  # pylint: disable=eval-used
        return [dict(SMART_TSTAT_MODELS).get(x, "-") for x in _models]
