"""models.py: Django customer_neea"""

import datetime
from collections import OrderedDict

from django.utils.timezone import now
from lxml import etree
from lxml.etree import XMLSyntaxError

from axis.company.models import Company
from axis.core.fields import AxisJSONField
from axis.customer_neea.managers import (
    NeeaGeneralLegacyManager,
    LegacyNEEAPartnerToHouseManager,
    NeeaLegacyPartnerManager,
    NeeaLegacyHomeManager,
    NeeaLegacyContactManager,
    StandardProtocolCalculatorManager,
)
from axis.customer_neea.neea_data_report.models import *  # noqa
from .rtf_calculator.constants.neea_v3 import (
    NEEA_REFRIGERATOR_CHOICE_MAP,
    NEEA_CLOTHES_WASHER_CHOICE_MAP,
)

__author__ = "Steven Klass"
__date__ = "9/5/12 5:30 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

# noinspection PyShadowingBuiltins

log = logging.getLogger(__name__)


# noinspection PyShadowingBuiltins
class LegacyNEEATCO(models.Model):
    """TCO assigned"""

    id = models.IntegerField(primary_key=True, db_column="TCO_ID")
    tco = models.CharField(max_length=600, db_column="TCO", blank=True)
    description = models.CharField(max_length=3000, db_column="Description", blank=True)
    last_update_by = models.CharField(max_length=150, db_column="Last_Update_By", blank=True)
    last_update_date = models.DateTimeField(null=True, db_column="Last_Update_Date", blank=True)
    active = models.IntegerField(db_column="Active")

    class Meta:
        """Non-field options"""

        db_table = "TCO"
        managed = False

    def __str__(self):
        return self.tco


