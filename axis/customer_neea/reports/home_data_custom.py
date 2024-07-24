"""NEEA Custom Home Export"""

import logging

from axis.home.export_data import HomeDataXLSExport
from .mixins import ExtraFiltersMixin, NEEAMixin

__author__ = "mjeffrey"
__date__ = "7/25/14 11:39 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "mjeffrey",
]

log = logging.getLogger(__name__)


class NEEAHomeDataCustomExport(ExtraFiltersMixin, NEEAMixin, HomeDataXLSExport):
    """Custom Export"""

    def __init__(self, *args, **kwargs):
        kwargs["title"] = kwargs["subject"] = "NEEA Utility Export"
        kwargs["specified_columns"] = self.get_specified_columns()
        kwargs["retain_empty"] = True
        kwargs["report_on"] = [
            "neea_checklist_values",
            "home",
            "subdivision",
            "relationships",
            "simulation_advanced",
            "neea_standard_protocol_calculator",
            "checklist_answers",
        ]
        super(NEEAHomeDataCustomExport, self).__init__(*args, **kwargs)

    def get_specified_columns(self):
        """Return specified Columns"""
        return [
            "home__id",
            "home__lot_number",
            "home__street_line1",
            "home__street_line2",
            "home__city__name",
            "home__state",
            "home__zipcode",
            "home__subdivision__name",  # Subdivision Name
            "home__created_date",
            "state",
            "certification_date",  # Certification Date
            "standardprotocolcalculator__percent_improvement",  # Percent Improvement
            "standardprotocolcalculator__revised_percent_improvement",  # Percent Improvement
            "standardprotocolcalculator__pct_improvement_method",  # Percent Improvement Method Used
            "standardprotocolcalculator__total_kwh_savings",  # Estimated Annual Savings (kWh)
            "standardprotocolcalculator__total_therm_savings",  # Estimated Annual Savings (Therms)
            "builder",  # Builder
            "rater",  # Rating Company
            "electric_utility",  # Electric Utility
            "gas_utility",  # Gas Utility
            "buildinginfo__conditioned_area",  # Area of Conditioned Space (sq.ft.)
            "buildinginfo__volume",  # Volume of Conditioned Space
            "buildinginfo__number_stories",  # Floors on or Above-Grade
            "buildinginfo__number_bedrooms",  # Number of Bedroom
            "buildinginfo__type",  # Building Type
            "buildinginfo__foundation_type",  # Foundation Type
            "abovegradewall__type__continuous_insulation",
            # Above-Grade Wall Total Continuous R-value
            "window__type__u_value",  # Window Information U-Value
            "building__window_floor_ratio",  # 'window__area',   # !!!!!!!
            "roof__style",  # Roof Information Type (Attic)
            "ceilingtype__continuous_insulation",
            # Ceiling Information Continuous Insulation (R-value)
            "cfl_installed",
            "led_installed",
            "total_installed_lamps",
            "percentage_of_efficient_light_sources",
            # Comes from checklist question, replaces lightsandappliance__pct_florescent
            "mech_programmable_thermostat",  # Programmable Thermostat
            "dominant_cooling_type",  # Air Conditioning System Type
            "neea-heating_source",  # Comes from checklist question, replaces dominant_cooling_type
            "primary_hvac_type",  # Comes from checklist question, replaces dominant_cooling_type
            "dominant_heating_fuel",  # Heating Fuel Type
            "dominant_heating_efficiency",  # Heating Seasonal Equipment Efficiency
            "dominant_heating_capacity",  # Heating Rated Output Capacity
            "dominant_hot_water_type",  # Water Heating Equipment Water Heater Type
            "dominant_hot_water_fuel",  # Water Heating Equipment Fuel Type
            "dominant_hot_water_energy_factor",  # Water Heating Equipment Energy Factor
            "duct__location",  # Duct Information Location
            "ductsystem__total_leakage",  # Duct System Duct Leakage (supply and return) to outside
            "ductsystem__leakage_unit",  # Duct System Duct Leakage to outside Units
            # 'infiltration__hours_per_day',   # !!!!
            "infiltration__heating_value",  # Mechanical Ventilation Type
            "infiltration__cooling_value",  # Mechanical Ventilation Type
            "infiltration__units",
            "infiltration__mechanical_vent_type",  # Mechanical Ventilation Type
            "infiltration__mechanical_vent_cfm",  # Mechanical Ventilation Rate (cfm)
            "solarsystem__type",  # Active Solar and PV Array Solar Type System
            # Checklist Questions
        ]

    def get_column_name_map(self):
        """Allows you to customize the column names

        If value is None it is not exported - but used by other applications
        """
        return {
            "home__subdivision__name": "Subdivision Name",
            "roof__style": "Ceiling Type",  # Roof Information Type (Attic)
            "building__window_floor_ratio": "Glazing fraction (% of floor area)",
            "standardprotocolcalculator__percent_improvement": "Percent Improvement",
            "standardprotocolcalculator__revised_percent_improvement": "Alternate Percent Improvement",
            "standardprotocolcalculator__pct_improvement_method": "% Improvement method used",
            "neea-heating_source": "Primary Heating Type",
            # Comes from checklist question, replaces dominant_cooling_type
            "dominant_heating_efficiency": "Primary Heating Efficiency HSPF/AFUE",
            "dominant_heating_capacity": "Primary Heating Capacity kBtuh",
        }
