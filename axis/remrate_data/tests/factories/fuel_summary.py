"""fuel_summary.py: Django factories"""

from random import random, choice

from ...models import FuelSummary

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def fuel_summary_factory(simulation, _result_number, **kwargs):
    base = {
        "simulation": simulation,
        "_result_number": _result_number,
        "total_cost": 0,
        "heating_consumption": 0,
        "cooling_consumption": 0,
        "hot_water_consumption": 0,
        "lights_and_appliances_consumption": 0,
        "rating_number": "",
        "photo_voltaics_consumption": 0,
        "total_consumption": 0,
    }

    gas_systems = base.copy()
    gas_systems.update({"fuel_type": 1, "fuel_units": 4})

    electric_systems = base.copy()
    electric_systems.update({"fuel_type": 4, "fuel_units": 1})

    gas_consumption, electric_consumption = 0, 0

    if kwargs.get("gas_cost"):
        gas_systems["total_cost"] = kwargs.get("gas_cost")
    if kwargs.get("electric_cost"):
        electric_systems["total_cost"] = kwargs.get("electric_cost")

    if kwargs.get("gas_heating_consumption"):
        gas_systems["heating_consumption"] = kwargs.get("gas_heating_consumption")
        gas_consumption += gas_systems["heating_consumption"]
    if kwargs.get("electric_heating_consumption"):
        electric_systems["heating_consumption"] = kwargs.get("electric_heating_consumption")
        electric_consumption += electric_systems["heating_consumption"]

    if kwargs.get("gas_hot_water_consumption"):
        gas_systems["hot_water_consumption"] = kwargs.get("gas_hot_water_consumption")
        gas_consumption += gas_systems["hot_water_consumption"]
    if kwargs.get("electric_hot_water_consumption"):
        electric_systems["hot_water_consumption"] = kwargs.get("electric_hot_water_consumption")
        electric_consumption += electric_systems["hot_water_consumption"]

    if kwargs.get("cooling_consumption"):
        electric_systems["cooling_consumption"] = kwargs.get("cooling_consumption")
        electric_consumption += electric_systems["cooling_consumption"]
    if kwargs.get("lights_and_appliances_consumption"):
        electric_systems["lights_and_appliances_consumption"] = kwargs.get(
            "lights_and_appliances_consumption"
        )
        electric_consumption += electric_systems["lights_and_appliances_consumption"]

    if gas_consumption:
        gas_systems["total_consumption"] = gas_consumption
        FuelSummary.objects.create(**gas_systems)

    if electric_consumption:
        electric_systems["total_consumption"] = electric_consumption
        FuelSummary.objects.create(**electric_systems)

    # Heating
    heating = random() + choice([2, 3, 4])
    hot_water = random() + choice([0, 1, 2])
    lights_and_appliances = random() + choice([0, 1, 2])
    FuelSummary.objects.create(
        simulation=simulation,
        _result_number=_result_number,
        fuel_type=4,
        fuel_units=7,
        heating_consumption=heating,
        cooling_consumption=0.0,
        hot_water_consumption=hot_water,
        lights_and_appliances_consumption=lights_and_appliances,
        total_cost=heating + hot_water + lights_and_appliances,
        total_consumption=heating + hot_water + lights_and_appliances,
    )

    cooling = random() + choice([2, 3, 4])
    hot_water = random() + choice([0, 1, 2])
    lights_and_appliances = random() + choice([0, 1, 2])
    FuelSummary.objects.create(
        simulation=simulation,
        _result_number=_result_number,
        fuel_type=4,
        fuel_units=8,
        heating_consumption=heating,
        cooling_consumption=cooling,
        hot_water_consumption=hot_water,
        lights_and_appliances_consumption=lights_and_appliances,
        total_cost=heating + hot_water + lights_and_appliances,
        total_consumption=heating + hot_water + lights_and_appliances,
    )

    return FuelSummary.objects.filter(simulation=simulation)
