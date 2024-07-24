"""RemRate Models suitable for use by Axis """

import logging

from django.db import models

from ..managers import InfiltrationManager
from ..strings import (
    INFILTRATION_EST_TYPES,
    INFILTRATION_UNITS,
    INFILTRATION_TYPES,
    INFILTRATION_VERIFICATIONS,
    INFILTRATION_COOLING_TYPES,
)
from ..utils import get_ACH50_string_value, compare_sets

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class Infiltration(models.Model):
    """Infilt - Infiltration"""

    simulation = models.OneToOneField("Simulation", on_delete=models.CASCADE)
    building = models.OneToOneField("Building", on_delete=models.CASCADE)
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")
    _source_infiltration_number = models.IntegerField(db_column="lINInfilNo")  # Interesting all 0s
    testing_type = models.IntegerField(
        null=True, db_column="nINType", choices=INFILTRATION_EST_TYPES
    )
    heating_value = models.FloatField(null=True, db_column="fINHeatVal")
    cooling_value = models.FloatField(null=True, db_column="fINCoolVal")
    units = models.IntegerField(null=True, db_column="nINWHInfUn", choices=INFILTRATION_UNITS)
    mechanical_vent_type = models.IntegerField(
        null=True, db_column="lINMVType", choices=INFILTRATION_TYPES
    )
    mechanical_vent_cfm = models.FloatField(null=True, db_column="fINMVRate")
    sensible_recovery_efficiency = models.FloatField(null=True, db_column="fINSREff")
    hours_per_day = models.IntegerField(null=True, db_column="nINHrsDay")
    mechanical_vent_power = models.FloatField(null=True, db_column="fINMVFan")
    rating_number = models.CharField(max_length=93, db_column="sINRateNo")

    total_recovery_efficiency = models.FloatField(null=True, db_column="fINTREff")
    verification_type = models.FloatField(
        null=True, db_column="nINVerify", choices=INFILTRATION_VERIFICATIONS
    )
    shelter_class = models.IntegerField(null=True, db_column="nINShltrCl")
    cooling_type = models.IntegerField(
        null=True, db_column="nINClgVent", choices=INFILTRATION_COOLING_TYPES
    )
    ecm_fan_motor = models.IntegerField(null=True, db_column="nINFanMotor")

    annual_filtration = models.FloatField(null=True, db_column="FINANNUAL", blank=True)
    field_tested_value = models.FloatField(null=True, db_column="FINTESTED", blank=True)
    multi_family_good_air_exchange = models.IntegerField(
        null=True, db_column="NINGDAIRXMF", blank=True
    )

    no_mechanical_vent_measured = models.BooleanField(
        null=True,
        db_column="NINNOMVMSRD",
        blank=True,
        verbose_name="No Mech Vent Measured",
    )
    use_fan_watts_defaults = models.BooleanField(
        null=True,
        db_column="NINWATTDFLT",
        blank=True,
        verbose_name="Fan Watts Use Defaults",
    )

    objects = InfiltrationManager()

    def __str__(self):
        out = ""
        if self.heating_value:
            out += " Htg: {}".format(round(self.heating_value, 2))
        if self.cooling_value:
            out += " Clg: {}".format(round(self.cooling_value, 2))

        out = out.strip()
        if out:
            out += " {}".format(self.get_units_display())
        return out

    def get_ventilation_system(self):
        """Get the ventillation system"""
        if self.mechanical_vent_type:
            if self.mechanical_vent_type > 0:
                return "{}: {} cfm {} watts {} hours/day".format(
                    self.get_mechanical_vent_type_display(),
                    round(self.mechanical_vent_cfm, 0),
                    round(self.mechanical_vent_power, 0),
                    int(round(self.hours_per_day, 0)),
                )
        return None

    def get_ach50_heating_value(self):
        """Return the ACH50 value for heating"""
        return get_ACH50_string_value(
            self.heating_value, self.units, self.building.building_info.volume
        ).as_string

    def get_ach50_cooling_value(self):
        """Return the ACH50 value for cooling"""
        return get_ACH50_string_value(
            self.cooling_value, self.units, self.building.building_info.volume
        ).as_string

    def compare_to_home_status(self, home_status, **kwargs):
        """Comprare the values to the home status"""
        data_map = {1: "HRV/ERV", 2: "Exhaust", 4: "Supply side – Air Cycler "}

        items = []
        if kwargs.get("duct_leakage_ach50"):
            items += [
                (
                    self.get_verification_type_display(),
                    kwargs.get("duct_leakage_verification_type"),
                    str,
                ),
                (
                    self.get_testing_type_display(),
                    kwargs.get("duct_leakage_ach50_testing_type"),
                    str,
                ),
                (
                    self.get_units_display(),
                    kwargs.get("duct_leakage_ach50_leakage_unit"),
                    str,
                ),
                (
                    self.heating_value,
                    (
                        self.cooling_value,
                        kwargs.get("duct_leakage_ach50_heating_cooling_match")[1:],
                    ),
                    float,
                ),
                (self.heating_value, kwargs.get("duct_leakage_ach50"), float),
            ]

        try:
            ventilation_type = kwargs["ventilation_type"]
            mechanical_vent_type = data_map[self.mechanical_vent_type]
        except KeyError:
            # Ventilation type may not exist.
            # mechanical_vent_type may be present but not a valid type
            pass
        else:
            items.append((mechanical_vent_type, ventilation_type, str))

        if self.mechanical_vent_type == 4:
            if kwargs.get("mechanical_vent_type_error"):
                items.append(
                    [
                        True,
                        self.mechanical_vent_type != 4,
                        bool,
                        kwargs.get("mechanical_vent_type_error")[1],
                        "error",
                    ]
                )
        else:
            if kwargs.get("mechanical_system_exists_error"):
                items.append(
                    [
                        True,
                        self.mechanical_vent_type not in [0, None],
                        bool,
                        kwargs.get("mechanical_system_exists_error")[1],
                        "error",
                    ]
                )
            if kwargs.get("mechanical_ventilation_hours_per_day") and self.mechanical_vent_type in [
                1,
                2,
                3,
            ]:
                items.append(
                    [
                        self.hours_per_day,
                        24,
                        float,
                        kwargs.get("mechanical_ventilation_hours_per_day")[1],
                        "error",
                    ]
                )

        if kwargs.get("mechanical_ventilation_rate_error"):
            # Customer desired this to be floored.  This is a dumb decision.
            tgt = int(self.simulation.buildinginfo.ashrae_64p2_2010_mechanical_ventillation_target)
            items.append(
                [
                    self.mechanical_vent_cfm >= tgt,
                    True,
                    bool,
                    kwargs.get("mechanical_ventilation_rate_error")[1],
                    "error",
                ]
            )

        match_items = []
        for fields in items:
            try:
                cmp1, cmp2, _type, label, warning_type = fields
            except ValueError:
                try:
                    cmp1, cmp2, _type, label = fields
                    warning_type = "warning"
                except ValueError:
                    cmp1, cmp2, _type = fields
                    # This is fugly did I really do this..
                    label = cmp2[2] if len(cmp2) > 2 else "Checklist"
                    label = "{}: {}".format(label, cmp2[1])
                    cmp2 = cmp2[0]
                    warning_type = "warning"
            if cmp2 is None:
                continue

            match_items.append((cmp1, cmp2, _type, label, warning_type))
        return compare_sets(match_items)
