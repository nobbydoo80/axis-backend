"""RemRate Models suitable for use by Axis """


import logging

from django.db import models

from ..managers import GeneralMechanicalEquipmentManager
from ..strings import VENT_TYPES, DUCT_LOCATIONS, DUCT_LEAKAGE, INFILTRATION_UNITS, QUALITATIVE_TYPE

__author__ = "Steven Klass"
__date__ = "06/10/2019 11:03"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


class GeneralMechanicalEquipment(models.Model):
    """Equip - General Mechanical Equipment"""

    simulation = models.ForeignKey("Simulation", on_delete=models.CASCADE)
    _source_equipment_number = models.IntegerField(db_column="lEIEINo")
    _result_number = models.IntegerField(db_column="lBldgRunNo")
    _building_number = models.IntegerField(db_column="lBldgNo")

    heating_set_point = models.FloatField(null=True, db_column="fEIHSetPnt")
    cooling_set_point = models.FloatField(null=True, db_column="fEICSetPnt")
    setback_thermostat = models.BooleanField(default=False, db_column="nEISBThrm")
    setup_thermostat = models.BooleanField(default=False, db_column="nEISUThrm")
    vent_type = models.IntegerField(
        null=True, db_column="nEIVentTyp", blank=True, choices=VENT_TYPES
    )

    setback_schedule = models.FloatField(null=True, db_column="nEISBSch", blank=True)
    setback_temperature = models.FloatField(null=True, db_column="fEISBTemp", blank=True)
    duct_location_1 = models.IntegerField(
        null=True, db_column="nEIDuctLoc", blank=True, choices=DUCT_LOCATIONS
    )
    duct_location_2 = models.IntegerField(
        null=True, db_column="nEIDuctLo2", blank=True, choices=DUCT_LOCATIONS
    )
    duct_location_3 = models.IntegerField(
        null=True, db_column="nEIDuctLo3", blank=True, choices=DUCT_LOCATIONS
    )
    duct_insulation_1 = models.FloatField(null=True, db_column="fEIDuctIns", blank=True)
    duct_insulation_2 = models.FloatField(null=True, db_column="fEIDuctIn2", blank=True)
    duct_insulation_3 = models.FloatField(null=True, db_column="fEIDuctIn3", blank=True)
    duct_supply_vs_total_supply_area_1 = models.FloatField(
        null=True, db_column="fEIDuctSup", blank=True
    )
    duct_supply_vs_total_supply_area_2 = models.FloatField(
        null=True, db_column="fEIDuctSu2", blank=True
    )
    duct_supply_vs_total_supply_area_3 = models.FloatField(
        null=True, db_column="fEIDuctSu3", blank=True
    )
    duct_return_vs_total_return_area_1 = models.FloatField(
        null=True, db_column="fEIDuctRet", blank=True
    )
    duct_return_vs_total_return_area_2 = models.FloatField(
        null=True, db_column="fEIDuctRe2", blank=True
    )
    duct_return_vs_total_return_area_3 = models.FloatField(
        null=True, db_column="fEIDuctRe3", blank=True
    )
    qualitative_duct_leakage_estimate = models.IntegerField(
        null=True, db_column="nEIDuctLk", choices=DUCT_LEAKAGE
    )
    quantitative_duct_leakage_units = models.IntegerField(
        null=True, db_column="nEIDTUNITS", choices=INFILTRATION_UNITS
    )
    quantitative_duct_leakage = models.FloatField(null=True, db_column="fEIDTLKAGE")
    using_qualitative = models.IntegerField(
        null=True, db_column="nEIDTQUAL", choices=QUALITATIVE_TYPE
    )
    rating_number = models.CharField(max_length=93, db_column="sEIRateNo", blank=True)
    capacity_weighting_heating = models.BooleanField(
        null=True, db_column="nEIHTGCAPWT", verbose_name="Capacity Weighting Heating"
    )
    capacity_weighting_cooling = models.BooleanField(
        null=True, db_column="nEICLGCAPWT", verbose_name="Capacity Weighting Cooling"
    )
    capacity_weighting_hot_water = models.BooleanField(
        null=True, db_column="nEIDHWCAPWT", verbose_name="Capacity Weighting Hot Water"
    )
    capacity_weighting_dehumidifier = models.BooleanField(
        null=True, db_column="nEIDHUCAPWT", verbose_name="Capacity Weighting Dehumidifier"
    )
    whf_flow = models.FloatField(null=True, db_column="fEIWHFFlow", blank=True)
    whf_watts = models.FloatField(null=True, db_column="FEIWHFWatts", blank=True)

    objects = GeneralMechanicalEquipmentManager()

    def __str__(self):
        return "Programmable Thermostat Heat={} Cool={} ({}/{})".format(
            "Yes" if self.setback_thermostat else "No",
            "Yes" if self.setback_thermostat else "No",
            self.heating_set_point,
            self.cooling_set_point,
        )

    @property
    def has_programmable_thermostat(self):
        """Does this have a programmable thermostat"""

        return all([self.setup_thermostat, self.setback_thermostat])
