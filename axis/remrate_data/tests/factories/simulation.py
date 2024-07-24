"""simulation.py: Django factories"""

import datetime
import logging
import random
import re
from collections import defaultdict

from django.apps import apps

from axis.remrate.tests.factories import remrate_user_factory

from ...models import Simulation

from .above_grade_wall import above_grade_wall_factory
from .air_source_heat_pump import air_source_heat_pump_factory
from .air_conditioner import air_conditioner_factory
from .building import building_factory
from .building_info import building_info_factory
from .dehumidifier import dehumidifier_factory
from .door import door_factory
from .duct_system import duct_system_factory
from .energystar import energystar_factory
from .frame_floor import frame_floor_factory
from .fuel_summary import fuel_summary_factory
from .foundation_wall import foundation_wall_factory
from .general_mechanical_equipment import general_mechanical_equipment_factory
from .ground_source_heat_pump import ground_source_heat_pump_factory
from .heater import heater_factory
from .hers import hers_factory
from .hot_water_distribution import hot_water_distribution_factory
from .hot_water_heater import hot_water_heater_factory
from .hvac_commissioning import hvac_commissioning_factory
from .iecc import iecc_factory
from .infiltration import infiltration_factory
from .installed_equipment import installed_equipment_factory
from .joist import joist_factory
from .lights_and_appliance import lights_and_appliance_factory
from .mechanical_ventilation import mechanical_ventilation_factory
from .project import project_factory
from .results import results_factory
from .site import site_factory
from .roof import roof_factory
from .shared_equipment import shared_equipment_factory
from .skylight import skylight_factory
from .solar_system import solar_system_factory
from .utility_rate import utility_rate_factory
from .window import window_factory
from .utils import pop_kwargs, random_digits


__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

log = logging.getLogger(__name__)
app = apps.get_app_config("remrate_data")


