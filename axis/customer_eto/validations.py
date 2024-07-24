"""validations.py - Axis"""

import logging
import math

from django.core.exceptions import ObjectDoesNotExist

from axis.home.models import EEPProgramHomeStatus
from simulation.enumerations import (
    MechanicalVentilationType,
    ResidenceType,
    Location,
    FuelType,
    SourceType,
)

from axis.customer_eto.enumerations import PrimaryHeatingEquipment2020
from simulation.models import Simulation

log = logging.getLogger(__name__)

__author__ = "Steven K"
__date__ = "8/28/20 13:49"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def get_simulation_validations(
    home_status: EEPProgramHomeStatus, simulation: Simulation, fuel_rates: list, **kwargs
) -> dict:
    """This will check our home status against simulation"""

    errors = []
    warnings = []

    if not simulation.mechanical_ventilation_systems.exists():
        errors.append("Mechanical ventilation system should exist")

    if home_status.eep_program.slug in ["eto-2020", "eto-2021", "eto-fire-2021"]:
        if simulation.mechanical_ventilation_systems.filter(
            type=MechanicalVentilationType.AIR_CYCLER
        ).exists():
            errors.append("Mechanical ventilation may not be Air Cycler")

    # Customer desired this to be the cap of this.  This is a dumb decision.
    ashrae_target = math.floor(simulation.ashrae_64p2_2010_mechanical_ventilation_target)
    if not simulation.mechanical_ventilation_systems.meets_ventilation_rate_target(ashrae_target):
        errors.append("Mechanical ventilation total CFM must meet ASHRAE 62.2 2010")

    if simulation.mechanical_ventilation_systems.exists():
        expected = {24, 4.5}
        expected_str = "24hr/day or 4.5hr/day"
        if home_status.eep_program.slug in ["eto-2020", "eto-2021", "eto-fire-2021"]:
            expected = {24}
            expected_str = "24hr/day"
        values = simulation.mechanical_ventilation_systems.values_list("hour_per_day", flat=True)
        if not set(values).issubset(expected):
            errors.append(f"Mechanical ventilation rate must be {expected_str}")

    bad_residence = [
        ResidenceType.MULTI_FAMILY_WHOLE,
        ResidenceType.DUPLEX_WHOLE,
        ResidenceType.MOBILE_HOME,
    ]
    if simulation.residence_type in bad_residence:
        msg = (
            "Single family detached, duplex single unit, townhouse, end unit, "
            "apartment or townhouse inside unit allowed"
        )
        errors.append(msg)

    if simulation.foundation_type in [Location.CONDITIONED_CRAWL_SPACE]:
        errors.append("Conditioned Crawlspaces is not allowed")

    try:
        appliances = simulation.appliances
    except ObjectDoesNotExist:
        errors.append("Missing appliances?")
        appliances = None

    if appliances and appliances.refrigerator_location == Location.UNCONDITIONED_SPACE:
        errors.append("Refrigerator location must be conditioned")
    elif appliances and appliances.refrigerator_location == Location.UNKNOWN:
        warnings.append("Refrigerator location cannot be verified (Ekotrope ok)")

    if appliances and appliances.clothes_dryer_location == Location.UNCONDITIONED_SPACE:
        errors.append("Clothes dryer location must be conditioned")
    elif appliances and appliances.clothes_dryer_location == Location.UNKNOWN:
        warnings.append("Clothes dryer location cannot be verified (Ekotrope ok)")

    if simulation.location is None:
        errors.append("Simulation has no location")
    elif home_status.home.city.county.climate_zone != simulation.location.climate_zone:
        errors.append("Climate zone does not match home")

    gas_company = home_status.get_gas_company()
    if gas_company and fuel_rates.get(gas_company.slug):
        utility_rate = simulation.utility_rates.filter(fuel=FuelType.NATURAL_GAS).last()
        if utility_rate and utility_rate.name not in fuel_rates.get(gas_company.slug):
            if not home_status.certification_date:
                errors.append("AXIS gas utility must match EPS simulation library utility")

    electric_company = home_status.get_electric_company()
    if electric_company and fuel_rates.get(electric_company.slug):
        utility_rate = simulation.utility_rates.filter(fuel=FuelType.ELECTRIC).last()
        if utility_rate and utility_rate.name not in fuel_rates.get(electric_company.slug):
            if not home_status.certification_date:
                errors.append("AXIS electric utility must match EPS simulation library utility")

    input_values = home_status.get_input_values()
    primary_heat = input_values.get("primary-heating-equipment-type")
    gas_heaters = [
        PrimaryHeatingEquipment2020.GAS_UNIT_HEATER.value,
        PrimaryHeatingEquipment2020.GAS_FURNACE.value,
        PrimaryHeatingEquipment2020.GAS_BOILER.value,
    ]
    if primary_heat and primary_heat in gas_heaters:
        if not simulation.mechanical_equipment.heaters().filter(fuel=FuelType.NATURAL_GAS).count():
            message = (
                f"Checklist identifies {primary_heat!r} but no Gas Heaters exist in simulation data"
            )
            warnings.append(message)
    ashps = [
        PrimaryHeatingEquipment2020.DUCTED_ASHP.value,
        PrimaryHeatingEquipment2020.MINI_SPLIT_DUCTED.value,
        PrimaryHeatingEquipment2020.MINI_SPLIT_MIXED.value,
    ]
    if primary_heat and primary_heat in ashps:
        if not simulation.mechanical_equipment.air_source_heat_pumps().count():
            message = (
                f"Checklist identifies {primary_heat!r} but no ASHP's exist in simulation data"
            )

            warnings.append(message)
    if primary_heat and primary_heat == PrimaryHeatingEquipment2020.GSHP.value:
        if not simulation.mechanical_equipment.ground_source_heat_pumps().count():
            message = (
                f"Checklist identifies {primary_heat!r} but no GSHP's exist in simulation data"
            )
            warnings.append(message)

    return {"errors": errors, "warnings": warnings}


