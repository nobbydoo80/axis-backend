"""legacy_simulation.py - Axis"""

__author__ = "Steven K"
__date__ = "10/14/21 14:22"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from axis.remrate_data.models import Simulation

log = logging.getLogger(__name__)


class EPSReportLegacySimulationSerializer(serializers.ModelSerializer):
    conditioned_area = serializers.SerializerMethodField()
    construction_year = serializers.SerializerMethodField()
    electric_unit_cost = serializers.SerializerMethodField()
    gas_unit_cost = serializers.SerializerMethodField()
    insulated_walls = serializers.SerializerMethodField()
    insulated_floors = serializers.SerializerMethodField()
    efficient_windows = serializers.SerializerMethodField()
    efficient_lighting = serializers.SerializerMethodField()
    water_heater_efficiency = serializers.SerializerMethodField()
    heating_efficiency = serializers.SerializerMethodField()
    envelope_tightness = serializers.SerializerMethodField()

    class Meta:
        """Meta Options"""

        model = Simulation
        fields = (
            "conditioned_area",
            "construction_year",
            "electric_unit_cost",
            "gas_unit_cost",
            "insulated_walls",
            "insulated_floors",
            "efficient_windows",
            "efficient_lighting",
            "water_heater_efficiency",
            "heating_efficiency",
            "envelope_tightness",
        )

    def to_internal_value(self, data):
        raise NotImplementedError("Un-supported Read-Only")

    def get_conditioned_area(self, instance: Simulation):
        return instance.building.building_info.conditioned_area

    def get_construction_year(self, instance: Simulation):
        return instance.building.building_info.year_built

    def get_electric_unit_cost(self, instance: Simulation) -> float:
        rate_data = instance.block_set.get_first_fuel_rate_dict()
        try:
            return round(rate_data["Electric"][0], 2)
        except (KeyError, ObjectDoesNotExist):
            return 0.0

    def get_gas_unit_cost(self, instance: Simulation) -> float:
        rate_data = instance.block_set.get_first_fuel_rate_dict()
        try:
            return round(rate_data["Natural gas"][0], 2)
        except (KeyError, ObjectDoesNotExist):
            return 0.0

    def get_insulated_walls(self, instance: Simulation) -> str:
        try:
            value = instance.abovegradewall_set.get_r_value_for_largest()
            return f"R-{value:.0f}"
        except (ObjectDoesNotExist, AttributeError):
            return ""

    def get_insulated_floors(self, instance: Simulation) -> str:
        try:
            value = instance.framefloor_set.get_r_value_for_largest()
            return f"R-{value:.0f}"
        except (ObjectDoesNotExist, AttributeError, TypeError):
            try:
                value = instance.slab_set.get_dominant_underslab_r_value()
                return f"R-{value:.0f}"
            except (ObjectDoesNotExist, AttributeError, TypeError):
                pass
        return ""

    def get_efficient_windows(self, instance: Simulation) -> str:
        try:
            value = instance.window_set.get_dominant_values()["u_value"]
            return f"U-{value:.2f}"
        except (ObjectDoesNotExist, AttributeError, ValueError, TypeError):
            pass
        return ""

    def get_efficient_lighting(self, instance: Simulation) -> str:
        value = 0
        try:
            _value = instance.lightsandappliance.pct_interior_led
            value += _value if _value is not None else 0.0
        except (ObjectDoesNotExist, AttributeError, ValueError):
            pass
        try:
            _value = instance.lightsandappliance.pct_interior_cfl
            value += _value if _value is not None else 0.0
        except (ObjectDoesNotExist, AttributeError, TypeError):
            pass
        return f"{value:.1f} %"

    def get_water_heater_efficiency(self, instance: Simulation) -> str:
        try:
            equip = instance.installedequipment_set.get_dominant_values(instance.id)[instance.id]
            return "{energy_factor} EF".format(**equip["dominant_hot_water"])
        except (ObjectDoesNotExist, AttributeError):
            pass
        return ""

    def get_heating_efficiency(self, instance: Simulation) -> str:
        try:
            equip = instance.installedequipment_set.get_dominant_values(instance.id)[instance.id]
            return "{efficiency:.1f} {units_pretty}".format(**equip["dominant_heating"])
        except (ObjectDoesNotExist, AttributeError):
            pass
        except ValueError:
            return "{efficiency} {units_pretty}".format(**equip["dominant_heating"])
        return ""

    def get_envelope_tightness(self, instance: Simulation) -> str:
        try:
            return "{} {}".format(
                instance.infiltration.heating_value,
                instance.infiltration.get_units_display(),
            )
        except (ObjectDoesNotExist, AttributeError):
            pass
        return ""
