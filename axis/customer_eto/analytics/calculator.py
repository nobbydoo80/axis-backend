"""eps.py: Django EPS Calculation Data"""


import logging
import typing

from rest_framework.exceptions import ValidationError

from axis.customer_eto.api_v3.serializers import (
    EPS2021CalculatorSerializer,
    EPSFire2021CalculatorSerializer,
    EPS2022CalculatorSerializer,
)
from axis.customer_eto.api_v3.serializers.calculators.washington_code_credit import (
    WashingtonCodeCreditCalculatorBaseSerializer,
)
from axis.customer_eto.models import FastTrackSubmission
from axis.home.models import EEPProgramHomeStatus
from axis.home.utils import get_eps_data

__author__ = "Steven K"
__date__ = "08/30/2019 10:31"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)


class EPSFire2022CalculatorSerializer:
    pass


def get_eps_required_data(
    simulation_id: typing.Union[str, None],
    city_id: typing.Union[int, None],
    us_state: typing.Union[str, None],
    electric_utility_id: typing.Union[int, None],
    gas_utility_id: typing.Union[int, None],
    builder_id: typing.Union[int, None],
    primary_heating_equipment_type: typing.Union[str, None],
    smart_thermostat_brand: typing.Union[str, None],
    ets_annual_etsa_kwh: typing.Union[int, None],
    non_ets_annual_pv_watts: typing.Union[int, None],
    home_status_id: typing.Union[int, None],
):
    """Pulls the EPS Calculator data"""

    data = {"percent_improvement": None}

    home_status = EEPProgramHomeStatus.objects.get(id=home_status_id)
    if home_status.eep_program.slug in ["eto-2021", "eto-2021-fire", "eto-2022"]:
        project_tracker = FastTrackSubmission.objects.filter(home_status=home_status.id).first()
        if not project_tracker:
            serializer_dict = {
                "eto-2021": EPS2021CalculatorSerializer,
                "eto-2021-fire": EPSFire2021CalculatorSerializer,
                "eto-2022": EPS2022CalculatorSerializer,
            }
            serializer_class = serializer_dict.get(home_status.eep_program.slug)
            serializer = serializer_class(
                data={"home_status": home_status_id},
            )
            try:
                if serializer.is_valid(raise_exception=True):
                    project_tracker = serializer.save()
            except ValidationError:
                return data
        data["percent_improvement"] = project_tracker.percent_improvement
        if home_status.home.state == "WA":
            data["percent_improvement"] = project_tracker.percent_improvement_therms
        return data
    else:
        try:
            result = get_eps_data(EEPProgramHomeStatus.objects.get(id=home_status_id))
        except Exception as _err:
            log.info(f"Error getting eps data {_err}")
            return data

    for k in data:
        data[k] = result.get(k)
    return data