def get_eto_2020_simulation_validations(
    home_status: EEPProgramHomeStatus, simulation: Simulation, **kwargs
) -> dict:
    from axis.customer_eto.calculator.eps.constants.eto_2020 import (
        ETO_2020_FUEL_RATES,
        ETO_2020_FUEL_RATES_WA_OVERRIDE,
    )

    fuel_rates = dict(ETO_2020_FUEL_RATES)
    if home_status.home.state == "WA":
        fuel_rates.update(dict(ETO_2020_FUEL_RATES_WA_OVERRIDE))

    return get_simulation_validations(home_status, simulation, fuel_rates, **kwargs)


def get_eto_2021_simulation_validations(
    home_status: EEPProgramHomeStatus, simulation: Simulation, **kwargs
) -> dict:
    from axis.customer_eto.eep_programs.eto_2021 import (
        ETO_2021_FUEL_RATES,
        ETO_2021_FUEL_RATES_WA_OVERRIDE,
    )

    fuel_rates = dict(ETO_2021_FUEL_RATES)
    if home_status.home.state == "WA":
        fuel_rates.update(dict(ETO_2021_FUEL_RATES_WA_OVERRIDE))

    return get_simulation_validations(home_status, simulation, fuel_rates, **kwargs)


def get_eto_2022_simulation_validations(
    home_status: EEPProgramHomeStatus, simulation: Simulation, **kwargs
) -> dict:
    from axis.customer_eto.eep_programs.eto_2022 import (
        ETO_2023_FUEL_RATES,
        ETO_2023_FUEL_RATES_WA_OVERRIDE,
        ETO_2022_FUEL_RATES,
        ETO_2022_FUEL_RATES_WA_OVERRIDE,
    )

    fuel_rates = dict(ETO_2023_FUEL_RATES)
    if home_status.home.state == "WA":
        fuel_rates.update(dict(ETO_2023_FUEL_RATES_WA_OVERRIDE))

    if simulation.source_type == SourceType.EKOTROPE:
        fuel_rates = dict(ETO_2022_FUEL_RATES)
        if home_status.home.state == "WA":
            fuel_rates.update(dict(ETO_2022_FUEL_RATES_WA_OVERRIDE))

    return get_simulation_validations(home_status, simulation, fuel_rates, **kwargs)
