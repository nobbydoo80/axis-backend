"""defaults.py - Axis"""

__author__ = "Steven K"
__date__ = "8/11/21 13:54"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import logging

from ....eep_programs.washington_code_credit import (
    BuildingEnvelope,
    FramingType,
    AirLeakageControl,
    VentilationType,
    HighEfficiencyHVACDistribution,
    FurnaceLocation,
    DuctLocation,
    DWHR,
    EfficientWaterHeating,
    HighEfficiencyHVAC,
    RenewableEnergy,
    Appliances,
)
from ....enumerations import YesNo

log = logging.getLogger(__name__)

BUILDING_ENVELOPE_OPTIONS = {
    BuildingEnvelope.NONE: {
        "wall_cavity_r_value": 21,
        "wall_continuous_r_value": 0,
        "framing_type": FramingType.INTERMEDIATE,
        "window_u_value": 0.3,
        "window_shgc": None,
        "floor_cavity_r_value": 30,
        "slab_perimeter_r_value": 10,
        "under_slab_r_value": 0,
        "ceiling_r_value": 49,
        "raised_heel": YesNo.NO,
        "total_ua_alternative": None,
        "eligible_credits": 0.0,
        "description": None,
    },
    BuildingEnvelope.OPTION_1p1: {
        "wall_cavity_r_value": 21,
        "wall_continuous_r_value": 0,
        "framing_type": FramingType.INTERMEDIATE,
        "window_u_value": 0.24,
        "window_shgc": None,
        "floor_cavity_r_value": 30,
        "slab_perimeter_r_value": 10,
        "under_slab_r_value": None,
        "ceiling_r_value": 49,
        "raised_heel": YesNo.NO,
        "total_ua_alternative": None,
        "eligible_credits": 0.5,
    },
    BuildingEnvelope.OPTION_1p2: {
        "wall_cavity_r_value": 21,
        "wall_continuous_r_value": 0,
        "framing_type": FramingType.INTERMEDIATE,
        "window_u_value": 0.2,
        "window_shgc": None,
        "floor_cavity_r_value": 30,
        "slab_perimeter_r_value": 10,
        "under_slab_r_value": None,
        "ceiling_r_value": 49,
        "raised_heel": YesNo.NO,
        "total_ua_alternative": None,
        "eligible_credits": 1.0,
    },
    BuildingEnvelope.OPTION_1p3a: {
        "wall_cavity_r_value": 21,
        "wall_continuous_r_value": 0,
        "framing_type": FramingType.INTERMEDIATE,
        "window_u_value": 0.28,
        "window_shgc": None,
        "floor_cavity_r_value": 38,
        "slab_perimeter_r_value": 10,
        "under_slab_r_value": 10,
        "ceiling_r_value": 49,
        "raised_heel": YesNo.NO,
        "total_ua_alternative": 5.0,
        "eligible_credits": 0.5,
    },
    BuildingEnvelope.OPTION_1p3b: {
        "wall_cavity_r_value": 21,
        "wall_continuous_r_value": 0,
        "framing_type": FramingType.INTERMEDIATE,
        "window_u_value": 0.30,
        "window_shgc": None,
        "floor_cavity_r_value": 30,
        "slab_perimeter_r_value": 10,
        "under_slab_r_value": None,
        "ceiling_r_value": 49,
        "raised_heel": YesNo.NO,
        "total_ua_alternative": 5.0,
        "eligible_credits": 0.5,
    },
    BuildingEnvelope.OPTION_1p4a: {
        "wall_cavity_r_value": 21,
        "wall_continuous_r_value": 4,
        "framing_type": FramingType.INTERMEDIATE,
        "window_u_value": 0.25,
        "window_shgc": None,
        "floor_cavity_r_value": 38,
        "slab_perimeter_r_value": 10,
        "under_slab_r_value": 10,
        "ceiling_r_value": 49,
        "raised_heel": YesNo.NO,
        "total_ua_alternative": 15.0,
        "eligible_credits": 1.0,
    },
    BuildingEnvelope.OPTION_1p4b: {
        "wall_cavity_r_value": 21,
        "wall_continuous_r_value": 0,
        "framing_type": FramingType.INTERMEDIATE,
        "window_u_value": 0.30,
        "window_shgc": None,
        "floor_cavity_r_value": 30,
        "slab_perimeter_r_value": 10,
        "under_slab_r_value": None,
        "ceiling_r_value": 49,
        "raised_heel": YesNo.NO,
        "total_ua_alternative": 15.0,
        "eligible_credits": 1.0,
    },
    BuildingEnvelope.OPTION_1p5a: {
        "wall_cavity_r_value": 21,
        "wall_continuous_r_value": 12,
        "framing_type": FramingType.INTERMEDIATE,
        "window_u_value": 0.22,
        "window_shgc": None,
        "floor_cavity_r_value": 38,
        "slab_perimeter_r_value": 10,
        "under_slab_r_value": 10,
        "ceiling_r_value": 49,
        "raised_heel": YesNo.YES,
        "total_ua_alternative": 30.0,
        "eligible_credits": 2.0,
    },
    BuildingEnvelope.OPTION_1p5b: {
        "wall_cavity_r_value": 21,
        "wall_continuous_r_value": 0,
        "framing_type": FramingType.INTERMEDIATE,
        "window_u_value": 0.30,
        "window_shgc": None,
        "floor_cavity_r_value": 30,
        "slab_perimeter_r_value": 10,
        "under_slab_r_value": None,
        "ceiling_r_value": 49,
        "raised_heel": YesNo.NO,
        "total_ua_alternative": 30.0,
        "eligible_credits": 2.0,
    },
    BuildingEnvelope.OPTION_1p6a: {
        "wall_cavity_r_value": 21,
        "wall_continuous_r_value": 16,
        "framing_type": FramingType.INTERMEDIATE,
        "window_u_value": 0.18,
        "window_shgc": None,
        "floor_cavity_r_value": 48,
        "slab_perimeter_r_value": 20,
        "under_slab_r_value": 20,
        "ceiling_r_value": 60,
        "raised_heel": YesNo.YES,
        "total_ua_alternative": 40.0,
        "eligible_credits": 3.0,
    },
    BuildingEnvelope.OPTION_1p6b: {
        "wall_cavity_r_value": 21,
        "wall_continuous_r_value": 0,
        "framing_type": FramingType.INTERMEDIATE,
        "window_u_value": 0.30,
        "window_shgc": None,
        "floor_cavity_r_value": 30,
        "slab_perimeter_r_value": 10,
        "under_slab_r_value": None,
        "ceiling_r_value": 49,
        "raised_heel": YesNo.NO,
        "total_ua_alternative": 40.0,
        "eligible_credits": 3.0,
    },
    BuildingEnvelope.OPTION_1p7: {
        "wall_cavity_r_value": 0,
        "wall_continuous_r_value": 0,
        "framing_type": FramingType.ADVANCED,
        "window_u_value": 0.28,
        "window_shgc": None,
        "floor_cavity_r_value": 30,
        "slab_perimeter_r_value": 10,
        "under_slab_r_value": None,
        "ceiling_r_value": 49,
        "raised_heel": YesNo.YES,
        "total_ua_alternative": None,
        "eligible_credits": 0.5,
    },
}