def get_washington_code_credit_calculator_specifications_data(
    # Annotations
    envelope_option: typing.Union[str, None],
    air_leakage_option: typing.Union[str, None],
    hvac_option: typing.Union[str, None],
    hvac_distribution_option: typing.Union[str, None],
    dwhr_option: typing.Union[str, None],
    water_heating_option: typing.Union[str, None],
    renewable_electric_option: typing.Union[str, None],
    appliance_option: typing.Union[str, None],
    # Checklist Responses
    conditioned_floor_area: typing.Union[int, None],
    water_heating_fuel: typing.Union[str, None],
    thermostat_type: typing.Union[str, None],
    fireplace_efficiency: typing.Union[str, None],
    wall_cavity_r_value: typing.Union[int, None],
    wall_continuous_r_value: typing.Union[int, None],
    framing_type: typing.Union[str, None],
    window_u_value: typing.Union[float, None],
    window_shgc: typing.Union[float, None],
    floor_cavity_r_value: typing.Union[int, None],
    slab_perimeter_r_value: typing.Union[int, None],
    under_slab_r_value: typing.Union[int, None],
    ceiling_r_value: typing.Union[int, None],
    raised_heel: typing.Union[str, None],
    total_ua_alternative: typing.Union[int, None],
    air_leakage_ach: typing.Union[float, None],
    ventilation_type: typing.Union[str, None],
    ventilation_brand: typing.Union[str, None],
    ventilation_model: typing.Union[str, None],
    hrv_asre: typing.Union[int, None],
    furnace_brand: typing.Union[str, None],
    furnace_model: typing.Union[str, None],
    furnace_afue: typing.Union[int, None],
    furnace_location: typing.Union[str, None],
    duct_location: typing.Union[str, None],
    duct_leakage: typing.Union[int, None],
    dwhr_installed: typing.Union[str, None],
    water_heater_brand: typing.Union[str, None],
    water_heater_model: typing.Union[str, None],
    gas_water_heater_uef: typing.Union[float, None],
    electric_water_heater_uef: typing.Union[float, None],
) -> dict:
    data = {
        "envelope_option": envelope_option,
        "air_leakage_option": air_leakage_option,
        "hvac_option": hvac_option,
        "hvac_distribution_option": hvac_distribution_option,
        "dwhr_option": dwhr_option,
        "water_heating_option": water_heating_option,
        "renewable_electric_option": renewable_electric_option,
        "appliance_option": appliance_option,
        "conditioned_floor_area": conditioned_floor_area,
        "water_heating_fuel": water_heating_fuel,
        "thermostat_type": thermostat_type,
        "fireplace_efficiency": fireplace_efficiency,
        "wall_cavity_r_value": wall_cavity_r_value,
        "wall_continuous_r_value": wall_continuous_r_value,
        "framing_type": framing_type,
        "window_u_value": window_u_value,
        "window_shgc": window_shgc,
        "floor_cavity_r_value": floor_cavity_r_value,
        "slab_perimeter_r_value": slab_perimeter_r_value,
        "under_slab_r_value": under_slab_r_value,
        "ceiling_r_value": ceiling_r_value,
        "raised_heel": raised_heel,
        "total_ua_alternative": total_ua_alternative,
        "air_leakage_ach": air_leakage_ach,
        "ventilation_type": ventilation_type,
        "ventilation_brand": ventilation_brand,
        "ventilation_model": ventilation_model,
        "hrv_asre": hrv_asre,
        "furnace_brand": furnace_brand,
        "furnace_model": furnace_model,
        "furnace_afue": furnace_afue,
        "furnace_location": furnace_location,
        "duct_leakage": duct_leakage,
        "duct_location": duct_location,
        "dwhr_installed": dwhr_installed,
        "water_heater_brand": water_heater_brand,
        "water_heater_model": water_heater_model,
        "gas_water_heater_uef": gas_water_heater_uef,
        "electric_water_heater_uef": electric_water_heater_uef,
    }
    for k in [
        "window_shgc",
        "total_ua_alternative",
        "hrv_asre",
        "gas_water_heater_uef",
        "electric_water_heater_uef",
    ]:
        if k in data and data.get(k) is None:
            data.pop(k)

    # Note this serializer will not save data.
    serializer = WashingtonCodeCreditCalculatorBaseSerializer(data=data)
    if not serializer.is_valid():
        return {
            "errors": {
                k.replace("_", " ").capitalize(): ", ".join([str(_i) for _i in v])
                for k, v in serializer.errors.items()
            }
        }
    calculator = serializer.calculator
    data = {}
    for k, spec in calculator.specifications.items():
        data[f"{k}_specification"] = {
            "specifications": [],
            "meet_requirements": spec.meet_requirements,
        }
        for _k, v in spec.data.items():
            if isinstance(v["minimum_requirement"], (list, tuple)):
                v["minimum_requirement"] = ", ".join(v["minimum_requirement"])
            data[f"{k}_specification"]["specifications"].append(v)
    return data
