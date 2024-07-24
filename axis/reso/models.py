"""models.py: Django reso"""


import logging

from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from localflavor.us.models import USStateField
from localflavor.us.us_states import US_STATES
from simple_history.models import HistoricalRecords

from axis.remrate_data.strings import FOUNDATION_TYPES

__author__ = "Steven Klass"
__date__ = "07/23/17 09:15"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)

STANDARD_ENERGY_DATA_SOURCES = (
    (1, "REM/Rate® Energy Model"),
    (2, "Ekotrope Energy Model"),
    (3, ""),
)

STANDARD_UNITS = ((1, "Square Feet"), (2, "Square Meters"))

GREEN_BUILDING_VERIFICATION_TYPES = (
    (1, "Certified Passive House"),
    (2, "ENERGY STAR Certified Homes"),
    (3, "EnerPHit"),
    (4, "HERS Index Score"),
    (5, "Home Energy Score"),
    (6, "Home Energy Upgrade Certificate of Energy Efficiency Improvements"),
    (7, "Home Energy Upgrade Certificate of Energy Efficiency Performance"),
    (8, "Home Performance with ENERGY STAR"),
    (9, "Indoor airPLUS"),
    (10, "LEED For Homes"),
    (11, "Living Building Challenge"),
    (12, "NGBS New Construction"),
    (13, "NGBS Small Projects Remodel"),
    (14, "NGBS Whole-Home Remodel"),
    (15, "PHIUS+"),
    (16, "WaterSense"),
    (17, "Zero Energy Ready Home"),
)

RESO_COOLING_CHOICES = (
    (1, "Air conditioner"),
    (2, "Air-source heat pump"),
    (3, "Ground-source heat pump"),
    (4, "Evaporative cooler"),
    (90, "ARI 330/Closed Loop Ground-source heat pump"),
    (91, "ARI 325/Open Loop Ground-source heat pump"),
    (92, "Dual Fuel heat Pump"),
    (33, "Integrated Space Water Heater"),
)
INV_RESO_COOLING_CHOICES = ((v, k) for k, v in RESO_COOLING_CHOICES)

RESO_HEATER_CHOICES = (
    (1, "Fuel-fired air distribution heater"),
    (2, "Fuel-fired hydronic distribution heater"),
    (3, "Fuel-fired unit heater"),
    (4, "Fuel-fired unvented unit heater"),
    (5, "Electric baseboard or radiant heater"),
    (6, "Electric air distribution"),
    (7, "Electric hydronic distribution"),
    (8, "Air-source heat pump"),
    (9, "Ground-source heat pump"),
    (90, "ARI 330/Closed Loop Ground-source heat pump"),
    (91, "ARI 325/Open Loop Ground-source heat pump"),
    (92, "Dual Fuel heat Pump"),
    (33, "Integrated Space Water Heater"),
)
INV_RESO_HEATER_CHOICES = ((v, k) for k, v in RESO_HEATER_CHOICES)

STATES = [(idx, name, "{}".format(label)) for idx, (name, label) in enumerate(US_STATES)]
US_STATE_CHOICES = ((x[0], x[1]) for x in STATES)


class ResoHomeManager(models.Manager):
    pass


