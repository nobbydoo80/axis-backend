"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import DuctSystemManager
from ..strings import (
    LEAKAGE_TYPES,
    INFILTRATION_UNITS,
    LEAKAGE_ESTIMATE_TYPES,
    LEAKAGE_TIGHTNESS_TESTS,
    DUCT_SYSTEM_INPUT_LEAKAGE_TYPES,
    DUCT_SYSTEM_LEAKAGE_TO_OUTSIDE_TYPES,
    DUCT_SYSTEM_LEAKAGE_TEST_TYPES,
)

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class DuctSystem(models.Model):
    """DuctSystem - Duct Systems"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    building = models.ForeignKey("Building", on_delete=models.CASCADE)

    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    _source_duct_system_number = models.IntegerField(db_column="lDSDSNo")
    rating_number = models.CharField(max_length=93, db_column="sDSRateNo", blank=True)

    # Duct Surface Area Frame
    supply_area = models.FloatField(null=True, db_column="fDSSupArea", help_text="Supply")
    return_area = models.FloatField(null=True, db_column="fDSRetArea", help_text="Return")

    # Location Tab
    name = models.CharField(max_length=93, db_column="szDSName", blank=True, help_text="Name")
    heating_equipment_number = models.IntegerField(
        null=True, db_column="lDSHtgNo", help_text="Htg Equip"
    )
    cooling_equipment_number = models.IntegerField(
        null=True, db_column="lDSClgNo", help_text="Clg Equip"
    )
    number_of_return_registers = models.IntegerField(
        null=True, db_column="lDSRegis", help_text="# Return Grills"
    )
    conditioned_floor_area = models.FloatField(
        null=True, db_column="fDSCFArea", help_text="Sq. Feet Served"
    )

    # Leakage Tab
    duct_leakage_input_type = models.IntegerField(
        null=True,
        db_column="nDSInpType",
        blank=True,
        choices=DUCT_SYSTEM_INPUT_LEAKAGE_TYPES,
        help_text="Leakage Input",
    )
    leakage_unit = models.IntegerField(
        null=True, db_column="nDSDLeakUn", choices=INFILTRATION_UNITS, help_text="Units of Measure"
    )
    no_building_cavities_used_as_ducts = models.BooleanField(
        null=True,
        db_column="nDSIsDucted",
        blank=True,
        help_text="No Building cavities used as ducts",
    )
    leakage_test_type = models.IntegerField(
        db_column="nDSTestType",
        choices=DUCT_SYSTEM_LEAKAGE_TEST_TYPES,
        blank=True,
        null=True,
        help_text="Test Type",
    )

    # Leakage To Outside Frame
    duct_leakage_leakage_to_outside_type = models.IntegerField(
        null=True,
        db_column="nDSLtOType",
        blank=True,
        choices=DUCT_SYSTEM_LEAKAGE_TO_OUTSIDE_TYPES,
        help_text="Radio Button Leakage to Outside",
    )
    total_leakage = models.FloatField(null=True, db_column="fDSDLeakTo")
    supply_leakage = models.FloatField(null=True, db_column="fDSDLeakSu")
    return_leakage = models.FloatField(null=True, db_column="fDSDLeakRe")

    # Total Duct Leakage Frame
    leakage_tightness_test = models.IntegerField(
        null=True,
        db_column="nDSDLeakTT",
        choices=LEAKAGE_TIGHTNESS_TESTS,
        help_text="Duct Test Conditions",
    )
    total_real_leakage = models.FloatField(
        null=True, db_column="fDSDLeakRTo", help_text="Total Duct Leakage"
    )

    # Field Test Frame (Activated via Input Type of Threshold)
    field_test_leakage_to_outside = models.FloatField(
        null=True, db_column="fDSTestLtO", blank=True, help_text="Final LtO Total"
    )
    field_test_total_duct_leakage = models.FloatField(
        null=True, db_column="fDSTestDL", blank=True, help_text="Final Total DL"
    )

    # Test Exemptions
    iecc_test_exemption = models.BooleanField(
        null=True, db_column="nDSIECCEx", blank=True, help_text="IECC"
    )
    resnet_test_exemption = models.BooleanField(
        null=True, db_column="nDSRESNETEx", blank=True, help_text="RESNET 2019"
    )
    energy_star_test_exemption = models.BooleanField(
        null=True, db_column="nDSESTAREx", blank=True, help_text="ENERGY STAR LtO"
    )

    # Hmmmm..  OLD?
    leakage_type = models.IntegerField(null=True, db_column="nDSDLeakTy", choices=LEAKAGE_TYPES)
    leakage_estimate = models.IntegerField(
        null=True, db_column="lDSDLeakET", choices=LEAKAGE_ESTIMATE_TYPES
    )
    total_real_leakage_unit = models.IntegerField(
        null=True, db_column="nDSDLeakRUN", choices=INFILTRATION_UNITS
    )
    leakage_test_exemption = models.BooleanField(default=False, db_column="nDSDLeakTEx")

    distribution_system_efficiency = models.FloatField(null=True, db_column="fDSDSE", blank=True)

    objects = DuctSystemManager()

    def __str__(self):
        return "{} {}".format(round(self.total_leakage, 2), self.get_leakage_type_display())

    def get_duct_leakage(self):
        """Return the duct leakage"""
        return "{} Total Leakage {} (S {} /R {})".format(
            self.get_leakage_type_display(),
            self.total_leakage,
            self.supply_leakage,
            self.return_leakage,
        )
