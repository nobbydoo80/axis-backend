"""hvac_commissioning.py - Axis"""

__author__ = "Steven K"
__date__ = "1/4/22 15:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.db import models

log = logging.getLogger(__name__)


class CommissionRefrigerantChargeMethod(models.TextChoices):
    NA = 0, "Not Applicable"
    PISTON = 1, "Piston/Cap.Tube"
    TXV = 2, "TXV/EEV"
    WEIGH_IN = 3, "Weigh-in"


class CommissionGradeChoices(models.TextChoices):
    GRADE_1 = 1, "I"
    GRADE_2 = 2, "II"
    GRADE_3 = 3, "III"


class HVACCommissioning(models.Model):
    """HVAC Commissioning HVACCX"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _result_number = models.IntegerField(null=True, db_column="lBldgRunNo", blank=True)
    _source_commissioning_number = models.IntegerField(null=True, db_column="lHvacCxNo", blank=True)

    duct_system_number = models.IntegerField(null=True, db_column="nDuctSysNo", blank=True)
    heating_equipment_number = models.IntegerField(null=True, db_column="nHtgEquipNo", blank=True)
    cooling_equipment_number = models.IntegerField(null=True, db_column="nClgEquipNo", blank=True)

    # Total Duct Leakage
    total_duct_leakage_grade = models.IntegerField(
        null=True,
        db_column="nTotDuctLeakGrade",
        blank=True,
        choices=CommissionGradeChoices.choices,
        help_text="Duct Grade",
    )
    total_duct_leakage_exemption = models.BooleanField(
        null=True,
        db_column="bTotDuctLeakExcep",
        blank=True,
        help_text="ACCA 310 Total Duct Leakage test exemption claimed",
    )
    total_duct_leakage_grade_1_met = models.BooleanField(
        null=True,
        db_column="bTotDuctLeakGrdIMet",
        blank=True,
        help_text="Grade I met using ANSI/ACCA5QA",
    )
    total_duct_leakage = models.FloatField(null=True, db_column="fTotDuctLeakage", blank=True)

    # Blower Fan Airflow
    blower_airflow_grade = models.IntegerField(
        null=True,
        db_column="nBFAirflowGrade",
        blank=True,
        choices=CommissionGradeChoices.choices,
        help_text="Airflow Grade",
    )
    blower_airflow_exemption = models.BooleanField(
        null=True,
        db_column="bBFAirflowException",
        blank=True,
    )
    blower_airflow_design_specified = models.IntegerField(
        null=True,
        db_column="nBFAirflowDesignSpec",
        blank=True,
        help_text="Design Specified airflow Qdesign (CFM)",
    )
    blower_airflow_operating_condition = models.IntegerField(
        null=True, db_column="nBFAirflowOpCond", blank=True, help_text="Measured airflow Qop (CFM)"
    )

    # Blower Fan Watts
    blower_watt_draw_grade = models.IntegerField(
        null=True,
        db_column="nBFWattDrawGrade",
        blank=True,
        help_text="Watt Draw Grade",
        choices=CommissionGradeChoices.choices,
    )
    blower_airflow_watt_draw = models.IntegerField(
        null=True,
        db_column="nBFWattDraw",
        blank=True,
        help_text="Power at operating conditions (Watts)",
    )
    blower_fan_efficiency = models.FloatField(null=True, db_column="fBFEffic", blank=True)

    # Refrigerant Charge
    refrigerant_charge_single_package_system = models.BooleanField(
        null=True,
        db_column="bRCSinglePkgSystem",
        blank=True,
        help_text="Selected system is a Single Packaged System",
    )
    refrigerant_charge_onboard_diagnostic = models.BooleanField(
        null=True,
        db_column="bRCOnboardDiagnostic",
        blank=True,
        help_text="On-board diagnostic or independent verification report met",
    )
    refrigerant_charge_test_method = models.IntegerField(
        null=True,
        db_column="nRCTestMethod",
        blank=True,
        choices=CommissionRefrigerantChargeMethod.choices,
        help_text="Test Method",
    )
    refrigerant_charge_grade = models.IntegerField(
        null=True,
        db_column="nRCGrade",
        blank=True,
        choices=CommissionGradeChoices.choices,
        help_text="Charge Grade",
    )

    difference_DTD = models.FloatField(
        null=True, db_column="fDiffDTD", blank=True, help_text="Diff DTD (F)"
    )
    difference_CTOA = models.FloatField(null=True, db_column="fDiffCTOA", blank=True)
    deviation = models.FloatField(null=True, db_column="fDeviation", blank=True)
    total_refrigerant_weight = models.FloatField(
        null=True,
        db_column="fRptdRefrigWeight",
        blank=True,
        help_text="Total Reported Refrigerant Weight",
    )
    rating_number = models.CharField(max_length=93, db_column="sRateNo", blank=True)