def simulation_factory(only_basic: bool = False, **kwargs) -> Simulation:
    """A simulation factory.  get_or_create based on the field '_source_result_number'"""
    blg_file = kwargs.pop("blg_file", None)

    version = kwargs.pop("version", "16.3.2")

    export_type = kwargs.pop("export_type", 1)
    number_of_runs = kwargs.pop("number_of_runs", 0)

    company = kwargs.pop("company", None)
    remrate_user = kwargs.pop("remrate_user", None)
    energystar = kwargs.pop("energystar", None)
    iecc = kwargs.pop("iecc", None)
    hers = kwargs.pop("hers", None)
    building_info = kwargs.pop("building_info", None)
    building = kwargs.pop("building", None)
    project = kwargs.pop("project", None)
    solar_system = kwargs.pop("solar_system", None)
    site = kwargs.pop("site", None)
    results = kwargs.pop("result", None)
    infiltration = kwargs.pop("infiltration", None)

    lightsandappliance = kwargs.pop("lightsandappliance", None)
    fuel_summary = kwargs.pop("fuel_summary", None)

    heating = kwargs.pop("heating", None)
    heating_count = kwargs.pop("heating_count", 1)
    heating_kwargs = pop_kwargs("heating__", kwargs)

    air_conditioning = kwargs.pop("air_conditioning", None)
    air_conditioning_count = kwargs.pop("air_conditioning_count", 1)
    air_conditioning_kwargs = pop_kwargs("air_conditioning__", kwargs)

    air_source_heat_pump = kwargs.pop("air_source_heat_pump", None)
    air_source_heat_pump_count = kwargs.pop("air_source_heat_pump_count", 0)
    air_source_heat_pump_kwargs = pop_kwargs("air_source_heat_pump__", kwargs)

    ground_source_heat_pump = kwargs.pop("ground_source_heat_pump", None)
    ground_source_heat_pump_count = kwargs.pop("ground_source_heat_pump_count", 0)
    ground_source_heat_pump_kwargs = pop_kwargs("ground_source_heat_pump__", kwargs)

    hot_water = kwargs.pop("hot_water", None)
    hot_water_count = kwargs.pop("hot_water_count", 1)
    hot_water_kwargs = pop_kwargs("hot_water__", kwargs)

    dehumidifier = kwargs.pop("dehumidifier", None)
    dehumidifier_count = kwargs.pop("dehumidifier_count", 1)
    dehumidifier_kwargs = pop_kwargs("dehumidifier__", kwargs)

    general_mechanical = kwargs.pop("general_mechanical", None)
    duct_system_kwargs = pop_kwargs("duct_system__", kwargs)

    above_grade_walls = kwargs.pop("above_grade_wall", None)
    above_grade_wall_count = kwargs.pop("above_grade_wall_count", 3)
    above_grade_wall_kwargs = pop_kwargs("above_grade_wall__", kwargs)

    foundation_walls = kwargs.pop("foundation_walls", None)
    foundation_wall_count = kwargs.pop("foundation_wall_count", 3)
    foundation_wall_kwargs = pop_kwargs("foundation_wall__", kwargs)

    frame_floors = kwargs.pop("frame_floors", None)
    frame_floors_count = kwargs.pop("frame_floors_count", 3)
    frame_floors_kwargs = pop_kwargs("frame_floor__", kwargs)

    joists = kwargs.pop("joists", None)
    joist_count = kwargs.pop("joist_count", 1)
    joist_kwargs = pop_kwargs("joist__", kwargs)

    roofs = kwargs.pop("roofs", None)
    roof_count = kwargs.pop("roof_count", 3)
    roof_kwargs = pop_kwargs("roof__", kwargs)

    windows = kwargs.pop("windows", None)
    window_count = kwargs.pop("window_count", 4)
    window_kwargs = pop_kwargs("window__", kwargs)

    skylights = kwargs.pop("skylights", None)
    skylight_count = kwargs.pop("skylight_count", 0)
    skylight_kwargs = pop_kwargs("skylight__", kwargs)

    doors = kwargs.pop("doors", None)
    door_count = kwargs.pop("door_count", 3)
    door_kwargs = pop_kwargs("door__", kwargs)

    hot_water_distribution = kwargs.pop("hot_water_distribution", None)
    hot_water_distribution_kwargs = pop_kwargs("hot_water_distribution__", kwargs)

    mechanical_ventilation_systems = kwargs.pop("mechanical_ventilation", None)
    mechanical_ventilation_count = kwargs.pop(
        "mechanical_ventilation_count", random.choice([1, 1, 2])
    )
    mechanical_ventilation_kwargs = pop_kwargs("mechanical_ventilation__", kwargs)

    shared_equipment = kwargs.pop("shared_equipment", None)
    shared_equipment_count = kwargs.pop("shared_equipment_count", 0)
    shared_equipment_kwargs = pop_kwargs("shared_equipment__", kwargs)

    commission_hvac = kwargs.pop("commission_hvac", False)
    hvac_commissioning_kwargs = pop_kwargs("hvac_commissioning__", kwargs)

    energystar_kwrgs = {}
    iecc_kwrgs = {}
    hers_kwrgs = {}
    building_info_kwrgs = {}
    lightsandappliance_kwrgs = {}
    project_kwrgs = {}
    solar_system_kwrgs = {}
    site_kwrgs = {}
    building_kwrgs = {}
    general_mechanical_kwrgs = {}
    infiltration_kwargs = {}
    results_kwargs = {}
    fuel_summary_kwargs = {}

    kwrgs = {
        "_source_result_number": int(random_digits(6)),
        "simulation_date": datetime.datetime.now(datetime.timezone.utc),
        "version": version,
        "export_type": export_type,
        "number_of_runs": number_of_runs,
        "flavor": kwargs.pop("flavor", "rate"),
        "udrh_filename": kwargs.pop("udrh_filename", None),
        "udrh_checksum": kwargs.pop("udrh_checksum", None),
    }

    def get_kwargs(field_prefix: str, **additional_kwargs):
        kwrgs = {}

        for k in list(kwargs.keys()):
            if k.startswith(field_prefix):
                kwrgs[re.sub(field_prefix, "", k)] = kwargs.pop(k)

        for k in additional_kwargs.keys():
            kwrgs[k] = additional_kwargs.get(k)

        return kwrgs

    if not company:
        company_kwrgs = get_kwargs("company__")
        kwrgs["company"] = app.rater_organization_factory(**company_kwrgs)
    else:
        kwrgs["company"] = company

    if not remrate_user and remrate_user_factory:
        remrate_user_kwrgs = get_kwargs("remrate_user__", company=kwrgs["company"])
        kwrgs["remrate_user"] = remrate_user_factory(**remrate_user_kwrgs)
    else:
        kwrgs["remrate_user"] = remrate_user

    if not energystar:
        energystar_kwrgs = get_kwargs("energystar__")
    if not hers:
        hers_kwrgs = get_kwargs("hers__")
    if not iecc:
        iecc_kwrgs = get_kwargs("iecc__")

    if not building:
        building_kwrgs = get_kwargs(
            "building__",
            company=kwrgs["company"],
            remrate_user=kwrgs["remrate_user"],
        )
    if not building_info:
        building_info_kwrgs = get_kwargs("building_info__")
    if not project:
        project_kwrgs = get_kwargs("project__")
    if not solar_system:
        solar_system_kwrgs = get_kwargs("solar_system__")
    if not site:
        site_kwrgs = get_kwargs("site__")
    if not lightsandappliance:
        lightsandappliance_kwrgs = get_kwargs("lightsandappliance__")
    if not fuel_summary:
        fuel_summary_kwargs = get_kwargs("fuel_summary__")
    if not results:
        results_kwargs = get_kwargs("results__")
    if not infiltration:
        infiltration_kwargs = get_kwargs("infiltration__")
    if not general_mechanical:
        general_mechanical_kwrgs = get_kwargs("general_mechanical__")

    kwrgs.update(kwargs)
    _source_result_number = kwrgs.pop("_source_result_number")

    sim, create = Simulation.objects.get_or_create(
        _source_result_number=_source_result_number, defaults=kwrgs
    )

    if create:
        if not building:
            building = building_factory(
                simulation=sim, _result_number=_source_result_number, **building_kwrgs
            )
        if only_basic:
            return sim

        if not energystar:
            energystar_factory(
                simulation=sim, _result_number=_source_result_number, **energystar_kwrgs
            )
        if not hers:
            hers_factory(simulation=sim, _result_number=_source_result_number, **hers_kwrgs)

        if not iecc:
            iecc_factory(simulation=sim, _result_number=_source_result_number, **iecc_kwrgs)

        if not building_info:
            building_info = building_info_factory(
                simulation=sim,
                _result_number=_source_result_number,
                _building_number=building._source_building_number,
                # blg_data=rem_data["building_info"],
                **building_info_kwrgs,
            )

        building.building_info = building_info
        building.save()

        if not project:
            project_factory(
                building=building,
                _result_number=_source_result_number,
                # blg_data=rem_data["project_info"],
                **project_kwrgs,
            )
        if not solar_system:
            solar_system_factory(
                simulation=sim,
                building=building,
                _result_number=_source_result_number,
                _building_number=building._source_building_number,
                **solar_system_kwrgs,
            )
        if not site:
            site_factory(
                simulation=sim,
                _result_number=_source_result_number,
                # blg_data=rem_data["site_location_data"],
                **site_kwrgs,
            )

        utility_rate_factory(
            simulation=sim,
            _result_number=_source_result_number,
            # blg_data=rem_data["utility_rate_data"],
        )

        if above_grade_walls is None:
            for wall_idx in range(above_grade_wall_count):
                above_grade_wall_factory(
                    simulation=sim, building=building, **above_grade_wall_kwargs
                )

        if foundation_walls is None:
            for wall_idx in range(foundation_wall_count):
                foundation_wall_factory(simulation=sim, building=building, **foundation_wall_kwargs)

        if frame_floors is None:
            for frame_floors_idx in range(frame_floors_count):
                frame_floor_factory(simulation=sim, **frame_floors_kwargs)

        if joists is None:
            for joist_idx in range(joist_count):
                joist_factory(simulation=sim, **joist_kwargs)

        if roofs is None:
            for roof_idx in range(roof_count):
                roof_factory(simulation=sim, **roof_kwargs)

        if windows is None:
            for window_idx in range(window_count):
                window_kwargs["wall_count"] = above_grade_wall_count + foundation_wall_count
                window_factory(simulation=sim, building=building, **window_kwargs)

        if skylights is None:
            for skylight_idx in range(skylight_count):
                skylight_kwargs["roof_count"] = roof_count
                skylight_factory(simulation=sim, building=building, **skylight_kwargs)

        if doors is None:
            for door_idx in range(door_count):
                door_kwargs["wall_count"] = above_grade_wall_count + foundation_wall_count
                door_factory(simulation=sim, building=building, **door_kwargs)

        if not lightsandappliance:
            lights_and_appliance_factory(
                simulation=sim,
                building=building,
                _result_number=_source_result_number,
                _building_number=building._source_building_number,
                # blg_data=rem_data["lights_and_appliances"],
                **lightsandappliance_kwrgs,
            )
        duct_systems, equip_id = [], -1
        if not heating:
            _blg_data = {}
            # if rem_data.get("mechanical_equipment", {}).get("equipment", {}).get("instances", []):
            #     instances = rem_data["mechanical_equipment"]["equipment"]["instances"]
            #     _blg_data = next((x for x in instances if x["library_type"] == 1), {})
            if _blg_data or heating_count:
                heater = heater_factory(
                    simulation=sim,
                    _result_number=_source_result_number,
                    _source_heater_number=1,
                    blg_data=_blg_data.get("type", {}),
                    **heating_kwargs,
                )
                equip = installed_equipment_factory(
                    simulation=sim,
                    building=building,
                    heater=heater,
                    _result_number=_source_result_number,
                    _building_number=building._source_building_number,
                    _source_equipment_number=heater._source_heater_number,
                    _heater_number=heater.id,
                    system_type=1,
                    heating_load_served_pct=60,
                    qty_installed=1,
                )
                assert equip.heater == heater
                equip_id += 1
                if heater.type in [1, 5, 6, 7]:
                    duct_systems.append({"heating_equipment_number": equip_id})

        if not hot_water:
            _blg_data = {}
            # if rem_data.get("mechanical_equipment", {}).get("equipment", {}).get("instances", []):
            #     instances = rem_data["mechanical_equipment"]["equipment"]["instances"]
            #     _blg_data = next((x for x in instances if x["library_type"] == 3), {})
            if _blg_data or hot_water_count:
                hot_water = hot_water_heater_factory(
                    simulation=sim,
                    _result_number=_source_result_number,
                    _source_hot_water_heater_number=1,
                    blg_data=_blg_data.get("type", {}),
                    **hot_water_kwargs,
                )
                equip = installed_equipment_factory(
                    simulation=sim,
                    building=building,
                    hot_water_heater=hot_water,
                    _result_number=_source_result_number,
                    _building_number=building._source_building_number,
                    _source_equipment_number=hot_water._source_hot_water_heater_number,
                    _hot_water_heater_number=hot_water.id,
                    system_type=3,
                    hot_water_heater_load_served_pct=100,
                    qty_installed=1,
                )
                assert equip.hot_water_heater == hot_water
                equip_id += 1
        if not air_conditioning:
            _blg_data = {}
            # if rem_data.get("mechanical_equipment", {}).get("equipment", {}).get("instances", []):
            #     instances = rem_data["mechanical_equipment"]["equipment"]["instances"]
            #     _blg_data = next((x for x in instances if x["library_type"] == 2), {})
            if _blg_data or air_conditioning_count:
                air_conditioning = air_conditioner_factory(
                    simulation=sim,
                    _result_number=_source_result_number,
                    _source_air_conditioner_number=1,
                    blg_data=_blg_data.get("type", {}),
                    **air_conditioning_kwargs,
                )
                equip = installed_equipment_factory(
                    simulation=sim,
                    building=building,
                    air_conditioner=air_conditioning,
                    _result_number=_source_result_number,
                    _building_number=building._source_building_number,
                    _source_equipment_number=air_conditioning._source_air_conditioner_number,
                    _air_conditioner_number=air_conditioning.id,
                    system_type=2,
                    air_conditioner_load_served_pct=90,
                    qty_installed=1,
                )
                assert equip.air_conditioner == air_conditioning
                equip_id += 1
                found = False
                for idx, item in enumerate(duct_systems[:]):
                    if not item.keys():
                        continue
                    if "cooling_equipment_number" not in item:
                        duct_systems[idx]["cooling_equipment_number"] = equip_id
                        found = True
                if not found:
                    duct_systems.append({"cooling_equipment_number": equip_id})
        if not air_source_heat_pump:
            _blg_data = {}
            # if rem_data.get("mechanical_equipment", {}).get("equipment", {}).get("instances", []):
            #     instances = rem_data["mechanical_equipment"]["equipment"]["instances"]
            #     _blg_data = next((x for x in instances if x["library_type"] == 4), {})
            if _blg_data or air_source_heat_pump_count:
                air_source_heat_pump = air_source_heat_pump_factory(
                    simulation=sim,
                    _result_number=_source_result_number,
                    _source_air_source_heat_pump_number=1,
                    **air_source_heat_pump_kwargs,
                )
                equip = installed_equipment_factory(
                    simulation=sim,
                    building=building,
                    air_source_heat_pump=air_source_heat_pump,
                    _result_number=_source_result_number,
                    _building_number=building._source_building_number,
                    _source_equipment_number=air_source_heat_pump._source_air_source_heat_pump_number,
                    _air_source_heat_pump_number=air_source_heat_pump.id,
                    system_type=4,
                    heating_load_served_pct=10,
                    air_conditioner_load_served_pct=10,
                    qty_installed=air_source_heat_pump_count,
                )
                assert equip.air_source_heat_pump == air_source_heat_pump
                equip_id += 1
                duct_systems.append(
                    {"heating_equipment_number": equip_id, "cooling_equipment_number": equip_id}
                )
        if not ground_source_heat_pump:
            _blg_data = {}
            # if rem_data.get("mechanical_equipment", {}).get("equipment", {}).get("instances", []):
            #     instances = rem_data["mechanical_equipment"]["equipment"]["instances"]
            #     _blg_data = next((x for x in instances if x["library_type"] == 5), {})
            if _blg_data or ground_source_heat_pump_count:
                ground_source_heat_pump = ground_source_heat_pump_factory(
                    simulation=sim,
                    _result_number=_source_result_number,
                    _source_ground_source_heat_pump_number=1,
                    **ground_source_heat_pump_kwargs,
                )
                equip = installed_equipment_factory(
                    simulation=sim,
                    building=building,
                    ground_source_heat_pump=ground_source_heat_pump,
                    _result_number=_source_result_number,
                    _building_number=building._source_building_number,
                    _source_equipment_number=ground_source_heat_pump._source_ground_source_heat_pump_number,
                    _ground_source_heat_pump_number=ground_source_heat_pump.id,
                    system_type=5,
                    heating_load_served_pct=10,
                    air_conditioner_load_served_pct=10,
                    qty_installed=ground_source_heat_pump_count,
                )
                assert equip.ground_source_heat_pump == ground_source_heat_pump
                equip_id += 1
                duct_systems.append(
                    {"heating_equipment_number": equip_id, "cooling_equipment_number": equip_id}
                )
        if not shared_equipment and shared_equipment_count:
            system_types = [1, 2, 3]
            if ground_source_heat_pump:
                system_types.append(4)
            system_type = random.choice(system_types)
            if system_type == 4:
                shared_equipment_kwargs["ground_source_heat_pump"] = ground_source_heat_pump
            shared_equipment = shared_equipment_factory(
                simulation=sim,
                _result_number=_source_result_number,
                _source_shared_equipment_number=1,
                **shared_equipment_kwargs,
            )
            equip = installed_equipment_factory(
                simulation=sim,
                building=building,
                shared_equipment=shared_equipment,
                _result_number=_source_result_number,
                _building_number=building._source_building_number,
                _source_equipment_number=shared_equipment._source_shared_equipment_number,
                _shared_equipment_number=shared_equipment.id,
                system_type=8,
                qty_installed=shared_equipment_count,
            )
            assert equip.shared_equipment == shared_equipment
            equip_id += 1
        if not dehumidifier and dehumidifier_count:
            dehumidifier = dehumidifier_factory(
                simulation=sim,
                _result_number=_source_result_number,
                _source_humidifier_number=equip_id,
                **dehumidifier_kwargs,
            )
            if dehumidifier:
                equip = installed_equipment_factory(
                    simulation=sim,
                    building=building,
                    dehumidifier=dehumidifier,
                    _result_number=_source_result_number,
                    _building_number=building._source_building_number,
                    _source_equipment_number=dehumidifier._source_humidifier_number,
                    _dehumidifier_number=dehumidifier.id,
                    system_type=9,
                    dehumidifier_load_served_pct=10,
                    qty_installed=dehumidifier_count,
                )
                assert equip.dehumidifier == dehumidifier
                equip_id += 1

        if not general_mechanical:
            _general_mechanical = general_mechanical_equipment_factory(
                simulation=sim,
                _result_number=_source_result_number,
                _building_number=building._source_building_number,
                _source_equipment_number=1,
                # blg_data=rem_data["mechanical_equipment"],
                **general_mechanical_kwrgs,
            )

        for idx, duct_system in enumerate(duct_systems):
            ds_kw = duct_system_kwargs.copy()
            ds_kw.update(duct_system)
            ds = duct_system_factory(simulation=sim, **ds_kw)
            if commission_hvac:
                ds_kw.update(hvac_commissioning_kwargs)
                hvac_commissioning_factory(
                    simulation=sim,
                    duct_system=ds,
                    _source_commissioning_number=idx,
                    _result_number=_source_result_number,
                    duct_system_number=ds._source_duct_system_number,
                    **ds_kw,
                )

        if not hot_water_distribution:
            hot_water_distribution_factory(simulation=sim, **hot_water_distribution_kwargs)

        if not fuel_summary:
            fuel_summary = fuel_summary_factory(
                simulation=sim, _result_number=_source_result_number, **fuel_summary_kwargs
            )

        if not results:
            results_factory(
                simulation=sim,
                _result_number=_source_result_number,
                fuel_summary=fuel_summary,
                **results_kwargs,
            )

        if not infiltration:
            infiltration_factory(
                simulation=sim,
                _result_number=_source_result_number,
                building=building,
                _building_number=building._source_building_number,
                # blg_data=rem_data["infiltration_ventilation"],
                **infiltration_kwargs,
            )
        if not mechanical_ventilation_systems:
            for _i in range(mechanical_ventilation_count):
                mechanical_ventilation_factory(
                    simulation=sim,
                    _result_number=_source_result_number,
                    _building_number=building._source_building_number,
                    **mechanical_ventilation_kwargs,
                )

    return sim