class ResoHome(models.Model):
    ListingKeyNumeric = models.AutoField(primary_key=True)

    AboveGradeFinishedArea = models.FloatField(blank=True, null=True)
    AboveGradeFinishedAreaSource = models.IntegerField(
        blank=True, null=True, choices=STANDARD_ENERGY_DATA_SOURCES
    )
    AboveGradeFinishedAreaUnits = models.IntegerField(blank=True, null=True, choices=STANDARD_UNITS)

    Basement = models.CharField(
        validators=[validate_comma_separated_integer_list], choices=FOUNDATION_TYPES, max_length=64
    )

    BuilderModel = models.CharField(max_length=50)
    BuilderName = models.CharField(max_length=50)

    BuildingAreaTotal = models.FloatField(blank=True, null=True)
    BuildingAreaSource = models.IntegerField(
        blank=True, null=True, choices=STANDARD_ENERGY_DATA_SOURCES
    )
    BuildingAreaUnits = models.IntegerField(blank=True, null=True, choices=STANDARD_UNITS)

    City = models.ForeignKey("geographic.City", blank=True, null=True, on_delete=models.SET_NULL)

    # ConstructionMaterials = models.ManyToManyRel(ResoConstructionMaterials)
    #
    Cooling = models.CharField(
        validators=[validate_comma_separated_integer_list],
        blank=True,
        null=True,
        choices=RESO_COOLING_CHOICES,
        max_length=64,
    )
    CoolingYN = models.BooleanField(null=True)

    GreenBuildingVerificationType = models.CharField(
        validators=[validate_comma_separated_integer_list],
        blank=True,
        null=True,
        choices=GREEN_BUILDING_VERIFICATION_TYPES,
        max_length=64,
    )

    CountyOrParish = models.ForeignKey(
        "geographic.County", blank=True, null=True, on_delete=models.SET_NULL
    )
    # DirectionFaces = models.IntegerField(blank=True, null=True, choices=DIRECTION_FACES)
    #
    # Electric = models.ManyToManyRel(ResoElectric)
    ElectricExpense = models.FloatField(blank=True, null=True)
    ElectricOnPropertyYN = models.BooleanField(null=True)
    #
    # Elevation = models.FloatField(blank=True, null=True)
    # ElevationUnits = models.IntegerField(blank=True, null=True, choices=STANDARD_UNITS)
    #
    # FoundationArea = models.FloatField(blank=True, null=True)
    # FoundationAreaUnits = models.IntegerField(blank=True, null=True, choices=STANDARD_UNITS)
    #
    # # Gas = models.ManyToManyRel(ResoElectric)
    GasExpense = models.FloatField(blank=True, null=True)
    GasOnPropertyYN = models.BooleanField(null=True)

    #
    Heating = models.CharField(
        validators=[validate_comma_separated_integer_list],
        blank=True,
        null=True,
        choices=RESO_HEATER_CHOICES,
        max_length=64,
    )
    HeatingYN = models.BooleanField(null=True)

    Latitude = models.FloatField(null=True, blank=True)
    Longitude = models.FloatField(null=True, blank=True)

    # NewConstructionYN = models.BooleanField(null=True)

    PostalCode = models.CharField(max_length=10, null=True, blank=True)

    # PropertyType = models.IntegerField(blank=True, null=True, choices=PROPERTY_TYPES)
    StateOrProvince = USStateField(null=True, blank=True)

    Stories = models.IntegerField(
        null=True,
        blank=True,
    )
    StoriesTotal = models.IntegerField(
        null=True,
        blank=True,
    )

    SubdivisionName = models.CharField(max_length=50)
    # Utilities = models.ForeignKey(ResoUtilities)

    YearBuilt = models.IntegerField(null=True, blank=True)
    YearBuiltSource = models.IntegerField(
        blank=True, null=True, choices=STANDARD_ENERGY_DATA_SOURCES
    )

    # Green Data

    # Non-RESO Fields
    AddressLine1 = models.CharField(max_length=128, blank=True, null=True)
    AddressLine2 = models.CharField(max_length=128, blank=True, null=True)

    home = models.OneToOneField("home.Home", on_delete=models.CASCADE)
    latest_home_status = models.ForeignKey("home.EEPProgramHomeStatus", on_delete=models.CASCADE)
    objects = ResoHomeManager()

    history = HistoricalRecords()

    # # Django Aliases
    # id = property(ListingKeyNumeric)
    # above_grade_finished_area = property(AboveGradeFinishedArea)
    # above_grade_finished_area_source = property(AboveGradeFinishedAreaSource)
    # above_grade_finished_area_units = property(AboveGradeFinishedAreaUnits)
    # basement = property(Basement)
    # builder_model = property(BuilderModel)
    # builder_name = property(BuilderName)
    # building_area_total = property(BuildingAreaTotal)
    # building_area_source = property(BuildingAreaSource)
    # building_area_units = property(BuildingAreaUnits)
    # city = property(City)
    # county = property(CountyOrParish)
    # latitude = property(Latitude)
    # longitude = property(Longitude)
    # zipcode = property(PostalCode)
    # state = property(StateOrProvince)
    # stories = property(Stories)
    # stories_total = property(StoriesTotal)
    # subdivision_name = property(SubdivisionName)
    # year_built = property(YearBuilt)
    # year_built_source = property(YearBuiltSource)
    #

    def __str__(self):
        return "%s %s, %s" % (self.City.name, self.StateOrProvince, self.PostalCode)


class ResoGreenVerificationManager(models.Manager):
    pass


class ResoGreenVerification(models.Model):
    ListingKeyNumeric = models.ForeignKey(
        ResoHome, related_name="GreenVerification", on_delete=models.CASCADE
    )
    GreenBuildingVerificationType = models.IntegerField(choices=GREEN_BUILDING_VERIFICATION_TYPES)
    GreenVerificationBody = models.CharField(max_length=64, blank=True, null=True)
    GreenVerificationDate = models.DateTimeField(null=True, blank=True)
    GreenVerificationMetric = models.CharField(max_length=64, blank=True, null=True)
    GreenVerificationRating = models.CharField(max_length=64, blank=True, null=True)
    GreenVerificationSource = models.CharField(max_length=64, blank=True, null=True)
    GreenVerificationStatus = models.CharField(max_length=64, blank=True, null=True)
    GreenVerificationURL = models.CharField(max_length=128, blank=True, null=True)

    qualifying_home_statuses = models.ManyToManyField("home.EEPProgramHomeStatus")

    objects = ResoGreenVerificationManager()
    history = HistoricalRecords()

    # Django Aliases
    #
    class Meta:
        unique_together = ("ListingKeyNumeric", "GreenBuildingVerificationType")