# noinspection PyShadowingBuiltins
class LegacyNEEABOP(models.Model):
    """Available BOP"""

    id = models.IntegerField(primary_key=True, db_column="BOP_ID")
    name = models.CharField(max_length=150, db_column="BOP", blank=True)
    description = models.CharField(max_length=3000, db_column="Description", blank=True)
    active = models.IntegerField(db_column="Active")
    last_update_by = models.CharField(max_length=150, db_column="Last_Update_By", blank=True)
    last_update_date = models.DateTimeField(null=True, db_column="Last_Update_Date", blank=True)
    multifamily = models.IntegerField(db_column="MultiFamily")
    bop_xml = models.TextField(db_column="BOP_XML", blank=True)
    bop_order = models.IntegerField(null=True, db_column="BOP_Order", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "BOP"
        managed = False

    def __str__(self):
        return self.name


# noinspection PyShadowingBuiltins
class LegacyNEEARegion(models.Model):
    """Regions"""

    id = models.IntegerField(primary_key=True, db_column="Region_ID")
    name = models.CharField(max_length=150, db_column="Region", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "Region"
        managed = False

    def __str__(self):
        return self.name


class LegacyNEEAZipPlus(models.Model):
    """ZIP Codes"""

    zip_code = models.CharField(max_length=15, primary_key=True, db_column="Zip_Code")
    city = models.CharField(max_length=150, db_column="City", blank=True)
    state = models.CharField(max_length=150, db_column="State", blank=True)
    state_abbr = models.CharField(max_length=6, db_column="State_Abbr", blank=True)
    region = models.ForeignKey(
        "LegacyNEEARegion",
        on_delete=models.CASCADE,
        null=True,
        db_column="Region_ID",
        blank=True,
        db_constraint=False,
    )
    last_update_by = models.CharField(max_length=150, db_column="Last_Update_By")
    last_update_date = models.DateTimeField(null=True, db_column="Last_Update_Date", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "Zip_Plus"
        managed = False

    def __str__(self):
        return self.zip_code


# noinspection PyShadowingBuiltins
class LegacyNEEAZipCounty(models.Model):
    """Zip to County"""

    id = models.IntegerField(primary_key=True, db_column="id")
    zip_code = models.ForeignKey(
        "LegacyNEEAZipPlus",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_column="Zip_Code",
        db_constraint=False,
    )
    county = models.CharField(max_length=192, db_column="County")

    class Meta:
        """Non-field options"""

        db_table = "ZipCounty"
        managed = False


# noinspection PyShadowingBuiltins
class LegacyNEEAAddress(models.Model):
    """Address"""

    id = models.IntegerField(primary_key=True, db_column="Address_ID")
    lot_no = models.CharField(max_length=150, db_column="Lot_No", blank=True)
    street_no = models.CharField(max_length=45, db_column="Street_No", blank=True)
    street_modifier = models.CharField(max_length=6, db_column="Street_Modifier", blank=True)
    street_name = models.CharField(max_length=300, db_column="Street_Name", blank=True)
    zip_code = models.ForeignKey(
        "LegacyNEEAZipPlus",
        db_column="Zip_Code",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_constraint=False,
    )
    last_update_by = models.CharField(max_length=150, db_column="Last_Update_By")
    last_update_date = models.DateTimeField(null=True, db_column="Last_Update_Date", blank=True)
    development_name = models.CharField(max_length=150, db_column="Development_Name", blank=True)
    oldaddress = models.CharField(max_length=900, db_column="OldAddress", blank=True)
    county = models.CharField(max_length=192, db_column="County", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "Address"
        managed = False

    def get_formatted_address(self, skip_lot=False, skip_zip=False, line1_only=False):
        """Return formatted address
        :param skip_lot: Skip the lot number
        :param skip_zip: Skip the ZIP Code
        :param line1_only: Only print line 1
        """
        name = "{}".format(self.street_no)
        name += "{}".format(" {}".format(self.street_modifier) if self.street_modifier else "")
        name += "{}".format(" {}".format(self.street_name) if self.street_name else "")
        if line1_only:
            return name
        if self.zip_code:
            name += "{}".format(", {}".format(self.zip_code.city) if self.zip_code.city else "")
            name += "{}".format(
                " {}".format(self.zip_code.state_abbr) if self.zip_code.state_abbr else ""
            )
        if not skip_zip:
            name += "{}".format(", {}".format(str(self.zip_code)) if self.zip_code else "")
        if not skip_lot:
            name += "{}".format(" Lot: [{}]".format(self.lot_no) if self.lot_no else "")
        return name

    def __str__(self):
        return self.get_formatted_address()

    def get_absolute_url(self):
        """Return associated url"""
        return reverse("legacy_partner_view", kwargs=dict(pk=self.id))

    def get_region(self):
        """Return the region"""
        return self.zip_code.region

    @property
    def formatted_address(self):
        return self.get_formatted_address()

    @property
    def city(self):
        return self.zip_code.city

    @property
    def state(self):
        return self.zip_code.state_abbr

    @property
    def street_line1(self):
        return self.get_formatted_address(line1_only=True)


# noinspection PyShadowingBuiltins
class LegacyNEEAStatus(models.Model):
    """Status"""

    id = models.IntegerField(primary_key=True, db_column="Status_ID")
    status = models.CharField(max_length=150, db_column="Status", blank=True)
    ordinal = models.IntegerField(null=True, db_column="Ordinal", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "Status"
        managed = False

    def __str__(self):
        return self.status


# noinspection PyShadowingBuiltins
class LegacyNEEABOPHeatSource(models.Model):
    """Heat Sources"""

    id = models.IntegerField(primary_key=True, db_column="BOP_Heat_Source_ID")
    heat_source = models.CharField(max_length=150, db_column="Heat_Source", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "BOP_Heat_Source"
        managed = False

    def __str__(self):
        return self.heat_source


# noinspection PyShadowingBuiltins
class LegacyNEEABOPToHeat(models.Model):
    """BOP to Heat Sources"""

    id = models.IntegerField(primary_key=True, db_column="BOP_To_Heat_Source_ID")
    bop_heat_source = models.ForeignKey(
        "LegacyNEEABOPHeatSource",
        on_delete=models.CASCADE,
        null=True,
        db_column="BOP_Heat_Source_ID",
        blank=True,
        db_constraint=False,
    )
    bop = models.ForeignKey(
        "LegacyNEEABOP",
        on_delete=models.CASCADE,
        null=True,
        db_column="BOP_ID",
        blank=True,
        db_constraint=False,
    )

    class Meta:
        """Non-field options"""

        db_table = "BOP_To_Heat"
        managed = False


# noinspection PyShadowingBuiltins
class LegacyNEEABOPToState(models.Model):
    """BOP to States"""

    id = models.IntegerField(primary_key=True, db_column="BOP_To_State_ID")
    bop = models.ForeignKey(
        "LegacyNEEABOP",
        on_delete=models.CASCADE,
        null=True,
        db_column="BOP_ID",
        blank=True,
        db_constraint=False,
    )
    state_abbr = models.CharField(max_length=6, db_column="State_Abbr", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "BOP_To_State"
        managed = False


# noinspection PyShadowingBuiltins
class LegacyNEEABOPToTCO(models.Model):
    """BOP to TCO"""

    id = models.IntegerField(primary_key=True, db_column="BOP_To_TCO_ID")
    bop = models.ForeignKey(
        "LegacyNEEABOP",
        on_delete=models.CASCADE,
        null=True,
        db_column="BOP_ID",
        blank=True,
        db_constraint=False,
    )
    tco = models.ForeignKey(
        "LegacyNEEATCO",
        on_delete=models.CASCADE,
        null=True,
        db_column="TCO_ID",
        blank=True,
        db_constraint=False,
    )

    class Meta:
        """Non-field options"""

        db_table = "BOP_To_TCO"
        managed = False


# noinspection PyShadowingBuiltins
class LegacyNEEATCOToState(models.Model):
    """TCO to State"""

    id = models.IntegerField(primary_key=True, db_column="TCO_To_State_ID")
    tco = models.ForeignKey(
        "LegacyNEEATCO",
        on_delete=models.CASCADE,
        null=True,
        db_column="TCO_ID",
        blank=True,
        db_constraint=False,
    )
    state_abbr = models.CharField(max_length=6, db_column="State_Abbr", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "TCO_To_State"
        managed = False


# noinspection PyShadowingBuiltins
class LegacyNEEABuilderType(models.Model):
    """Types of builders"""

    id = models.IntegerField(primary_key=True, db_column="Builder_Type_ID")
    builder_type = models.CharField(max_length=150, db_column="Builder_Type", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "Builder_Type"
        managed = False

    def __str__(self):
        return self.builder_type


# noinspection PyShadowingBuiltins
class LegacyNEEAPartner(models.Model):
    """Partner companies"""

    id = models.IntegerField(primary_key=True, db_column="Partner_ID")
    address = models.ForeignKey(
        "LegacyNEEAAddress",
        on_delete=models.CASCADE,
        null=True,
        db_column="Address_ID",
        blank=True,
        db_constraint=False,
    )
    last_update_by = models.CharField(max_length=150, db_column="Last_Update_By")
    last_update_date = models.DateTimeField(db_column="Last_Update_Date")
    website = models.CharField(max_length=300, db_column="Website", blank=True)
    partner_name = models.CharField(max_length=300, db_column="Partner_Name", blank=True)
    partner_type = models.CharField(max_length=150, db_column="Partner_Type", blank=True)
    utility_type = models.CharField(max_length=150, db_column="Utility_Type", blank=True)
    builder_type = models.ForeignKey(
        "LegacyNEEABuilderType",
        on_delete=models.CASCADE,
        null=True,
        db_column="Builder_Type_ID",
        blank=True,
        db_constraint=False,
    )
    partner_since_date = models.DateTimeField(null=True, db_column="Partner_Since_Date", blank=True)
    homes_built_per_year = models.IntegerField(
        null=True, db_column="Homes_Built_Per_Year", blank=True
    )
    builder_experience_years = models.IntegerField(
        null=True, db_column="Builder_Experience_Years", blank=True
    )
    commitment = models.IntegerField(db_column="Commitment")
    star_homes_per_year = models.IntegerField(
        null=True, db_column="Star_Homes_Per_Year", blank=True
    )
    notes = models.CharField(max_length=7500, db_column="Notes", blank=True)
    active = models.BooleanField(default=False, db_column="Active")
    objects = NeeaLegacyPartnerManager()

    class Meta:
        """Non-field options"""

        verbose_name = "Legacy NEEA Partner"
        db_table = "Partner"
        managed = False

    def __str__(self):
        return self.partner_name

    def get_absolute_url(self):
        """Return associated url"""
        return reverse("neea_legacy_partner_view", kwargs=dict(pk=self.id))


class LegacyNEEAPartnerAxisBridge(models.Model):
    partner = models.ForeignKey(
        "LegacyNEEAPartner",
        on_delete=models.CASCADE,
        related_name="axis_company",
        db_constraint=False,
    )
    company_id = models.IntegerField()

    class Meta:
        """Non-field options"""

        verbose_name = "Legacy NEEA Partner to Axis Bridge"

    def __str__(self):
        return "{} <-> {}".format(self.partner, Company.objects.get(id=self.company_id))


# noinspection PyShadowingBuiltins
class LegacyNEEAContactType(models.Model):
    """Type of Contact"""

    id = models.IntegerField(primary_key=True, db_column="Contact_Type_ID")
    contact_type = models.CharField(max_length=150, db_column="Contact_Type", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "Contact_Type"
        managed = False


# noinspection PyShadowingBuiltins
class LegacyNEEAContact(models.Model):
    """Contacts"""

    id = models.IntegerField(primary_key=True, db_column="Contact_ID")
    title = models.CharField(max_length=150, db_column="Title", blank=True)
    last_name = models.CharField(max_length=150, db_column="Last_Name", blank=True)
    first_name = models.CharField(max_length=150, db_column="First_Name", blank=True)
    email = models.CharField(max_length=300, db_column="Email", blank=True)
    office_phone = models.CharField(max_length=60, db_column="Office_Phone", blank=True)
    direct_phone = models.CharField(max_length=60, db_column="Direct_Phone", blank=True)
    cell_phone = models.CharField(max_length=60, db_column="Cell_Phone", blank=True)
    fax = models.CharField(max_length=60, db_column="Fax", blank=True)
    alternate_phone = models.CharField(max_length=60, db_column="Alternate_Phone", blank=True)
    last_update_by = models.CharField(max_length=150, db_column="Last_Update_By")
    last_update_date = models.DateTimeField(null=True, db_column="Last_Update_Date", blank=True)
    partner = models.ForeignKey(
        "LegacyNEEAPartner",
        on_delete=models.CASCADE,
        null=True,
        db_column="Partner_ID",
        blank=True,
        db_constraint=False,
    )
    active = models.IntegerField(null=True, db_column="Active", blank=True)
    username = models.CharField(max_length=150, db_column="UserName", blank=True)
    address = models.ForeignKey(
        "LegacyNEEAAddress",
        on_delete=models.CASCADE,
        null=True,
        db_column="Address_ID",
        blank=True,
        db_constraint=False,
    )
    certified_date = models.DateTimeField(null=True, db_column="Certified_Date", blank=True)
    certifier = models.CharField(max_length=150, db_column="Certifier", blank=True)
    ducts = models.IntegerField(db_column="Ducts")
    blower_door = models.IntegerField(db_column="Blower_Door")
    heat_pump = models.IntegerField(db_column="Heat_Pump")
    agreement_date = models.DateTimeField(null=True, db_column="Agreement_Date", blank=True)

    objects = NeeaLegacyContactManager()

    class Meta:
        """Non-field options"""

        db_table = "Contact"
        managed = False

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def get_absolute_url(self):
        """Return associated url"""
        return reverse("neea_legacy_contact_view", kwargs=dict(pk=self.id))


# noinspection PyShadowingBuiltins
class LegacyNEEAContactStateCertification(models.Model):
    """States the contact is certified in"""

    id = models.IntegerField(primary_key=True, db_column="CertifyID")
    contact = models.ForeignKey(
        "LegacyNEEAContact",
        on_delete=models.CASCADE,
        null=True,
        db_column="Contact_ID",
        blank=True,
        db_constraint=False,
    )
    state_abbr = models.CharField(max_length=6, db_column="State_Abbr", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "Contact_State_Certification"
        managed = False


# noinspection PyShadowingBuiltins
class LegacyNEEAContactToType(models.Model):
    """Contact to Types"""

    id = models.IntegerField(primary_key=True, db_column="Contact_To_Type_ID")
    contact = models.ForeignKey(
        "LegacyNEEAContact",
        on_delete=models.CASCADE,
        null=True,
        db_column="Contact_ID",
        blank=True,
        db_constraint=False,
    )
    contact_type = models.ForeignKey(
        "LegacyNEEAContactType",
        on_delete=models.CASCADE,
        null=True,
        db_column="Contact_Type_ID",
        blank=True,
        db_constraint=False,
    )

    class Meta:
        """Non-field options"""

        db_table = "Contact_To_Type"
        managed = False


# noinspection PyShadowingBuiltins
class LegacyNEEAHomeType(models.Model):
    """Home Types"""

    id = models.IntegerField(primary_key=True, db_column="Home_Type_ID")
    name = models.CharField(max_length=150, db_column="Description", blank=True)
    last_update_by = models.CharField(max_length=150, db_column="Last_Update_By")
    last_update_date = models.DateTimeField(null=True, db_column="Last_Update_Date", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "Home_Type"
        managed = False

    def __str__(self):
        return self.name


# noinspection PyShadowingBuiltins
class LegacyNEEAHome(models.Model):
    """Home"""

    id = models.IntegerField(primary_key=True, db_column="Home_ID")
    builder_owner = models.IntegerField(null=True, db_column="Builder_Owner", blank=True)
    eto_territory = models.BooleanField(default=False, db_column="ETO_Territory", blank=True)
    electric_utility_account_no = models.CharField(
        max_length=75, db_column="Electric_Utility_Account_No", blank=True
    )
    gas_utility_account_no = models.CharField(
        max_length=75, db_column="Gas_Utility_Account_No", blank=True
    )
    home_type = models.ForeignKey(
        "LegacyNEEAHomeType",
        on_delete=models.CASCADE,
        null=True,
        db_column="Home_Type_ID",
        blank=True,
        db_constraint=False,
    )
    address = models.ForeignKey(
        "LegacyNEEAAddress",
        on_delete=models.CASCADE,
        null=True,
        db_column="Address_ID",
        blank=True,
        db_constraint=False,
    )
    last_update_by = models.CharField(max_length=150, db_column="Last_Update_By")
    last_update_date = models.DateField(null=True, db_column="Last_Update_Date", blank=True)
    project_start_date = models.DateField(null=True, db_column="Project_Start_Date", blank=True)
    estimated_completion_date = models.DateField(
        null=True, db_column="Estimated_Completion_Date", blank=True
    )
    reference_home = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        db_column="Reference_Home_ID",
        blank=True,
        db_constraint=False,
    )
    multifamily = models.BooleanField(default=False, db_column="MultiFamily")
    description = models.CharField(max_length=600, db_column="Description", blank=True)
    initiation_date = models.DateField(null=True, db_column="Initiation_Date", blank=True)

    objects = NeeaLegacyHomeManager()

    class Meta:
        """Non-field options"""

        verbose_name = "Legacy NEEA Home"
        verbose_name_plural = "Legacy NEEA Homes"
        db_table = "Home"
        managed = False

    def __str__(self):
        return "{}".format(self.address)

    def get_absolute_url(self):
        """Return associated url"""
        return reverse("neea_legacy_home_view", kwargs=dict(pk=self.id))


# noinspection PyShadowingBuiltins
class LegacyNEEAIncentive(models.Model):
    """Incentives available"""

    id = models.IntegerField(primary_key=True, db_column="Incentive_ID")
    name = models.CharField(max_length=150, db_column="Description")

    class Meta:
        """Non-field options"""

        db_table = "Incentive"
        managed = False

    def __str__(self):
        return self.name


# noinspection PyShadowingBuiltins
class LegacyNEEAPartnerToHouse(models.Model):
    """Partners associated to a home"""

    id = models.IntegerField(primary_key=True, db_column="Partner_To_House_ID")
    home = models.ForeignKey(
        "LegacyNEEAHome",
        on_delete=models.CASCADE,
        null=True,
        db_column="Home_ID",
        blank=True,
        db_constraint=False,
    )
    partner = models.ForeignKey(
        "LegacyNEEAPartner",
        on_delete=models.CASCADE,
        null=True,
        db_column="Partner_ID",
        blank=True,
        db_constraint=False,
    )
    last_update_by = models.CharField(max_length=150, db_column="Last_Update_By")
    last_update_date = models.DateTimeField(null=True, db_column="Last_Update_Date", blank=True)
    contact = models.ForeignKey(
        "LegacyNEEAContact",
        on_delete=models.CASCADE,
        null=True,
        db_column="Contact_ID",
        blank=True,
        db_constraint=False,
    )
    partner_role = models.CharField(max_length=150, db_column="Partner_Role", blank=True)

    objects = LegacyNEEAPartnerToHouseManager()

    class Meta:
        """Non-field options"""

        db_table = "Partner_To_House"
        managed = False

    def __str__(self):
        return "{}{}".format(self.partner, " ({})".format(self.contact) if self.contact else "")


# noinspection PyShadowingBuiltins
class LegacyNEEAPartnerToRegion(models.Model):
    """Parter to Region"""

    id = models.IntegerField(primary_key=True, db_column="Partner_to_Region_ID")
    partner = models.ForeignKey(
        "LegacyNEEAPartner",
        on_delete=models.CASCADE,
        db_column="Partner_ID",
        db_constraint=False,
    )
    region = models.ForeignKey(
        "LegacyNEEARegion",
        on_delete=models.CASCADE,
        db_column="Region_ID",
        db_constraint=False,
    )

    class Meta:
        """Non-field options"""

        db_table = "Partner_to_Region"
        managed = False


# noinspection PyShadowingBuiltins
class LegacyNEEAPerformanceTest(models.Model):
    """Performance Tests"""

    id = models.IntegerField(primary_key=True, db_column="Performance_Test_ID")
    title = models.CharField(max_length=150, db_column="Title", blank=True)
    description = models.CharField(max_length=600, db_column="Description", blank=True)
    performance_test_xml = models.TextField(db_column="Performance_Test_Xml", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "Performance_Test"
        managed = False

    def __str__(self):
        return self.title


# noinspection PyShadowingBuiltins
class LegacyNEEAInspection(models.Model):
    """Home Inspection Results"""

    id = models.IntegerField(primary_key=True, db_column="Inspection_ID")
    bop = models.ForeignKey(
        "LegacyNEEABOP",
        on_delete=models.CASCADE,
        null=True,
        db_column="BOP_ID",
        blank=True,
        db_constraint=False,
    )
    bop_xml = models.TextField(db_column="BOP_XML", blank=True)
    bop_heat_source = models.ForeignKey(
        "LegacyNEEABOPHeatSource",
        on_delete=models.CASCADE,
        null=True,
        db_column="BOP_Heat_Source_ID",
        blank=True,
    )
    home = models.ForeignKey(
        "LegacyNEEAHome",
        on_delete=models.CASCADE,
        null=True,
        db_column="Home_ID",
        blank=True,
        db_constraint=False,
    )
    status = models.ForeignKey(
        "LegacyNEEAStatus",
        on_delete=models.CASCADE,
        null=True,
        db_column="Status_ID",
        blank=True,
        db_constraint=False,
    )
    certification_date = models.DateTimeField(null=True, db_column="Certification_Date", blank=True)
    verification_date = models.DateTimeField(null=True, db_column="Verification_Date", blank=True)
    last_update_by = models.CharField(max_length=150, db_column="Last_Update_By", blank=True)
    last_update_date = models.DateTimeField(null=True, db_column="Last_Update_Date", blank=True)
    note = models.CharField(max_length=21000, db_column="Note", blank=True)
    performance_test_result = models.TextField(db_column="Performance_Test", blank=True)
    performance_test = models.ForeignKey(
        "LegacyNEEAPerformanceTest",
        on_delete=models.CASCADE,
        null=True,
        db_column="Performance_Test_ID",
        blank=True,
        db_constraint=False,
    )
    qa_required = models.BooleanField(default=False, db_column="QA_Required")
    qa_completed = models.BooleanField(default=False, db_column="QA_Completed")
    invoice = models.CharField(max_length=150, db_column="Invoice", blank=True)
    receipt = models.CharField(max_length=150, db_column="Receipt", blank=True)
    ischeckedout = models.IntegerField(db_column="IsCheckedOut")
    qa_start_date = models.DateTimeField(null=True, db_column="QA_Start_Date", blank=True)
    qa_lastactivity_date = models.DateTimeField(
        null=True, db_column="QA_LastActivity_Date", blank=True
    )
    qacompletedate = models.DateTimeField(null=True, db_column="QACompleteDate", blank=True)

    objects = NeeaGeneralLegacyManager()

    class Meta:
        """Non-field options"""

        verbose_name = "Legacy NEEA Inspection"
        db_table = "Inspection"
        managed = False

    def __str__(self):
        return "{} - {}".format(self.bop, self.home)

    def get_absolute_url(self):
        """Return associated url"""
        return reverse("neea_legacy_home_view", kwargs=dict(pk=self.id))

    def get_inspection_notes(self):
        """This will return the Inspection notes"""
        try:
            root = etree.fromstring(self.bop_xml.encode("utf8"))
            #        print(etree.tostring(root, pretty_print=True))
            return {
                x.attrib["name"]: x.text.strip() for x in root.xpath("//*[@type='Notes']") if x.text
            }
        except XMLSyntaxError:
            return {}

    def get_verifier_results(self):
        """This will return the Verifiers results"""
        try:
            root = etree.fromstring(self.bop_xml.encode("utf8"))
            output = {}
            for item in root.xpath("//*[@type='Check']"):
                result_dict = dict(item.attrib)
                for k, v in result_dict.items():
                    if v == "true":
                        v = True
                    if v in ["false", ""]:
                        v = False
                    result_dict[k] = v
                output[item.tag] = result_dict
            return output
        except XMLSyntaxError:
            return {}

    def get_attached_TCOs(self):
        """Get the attached TCO"""
        try:
            root = etree.fromstring(self.bop_xml.encode("utf8"))
            tco = root.xpath("//*[@name='Attached TCO']")[0]
            tco_ids = [x.attrib.get("id") for x in tco.getchildren()]
            return LegacyNEEATCO.objects.filter(id__in=tco_ids)
        except XMLSyntaxError:
            return {}
        except (IndexError, KeyError):
            return None


# noinspection PyShadowingBuiltins
class LegacyNEEAInspectionAttachments(models.Model):
    """Attachments"""

    id = models.IntegerField(primary_key=True, db_column="File_ID")
    inspection = models.ForeignKey(
        "LegacyNEEAInspection",
        on_delete=models.CASCADE,
        null=True,
        db_column="Inspection_ID",
        blank=True,
        db_constraint=False,
    )
    file_name = models.CharField(max_length=150, db_column="File_Name", blank=True)
    file_description = models.CharField(max_length=600, db_column="File_Description", blank=True)
    mime_type = models.CharField(max_length=150, db_column="Mime_Type", blank=True)
    file_size = models.CharField(max_length=60, db_column="File_Size", blank=True)
    file_binary = models.TextField(db_column="File_Binary", blank=True)

    class Meta:
        """Non-field options"""

        db_table = "Inspection_Attachments"
        managed = False


# noinspection PyShadowingBuiltins
class LegacyNEEAInspectionIncentive(models.Model):
    """Inspection Incentives"""

    id = models.IntegerField(primary_key=True, db_column="Inspection_Incentive_Id")
    inspection = models.ForeignKey(
        "LegacyNEEAInspection",
        on_delete=models.CASCADE,
        null=True,
        db_column="Inspection_ID",
        blank=True,
        db_constraint=False,
    )
    incentive = models.ForeignKey(
        "LegacyNEEAIncentive",
        on_delete=models.CASCADE,
        db_column="Incentive_ID",
        db_constraint=False,
    )
    model = models.CharField(max_length=150, db_column="Model", blank=True)
    comments = models.CharField(max_length=6144, db_column="Comments", blank=True)

    objects = NeeaGeneralLegacyManager()

    class Meta:
        """Non-field options"""

        verbose_name = "Legacy NEEA Inspection Incentive"
        db_table = "Inspection_Incentive"
        managed = False

    def __str__(self):
        return "{} ({})".format(self.incentive, self.model)

    def get_absolute_url(self):
        """Return associated url"""
        return reverse("neea_legacy_home_view", kwargs=dict(pk=self.inspection.home_id))


# noinspection PyShadowingBuiltins
class LegacyNEEAError(models.Model):
    """Errors"""

    id = models.IntegerField(primary_key=True, db_column="ID")
    error = models.CharField(max_length=255, db_column="Error")
    created_on = models.DateTimeField(default=datetime.datetime.now, editable=False)

    class Meta:
        """Non-field options"""

        db_table = "Error"
        managed = False


class PNWZone(models.Model):
    county = models.OneToOneField("geographic.County", null=True, on_delete=models.SET_NULL)
    heating_zone = models.IntegerField(choices=[(1, "hz1"), (2, "hz2"), (3, "hz3")])
    cooling_zone = models.IntegerField(choices=[(1, "cz1"), (2, "cz2"), (3, "cz3")])


class StandardProtocolCalculator(models.Model):
    objects = StandardProtocolCalculatorManager()

    home_status = models.ForeignKey("home.EEPProgramHomeStatus", on_delete=models.CASCADE)
    last_updated = models.DateTimeField(default=now)
    reports = AxisJSONField(default=dict)

    heating_fuel = models.CharField(
        max_length=8, choices=[("gas", "Gas"), ("electric", "Electric")]
    )
    heating_system_config = models.CharField(
        max_length=8,
        choices=[("central", "Central"), ("zonal", "Zonal"), ("all", "All")],
    )
    home_size = models.CharField(
        max_length=8,
        choices=[
            ("small", "Small"),
            ("medium", "Medium"),
            ("large", "Large"),
            ("all", "All"),
        ],
    )

    estar_std_refrigerators_installed = models.BooleanField(default=False, null=True)
    estar_refrigerators_installed = models.CharField(
        max_length=32, choices=NEEA_REFRIGERATOR_CHOICE_MAP, null=True
    )

    estar_dishwasher_installed = models.BooleanField(default=False)

    estar_front_load_clothes_washer_installed = models.BooleanField(default=False, null=True)
    estar_clothes_washer_installed = models.CharField(
        max_length=32, choices=NEEA_CLOTHES_WASHER_CHOICE_MAP, null=True
    )

    clothes_dryer_tier = models.CharField(
        max_length=8,
        choices=[
            ("tier2", "Tier 2"),
            ("tier3", "Tier 3"),
            ("estar", "ENERGY STAR\xae"),
        ],
        null=True,
        blank=True,
    )

    cfl_installed = models.PositiveIntegerField(default=0)
    led_installed = models.PositiveIntegerField(default=0)
    total_installed_lamps = models.PositiveIntegerField(default=0)

    smart_thermostat_installed = models.BooleanField(default=False)
    qty_shower_head_1p5 = models.PositiveIntegerField(default=0)
    qty_shower_head_1p75 = models.PositiveIntegerField(default=0)

    heating_kwh_savings = models.FloatField(default=0)
    heating_therm_savings = models.FloatField(default=0)
    cooling_kwh_savings = models.FloatField(default=0)
    cooling_therm_savings = models.FloatField(default=0)
    smart_thermostat_kwh_savings = models.FloatField(default=0)
    smart_thermostat_therm_savings = models.FloatField(default=0)
    water_heater_kwh_savings = models.FloatField(default=0)
    water_heater_therm_savings = models.FloatField(default=0)
    showerhead_kwh_savings = models.FloatField(default=0)
    showerhead_therm_savings = models.FloatField(default=0)
    lighting_kwh_savings = models.FloatField(default=0)
    lighting_therm_savings = models.FloatField(default=0)
    appliance_kwh_savings = models.FloatField(default=0)
    appliance_therm_savings = models.FloatField(default=0)
    total_kwh_savings = models.FloatField(default=0)
    total_therm_savings = models.FloatField(default=0)

    has_incentive = models.BooleanField(null=True, default=None)
    reference_home_kwh = models.FloatField(default=0)
    busbar_consumption = models.FloatField(default=0)
    busbar_savings = models.FloatField(default=0)
    pct_improvement_method = models.CharField(
        max_length=16,
        choices=(("default", "Default"), ("alternate", "Alternate")),
        default="default",
    )
    percent_improvement = models.FloatField(default=0)
    revised_percent_improvement = models.FloatField(default=0)

    total_incentive = models.FloatField(default=0)
    builder_incentive = models.FloatField(default=0)

    # Original stats
    bpa_hvac_kwh_savings = models.FloatField(default=0.0)
    hvac_kwh_incentive = models.FloatField(default=0.0)
    bpa_lighting_kwh_savings = models.FloatField(default=0.0)
    lighting_kwh_incentive = models.FloatField(default=0.0)
    bpa_water_heater_kwh_savings = models.FloatField(default=0.0)
    water_heater_kwh_incentive = models.FloatField(default=0.0)
    bpa_appliance_kwh_savings = models.FloatField(default=0.0)
    appliance_kwh_incentive = models.FloatField(default=0.0)
    bpa_windows_shell_kwh_savings = models.FloatField(default=0.0)
    windows_shell_kwh_incentive = models.FloatField(default=0.0)
    bpa_smart_thermostat_kwh_savings = models.FloatField(default=0.0)
    smart_thermostat_kwh_incentive = models.FloatField(default=0.0)
    bpa_showerhead_kwh_savings = models.FloatField(default=0.0)
    showerhead_kwh_incentive = models.FloatField(default=0.0)

    # BPA report stats
    reported_shell_windows_kwh_savings = models.FloatField(default=0.0)
    reported_shell_windows_incentive = models.FloatField(default=0.0)
    reported_hvac_waterheater_kwh_savings = models.FloatField(default=0.0)
    reported_hvac_waterheater_incentive = models.FloatField(default=0.0)
    reported_lighting_showerhead_tstats_kwh_savings = models.FloatField(default=0.0)
    reported_lighting_showerhead_tstats_incentive = models.FloatField(default=0.0)

    code_total_consumption_mmbtu = models.FloatField(default=0.0)
    improved_total_consumption_mmbtu = models.FloatField(default=0.0)
    improved_total_consumption_mmbtu_with_savings = models.FloatField(default=0.0)

    incentive_paying_organization = models.ForeignKey(
        "company.Company", null=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "Standard Protocol Calculator Result"

    @property
    def total_mmbtu_savings(self):
        return self.total_therm_savings / 10.0 + (self.total_kwh_savings * 3.412) / 1000.0

    def as_dict(self):
        builder_incentive = (
            "Builder incentive is dependent upon partner utility and managed outside of "
            "Axis. Please contact utility directly for more information."
        )

        try:
            if self.has_incentive is not None:
                builder_incentive = "${:.2f}".format(round(self.builder_incentive, 2))
        except AttributeError:
            pass

        incentive_paying_organization = None
        if self.incentive_paying_organization:
            incentive_paying_organization = self.incentive_paying_organization.slug

        estar_front_load_clothes_washer_installed = self.estar_clothes_washer_installed
        estar_std_refrigerators_installed = self.estar_refrigerators_installed

        if self.home_status.eep_program.slug == "neea-bpa":
            estar_front_load_clothes_washer_installed = (
                self.estar_front_load_clothes_washer_installed
            )
            estar_std_refrigerators_installed = self.estar_std_refrigerators_installed

        return OrderedDict(
            [
                ("home_status", self.home_status),
                ("heating_fuel", self.heating_fuel),
                ("heating_system_config", self.heating_system_config),
                ("home_size", self.home_size),
                (
                    "estar_std_refrigerators_installed",
                    estar_std_refrigerators_installed,
                ),
                ("estar_dishwasher_installed", self.estar_dishwasher_installed),
                (
                    "estar_front_load_clothes_washer_installed",
                    estar_front_load_clothes_washer_installed,
                ),
                ("clothes_dryer_tier", self.clothes_dryer_tier),
                ("cfl_installed", self.cfl_installed),
                ("led_installed", self.led_installed),
                ("total_installed_lamps", self.total_installed_lamps),
                ("smart_thermostat_installed", self.smart_thermostat_installed),
                ("qty_shower_head_1p5", self.qty_shower_head_1p5),
                ("qty_shower_head_1p75", self.qty_shower_head_1p75),
                ("heating_kwh_savings", self.heating_kwh_savings),
                ("heating_therm_savings", self.heating_therm_savings),
                ("cooling_kwh_savings", self.cooling_kwh_savings),
                ("cooling_therm_savings", self.cooling_therm_savings),
                ("smart_thermostat_kwh_savings", self.smart_thermostat_kwh_savings),
                ("smart_thermostat_therm_savings", self.smart_thermostat_therm_savings),
                ("water_heater_kwh_savings", self.water_heater_kwh_savings),
                ("water_heater_therm_savings", self.water_heater_therm_savings),
                ("showerhead_kwh_savings", self.showerhead_kwh_savings),
                ("showerhead_therm_savings", self.showerhead_therm_savings),
                ("lighting_kwh_savings", self.lighting_kwh_savings),
                ("lighting_therm_savings", self.lighting_therm_savings),
                ("appliance_kwh_savings", self.appliance_kwh_savings),
                ("appliance_therm_savings", self.appliance_therm_savings),
                ("total_kwh_savings", self.total_kwh_savings),
                ("total_therm_savings", self.total_therm_savings),
                ("total_mmbtu_savings", self.total_mmbtu_savings),
                ("has_incentive", self.has_incentive),
                ("reference_home_kwh", self.reference_home_kwh),
                ("busbar_consumption", self.busbar_consumption),
                ("busbar_savings", self.busbar_savings),
                ("pct_improvement_method", self.pct_improvement_method),
                (
                    "pretty_pct_improvement_method",
                    self.get_pct_improvement_method_display(),
                ),
                ("percent_improvement", self.percent_improvement),
                (
                    "pretty_percent_improvement",
                    "{:.2%}".format(self.percent_improvement),
                ),
                ("revised_percent_improvement", self.revised_percent_improvement),
                (
                    "pretty_revised_percent_improvement",
                    "{:.2%}".format(self.revised_percent_improvement),
                ),
                ("total_incentive", self.total_incentive),
                (
                    "pretty_total_incentive",
                    "${:.2f}".format(round(self.total_incentive, 2)),
                ),
                ("builder_incentive", self.builder_incentive),
                ("pretty_builder_incentive", builder_incentive),
                ("bpa_hvac_kwh_savings", self.bpa_hvac_kwh_savings),
                ("hvac_kwh_incentive", self.hvac_kwh_incentive),
                ("bpa_lighting_kwh_savings", self.bpa_lighting_kwh_savings),
                ("lighting_kwh_incentive", self.lighting_kwh_incentive),
                ("bpa_water_heater_kwh_savings", self.bpa_water_heater_kwh_savings),
                ("water_heater_kwh_incentive", self.water_heater_kwh_incentive),
                ("bpa_appliance_kwh_savings", self.bpa_appliance_kwh_savings),
                ("appliance_kwh_incentive", self.appliance_kwh_incentive),
                ("bpa_showerhead_kwh_savings", self.bpa_showerhead_kwh_savings),
                ("showerhead_kwh_incentive", self.showerhead_kwh_incentive),
                ("bpa_windows_shell_kwh_savings", self.bpa_windows_shell_kwh_savings),
                ("windows_shell_kwh_incentive", self.windows_shell_kwh_incentive),
                (
                    "bpa_smart_thermostat_kwh_savings",
                    self.bpa_smart_thermostat_kwh_savings,
                ),
                ("smart_thermostat_kwh_incentive", self.smart_thermostat_kwh_incentive),
                (
                    "reported_shell_windows_kwh_savings",
                    self.reported_shell_windows_kwh_savings,
                ),
                (
                    "reported_shell_windows_incentive",
                    self.reported_shell_windows_incentive,
                ),
                (
                    "reported_hvac_waterheater_kwh_savings",
                    self.reported_hvac_waterheater_kwh_savings,
                ),
                (
                    "reported_hvac_waterheater_incentive",
                    self.reported_hvac_waterheater_incentive,
                ),
                (
                    "reported_lighting_showerhead_tstats_kwh_savings",
                    self.reported_lighting_showerhead_tstats_kwh_savings,
                ),
                (
                    "reported_lighting_showerhead_tstats_incentive",
                    self.reported_lighting_showerhead_tstats_incentive,
                ),
                ("code_total_consumption_mmbtu", self.code_total_consumption_mmbtu),
                (
                    "improved_total_consumption_mmbtu",
                    self.improved_total_consumption_mmbtu,
                ),
                (
                    "improved_total_consumption_mmbtu_with_savings",
                    self.improved_total_consumption_mmbtu_with_savings,
                ),
                ("incentive_paying_organization", incentive_paying_organization),
                ("reports", self.reports),
                ("last_updated", self.last_updated),
                ("from_db", True),
            ]
        )
