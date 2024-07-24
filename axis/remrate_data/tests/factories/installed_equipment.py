"""installed_equipment.py: Django factories"""

import random

from .utils import random_sequence
from ...models import InstalledEquipment

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def installed_equipment_factory(simulation, building, _result_number, **kwargs):
    heater = kwargs.pop("heater", None)
    ground_source_heat_pump = kwargs.pop("ground_source_heat_pump", None)
    dual_fuel_heat_pump = kwargs.pop("dual_fuel_heat_pump", None)
    air_source_heat_pump = kwargs.pop("air_source_heat_pump", None)
    integrated_space_water_heater = kwargs.pop("integrated_space_water_heater", None)
    air_conditioner = kwargs.pop("air_conditioner", None)
    hot_water_heater = kwargs.pop("hot_water_heater", None)
    dehumidifier = kwargs.pop("dehumidifier", None)
    shared_equipment = kwargs.pop("shared_equipment", None)

    heating_load_served_pct = 0.0
    air_conditioner_load_served_pct = 0.0
    hot_water_heater_load_served_pct = 0.0
    dehumidifier_load_served_pct = 0.0
    if heater:
        heating_load_served_pct = random.randint(0, 99) + random.random()
    if air_conditioner:
        air_conditioner_load_served_pct = random.randint(0, 99) + random.random()
    if ground_source_heat_pump or air_source_heat_pump or dual_fuel_heat_pump:
        heating_load_served_pct = random.randint(0, 99) + random.random()
        air_conditioner_load_served_pct = random.randint(0, 99) + random.random()
    if shared_equipment:
        if shared_equipment.type == 1:
            heating_load_served_pct = random.randint(0, 99) + random.random()
        if shared_equipment.type == [2, 3]:
            air_conditioner_load_served_pct = random.randint(0, 99) + random.random()
        if shared_equipment.type == 4:
            heating_load_served_pct = random.randint(0, 99) + random.random()
            air_conditioner_load_served_pct = random.randint(0, 99) + random.random()
    if dehumidifier:
        dehumidifier_load_served_pct = random.randint(0, 99) + random.random()

    greater_16p1 = tuple(simulation.numerical_version) >= (16, 1, 0)

    clothes_washer_load_served_pct = 0 if greater_16p1 else None
    dishwasher_load_served_pct = 0 if greater_16p1 else None
    dehumidifier_load_served_pct = dehumidifier_load_served_pct if greater_16p1 else None
    mechanical_ventilation_heating_lsp = 0 if greater_16p1 else None
    mechanical_ventilation_cooling_lsp = 0 if greater_16p1 else None
    hot_water_units_served = 0 if greater_16p1 else None
    preconditioned_shared_mv = 0 if greater_16p1 else None

    if hot_water_heater:
        hot_water_heater_load_served_pct = random.randint(0, 99) + random.random()
        clothes_washer_load_served_pct = random.randint(0, 100) if greater_16p1 else None
        dishwasher_load_served_pct = random.randint(0, 100) if greater_16p1 else None

    locations = [1, 2, 3, 4, 5]
    if simulation.numerical_version >= (16, 1):
        locations = [1, 3, 4, 5, 6, 7, 8]
    return InstalledEquipment.objects.get_or_create(
        simulation=simulation,
        _result_number=_result_number,
        ground_source_heat_pump=ground_source_heat_pump,
        air_source_heat_pump=air_source_heat_pump,
        integrated_space_water_heater=integrated_space_water_heater,
        dual_fuel_heat_pump=dual_fuel_heat_pump,
        shared_equipment=shared_equipment,
        heater=heater,
        air_conditioner=air_conditioner,
        hot_water_heater=hot_water_heater,
        dehumidifier=dehumidifier,
        building=building,
        location=random.choice(locations),
        air_conditioner_load_served_pct=air_conditioner_load_served_pct,
        heating_load_served_pct=heating_load_served_pct,
        hot_water_heater_load_served_pct=hot_water_heater_load_served_pct,
        clothes_washer_load_served_pct=clothes_washer_load_served_pct,
        dishwasher_load_served_pct=dishwasher_load_served_pct,
        dehumidifier_load_served_pct=dehumidifier_load_served_pct,
        mechanical_ventilation_heating_load_served_pct=mechanical_ventilation_heating_lsp,
        mechanical_ventilation_cooling_load_served_pct=mechanical_ventilation_cooling_lsp,
        hot_water_units_served=hot_water_units_served,
        preconditioned_shared_mechanical_ventilation=preconditioned_shared_mv,
        qty_installed=1,
        defaults=kwargs,
    )[0]