AIR_LEAKAGE = {
    AirLeakageControl.NONE: {
        "air_leakage_ach": 5.0,
        "ventilation_type": None,
        "hrv_asre": None,
        "eligible_credits": 0.0,
    },
    AirLeakageControl.OPTION_2p1: {
        "air_leakage_ach": 3.0,
        "ventilation_type": None,
        "hrv_asre": None,
        "eligible_credits": 0.5,
    },
    AirLeakageControl.OPTION_2p2: {
        "air_leakage_ach": 2.0,
        "ventilation_type": VentilationType.HRV_ERV,
        "hrv_asre": 65.0,
        "eligible_credits": 1.0,
    },
    AirLeakageControl.OPTION_2p3: {
        "air_leakage_ach": 1.5,
        "ventilation_type": VentilationType.HRV_ERV,
        "hrv_asre": 75.0,
        "eligible_credits": 1.5,
    },
    AirLeakageControl.OPTION_2p4: {
        "air_leakage_ach": 0.6,
        "ventilation_type": VentilationType.HRV_ERV,
        "hrv_asre": 80,
        "eligible_credits": 2.0,
    },
}

HVAC = {
    HighEfficiencyHVAC.NONE: {
        "furnace_afue": 95,
        "eligible_credits": None,
    },
    HighEfficiencyHVAC.OPTION_3p1: {
        "furnace_afue": 95,
        "eligible_credits": 1.0,
    },
    HighEfficiencyHVAC.OPTION_3p2: {
        "furnace_afue": 95,
        "eligible_credits": None,
    },
    HighEfficiencyHVAC.OPTION_3p3: {
        "furnace_afue": 95,
        "eligible_credits": None,
    },
    HighEfficiencyHVAC.OPTION_3p4: {
        "furnace_afue": 95,
        "eligible_credits": None,
    },
    HighEfficiencyHVAC.OPTION_3p5: {
        "furnace_afue": 95,
        "eligible_credits": None,
    },
    HighEfficiencyHVAC.OPTION_3p6: {
        "furnace_afue": 95,
        "eligible_credits": None,
    },
}


