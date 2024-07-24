"""Examine input methods"""


import logging

from . import lookups
from ..base import BaseCascadingSelectMethod

__author__ = "Autumn Valenta"
__date__ = "2018-10-08 1:49 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]

log = logging.getLogger(__name__)


CHARACTERISTICS_LABEL = "Characteristics"


class CascadingFurnacePickerMethod(BaseCascadingSelectMethod):
    """TRC Furance filter widget."""

    labels = ["Brand Name", "Model Number", CHARACTERISTICS_LABEL]
    source = lookups.FURNACE_LOOKUPS
    display_format_short = "{brand_name} {model_number}"
    display_format = "{brand_name}; {model_number}; {characteristics}"
    leaf_display_format = ", ".join(
        [
            "Capacity={capacity_mbtuh} MBtuh",
            "AFUE={afue}%",
            "Eae={eae_kwh_yr} kWh/yr",
            "ECM={ecm}",
            "HP={motor_hp}",
            "Fan={ventilation_fan_watts}W",
        ]
    )


class CascadingHeatPumpPickerMethod(BaseCascadingSelectMethod):
    """TRC Heat Pump filter widget."""

    labels = ["Brand Name", "Outdoor Model Number", "Indoor Model Number", CHARACTERISTICS_LABEL]
    source = lookups.HEAT_PUMP_LOOKUPS
    display_format_short = "{brand_name} {outdoor_model_number} / {indoor_model_number}"
    display_format = "{brand_name}; {outdoor_model_number}/{indoor_model_number}; {characteristics}"
    leaf_display_format = ", ".join(
        [
            "Capacity (17F)={capacity_17f_kbtuh} kBtuh",
            "Capacity (47F)={capacity_47f_kbtuh} kBtuh",
            "HSPF={hspf}",
            "Cooling Capacity={cooling_capacity_kbtuh} kBTUh",
            "SEER={seer}",
            "HP={motor_hp}",
            "Fan={ventilation_fan_watts}W",
        ]
    )


class CascadingWaterHeaterPickerMethod(BaseCascadingSelectMethod):
    """TRC Water heater filter widget."""

    labels = ["Brand Name", "Model Number", CHARACTERISTICS_LABEL]
    source = lookups.WATER_HEATER_LOOKUPS
    display_format_short = "{brand_name} {model_number}"
    display_format = "{brand_name}; {model_number}; {characteristics}"
    leaf_display_format = ", ".join(
        [
            "Capacity={capacity}",
            "EF={energy_factor}",
            "UEF/CCE={uef_cce}",
            "Converted EF={converted_ef}",
        ]
    )


class CascadingRefrigeratorPickerMethod(BaseCascadingSelectMethod):
    """TRC Refrigerator filter widget."""

    labels = ["Brand Name", "Model Number", CHARACTERISTICS_LABEL]
    source = lookups.REFRIGERATOR_LOOKUPS
    display_format_short = "{brand_name} {model_number}"
    display_format = "{brand_name}; {model_number}; {characteristics}"
    leaf_display_format = "AEU={annual_energy_use_kwh_yr} kWh/yr"


class CascadingDishwasherPickerMethod(BaseCascadingSelectMethod):
    """TRC Dishwasher filter widget."""

    labels = ["Brand Name", "Model Number", CHARACTERISTICS_LABEL]
    source = lookups.DISHWASHER_LOOKUPS
    display_format_short = "{brand_name} {model_number}"
    display_format = "{brand_name}; {model_number}; {characteristics}"
    leaf_display_format = "AEU={annual_energy_use_kwh_yr} kWh/yr"


class CascadingClothesWasherPickerMethod(BaseCascadingSelectMethod):
    """TRC Clothes Washer filter widget."""

    labels = ["Brand Name", "Model Number", CHARACTERISTICS_LABEL]
    source = lookups.CLOTHES_WASHER_LOOKUPS
    display_format_short = "{brand_name} {model_number}"
    display_format = "{brand_name}; {model_number}; {characteristics}"
    leaf_display_format = ", ".join(
        [
            "AEU={annual_energy_use_kwh_yr} kWh/yr",
            "IMEF={integrated_modified_energy_factor}",
            "Volume={volume_cu_ft} cu.ft.",
            "Electric Rate={electric_rate}",
            "Gas Rate={gas_rate}",
            "Annual Cost={annual_cost}",
        ]
    )


class CascadingClothesDryerPickerMethod(BaseCascadingSelectMethod):
    """TRC Clothes Dryer filter widget."""

    labels = ["Brand Name", "Model Number", CHARACTERISTICS_LABEL]
    source = lookups.CLOTHES_DRYER_LOOKUPS
    display_format_short = "{brand_name} {model_number}"
    display_format = "{brand_name}; {model_number}; {characteristics}"
    leaf_display_format = "CEF={combined_energy_factor}"


class CascadingBalancedVentilationPickerMethod(BaseCascadingSelectMethod):
    """TRC Balance Ventilation filter widget."""

    labels = ["Brand Name", "Model Number", CHARACTERISTICS_LABEL]
    source = lookups.VENTILATION_BALANCED_LOOKUPS
    display_format_short = "{brand_name} {model_number}"
    display_format = "{brand_name}; {model_number}; {characteristics}"
    leaf_display_format = ", ".join(
        [
            "Net Airflow={net_airflow_cfm} CFM",
            "Power Consumption={power_consumption_watts} watts",
            "ASRE={asre}%",
        ]
    )


class CascadingExhaustVentilationPickerMethod(BaseCascadingSelectMethod):
    """TRC Exhaust Ventilation filter widget."""

    labels = ["Brand Name", "Model Number", CHARACTERISTICS_LABEL]
    source = lookups.VENTILATION_EXHAUST_LOOKUPS
    display_format_short = "{brand_name} {model_number}"
    display_format = "{brand_name}; {model_number}; {characteristics}"
    leaf_display_format = ", ".join(
        [
            "SP={sp}",
            "Speed={speed_cfm} (CFM)",
            "Input power={input_power_watts} (watts)",
        ]
    )
