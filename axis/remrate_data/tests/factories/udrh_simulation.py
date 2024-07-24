"""udrh_simulation.py: Django factories"""
import datetime
import random

from .simulation import simulation_factory
from .utils import random_sequence
from ...models import Simulation

__author__ = "Steven K"
__date__ = "01/09/2020 11:10"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]


def udrh_simulation_factory(**kwargs):
    suffix = kwargs.pop(
        "suffix",
        random_sequence(
            4,
        ),
    )

    percent_improvement = kwargs.pop("percent_improvement", 0.30)

    fs_kwrgs = {
        "fuel_summary__gas_cost": 250.00,
        "fuel_summary__electric_cost": 1200.00,
        "fuel_summary__gas_heating_consumption": 100,
        "fuel_summary__electric_heating_consumption": 120,
        "fuel_summary__gas_hot_water_consumption": 0,
        "fuel_summary__electric_hot_water_consumption": 50,
        "fuel_summary__cooling_consumption": 1250,
        "fuel_summary__lights_and_appliances_consumption": 1500,
    }
    kwrgs = fs_kwrgs.copy()

    kwrgs.update(kwargs)
    design = simulation_factory(
        number_of_runs=kwargs.get("number_of_runs", 3),
        export_type=4,
        **kwrgs,
    )
    company = kwargs.pop("company", design.company)

    kwrgs = {}
    for k, v in fs_kwrgs.items():
        kwrgs[k] = v / (1 - percent_improvement)

    kwrgs.update(kwargs)
    kwrgs.pop("version", None)
    kwrgs.pop("flavor", None)
    kwrgs.pop("udrh_filename", None)
    kwrgs.pop("udrh_checksum", None)

    # This aligns the reference methodology
    if design.numerical_version < (15, 7):
        delta = datetime.timedelta(seconds=random.uniform(-90, 90))
        kwrgs["building__created_on"] = design.building.created_on + delta
    else:
        kwrgs["simulation_date"] = design.simulation_date

    reference = simulation_factory(
        number_of_runs=design.number_of_runs + 1,
        export_type=5,
        remrate_user=design.remrate_user,
        company=company,
        version=design.version,
        flavor=design.flavor,
        rating_number=design.rating_number,
        udrh_filename=design.udrh_filename,
        udrh_checksum=design.udrh_checksum,
        building_run_flag=design.building_run_flag,
        **kwrgs,
    )

    design = Simulation.objects.get(id=design.id)
    reference = Simulation.objects.get(id=reference.id)
    design.references.add(reference)

    return design