HVAC_DISTRIBUTION = {
    HighEfficiencyHVACDistribution.NONE: {
        "furnace_location": FurnaceLocation.UNCONDITIONED_SPACE,
        "duct_location": DuctLocation.UNCONDITIONED_SPACE,
        "eligible_credits": 0.0,
    },
    HighEfficiencyHVACDistribution.OPTION_4p1: {
        "furnace_location": FurnaceLocation.UNCONDITIONED_SPACE,
        "duct_location": DuctLocation.DEEPLY_BURIED,
        "eligible_credits": 0.5,
    },
    HighEfficiencyHVACDistribution.OPTION_4p2: {
        "furnace_location": FurnaceLocation.CONDITIONED_SPACE,
        "duct_location": DuctLocation.CONDITIONED_SPACE,
        "eligible_credits": 1.0,
    },
}

DRAIN_WATER_HEAT_RECOVER = {
    DWHR.NONE: {
        "dwhr_installed": YesNo.NO,
        "eligible_credits": 0.0,
    },
    DWHR.OPTION_5p1: {
        "dwhr_installed": YesNo.YES,
        "eligible_credits": 0.5,
    },
}

HOT_WATER = {
    EfficientWaterHeating.NONE: {
        "gas_water_heater_uef": 0.6,
        "electric_water_heater_uef": 2,
        "eligible_credits": 0.0,
    },
    EfficientWaterHeating.OPTION_5p2: {
        "gas_water_heater_uef": 0.80,
        "electric_water_heater_uef": None,
        "eligible_credits": None,
    },
    EfficientWaterHeating.OPTION_5p3: {
        "gas_water_heater_uef": 0.91,
        "electric_water_heater_uef": None,
        "eligible_credits": 1.0,
    },
    EfficientWaterHeating.OPTION_5p4: {
        "gas_water_heater_uef": None,
        "electric_water_heater_uef": 2,
        "eligible_credits": 1.5,
    },
    EfficientWaterHeating.OPTION_5p5: {
        "gas_water_heater_uef": None,
        "electric_water_heater_uef": 2.6,
        "eligible_credits": 2.0,
    },
    EfficientWaterHeating.OPTION_5p6: {
        "gas_water_heater_uef": None,
        "electric_water_heater_uef": 2.9,
        "eligible_credits": 2.5,
    },
}

RENEWABLES = {
    RenewableEnergy.NONE: {
        "eligible_credits": 0.0,
    },
    RenewableEnergy.OPTION_6p1a: {
        "eligible_credits": 1.0,
    },
    RenewableEnergy.OPTION_6p1b: {
        "eligible_credits": 2.0,
    },
    RenewableEnergy.OPTION_6p1c: {
        "eligible_credits": 3.0,
    },
}

APPLIANCES = {
    Appliances.NONE: {
        "eligible_credits": 0.0,
    },
    Appliances.OPTION_7p1: {
        "eligible_credits": 0.5,
    },
}

CEC_THERM_SAVINGS_MULTIPLIER = 34.2783728876166

INCENTIVE_PER_CODE_CREDIT_MULTIPLIER = 800.00
THERMOSTAT_INCENTIVE_VALUE = 125.00
FIREPLACE_INCENTIVE_VALUE = 200.00
VERIFIER_INCENTIVE_VALUE = 100.00
