"""factory.py: Django floorplan"""
import glob
import logging
import os.path
import random
import re

from simulation.tests.factories import (
    simulation_factory,
    reference_and_design_analysis_simulation_factory,
)

from axis.company.tests.factories import rater_organization_factory
from axis.core.tests import pop_kwargs
from axis.core.utils import random_sequence, slugify_uniquely, random_digits
from ..models import Floorplan

__author__ = "Steven Klass"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def basic_custom_home_floorplan_factory(**kwargs):
    """A floorplan factory.  get_or_create based on the field 'name'"""
    owner = kwargs.pop("owner", None)
    subdivision = kwargs.pop("subdivision", False)  # No automatic subdivision by default

    kwrgs = {
        "name": f"Floorplan - {random_sequence(4)}",
        "number": f"{random_sequence(4)} - {random_digits(5)}",
        "square_footage": random_digits(5),
        "is_custom_home": True,
        "comment": f"{random_sequence(4)} comment",
    }
    if not owner:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("owner__"):
                c_kwrgs[re.sub(r"owner__", "", k)] = kwargs.pop(k)
        kwrgs["owner"] = rater_organization_factory(**c_kwrgs)
    else:
        kwrgs["owner"] = owner

    s_kwrgs = {}
    poppers = []
    for k, v in list(kwargs.items()):
        if k.startswith("subdivision__"):
            s_kwrgs[re.sub(r"subdivision__", "", k)] = kwargs.get(k)
            poppers.append(k)

    for k in poppers:
        kwargs.pop(k)

    if subdivision is None or s_kwrgs:
        from axis.subdivision.tests.factories import subdivision_factory

        subdivision = subdivision_factory(**s_kwrgs)

    kwrgs.update(kwargs)
    name = kwrgs.pop("name")
    owner = kwrgs.pop("owner")

    floorplan, create = Floorplan.objects.get_or_create(owner=owner, name=name, defaults=kwrgs)

    if subdivision:
        manual_approval = False
        floorplan.floorplanapproval_set.get_or_create(
            subdivision=subdivision,
            defaults={
                "is_approved": (not manual_approval),
            },
        )
        floorplan.floorplanapproval_set.get_or_create(subdivision=subdivision)

    return floorplan


def floorplan_factory(**kwargs):
    """A floorplan name factory.  get_or_create based on the field 'name'"""
    kwargs["is_custom_home"] = False
    return basic_custom_home_floorplan_factory(**kwargs)


def floorplan_with_remrate_factory(**kwargs):
    """A floorplan factory with REMRate Data.  get_or_create based on the field 'name'"""
    from axis.remrate_data.tests.factories import simulation_factory, udrh_simulation_factory

    owner = kwargs.pop("owner", None)
    remrate_target = kwargs.pop("remrate_target", None)
    use_udrh_simulation = kwargs.pop("use_udrh_simulation", False)

    kwrgs = {}
    if not owner:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("owner__"):
                c_kwrgs[re.sub(r"owner__", "", k)] = kwargs.pop(k)
        kwrgs["owner"] = rater_organization_factory(**c_kwrgs)
    else:
        kwrgs["owner"] = owner

    if not remrate_target:
        _owner = owner if owner else kwrgs["owner"]
        c_kwrgs = {
            "company": _owner,
            "blg_file": kwargs.get("remrate_data_file"),
        }
        for k, v in list(kwargs.items()):
            if k.startswith("remrate_target__"):
                c_kwrgs[re.sub(r"remrate_target__", "", k)] = kwargs.pop(k)
        if use_udrh_simulation:
            kwrgs["remrate_target"] = udrh_simulation_factory(**c_kwrgs)
        else:
            kwrgs["remrate_target"] = simulation_factory(**c_kwrgs)
    else:
        kwrgs["remrate_target"] = remrate_target
    kwrgs.update(kwargs)
    return floorplan_factory(**kwrgs)


def add_dummy_blg_data_file(
    floorplan: Floorplan, version: str | None = None, use_real_data: bool = False
):
    if not floorplan.remrate_data_file:
        from django.core.files.uploadedfile import SimpleUploadedFile

        content = f"REM/Rate Building File\nXXX\n1 4 {version or '16.0.1'}\nTEST DATA\n".encode()

        if use_real_data:
            BLG_FILE_PATH = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "remrate", "tests", "sources")
            )
            paths = BLG_FILE_PATH + "/*.blg" if not version else f"*{version}.blg"
            file_path = random.choice(glob.glob(paths))
            with open(file_path, encoding="ISO-8859-1") as f:
                content = f.read().encode()

        floorplan.remrate_data_file = SimpleUploadedFile(
            f"simulation_{random_sequence(4)}.blg", content
        )
        floorplan.save()


def floorplan_with_simulation_factory(**kwargs):
    """Floorplan with simulation factory"""
    owner = kwargs.pop("owner", None)
    owner_kwargs = pop_kwargs("owner__", kwargs)

    simulation = kwargs.pop("simulation", None)
    simulation_kwargs = pop_kwargs("simulation__", kwargs)
    use_reference_and_design_simulation = kwargs.pop("use_udrh_simulation", False)

    if owner is None:
        owner = rater_organization_factory(**owner_kwargs)

    if simulation is None:
        if use_reference_and_design_simulation:
            simulation = reference_and_design_analysis_simulation_factory(
                company=owner, **simulation_kwargs
            )
        else:
            simulation = simulation_factory(company=owner, **simulation_kwargs)

    kwrgs = {
        "name": simulation.name,
        "number": f"{random.randint(1000, 2500)}",
        "square_footage": simulation.conditioned_area,
        "simulation": simulation,
        "type": random.choice(list(dict(Floorplan.RATING_TYPE_CHOICES).keys())),
        "is_custom_home": random.choice([True, False]),
        "slug": slugify_uniquely(simulation.name, Floorplan),
    }

    kwrgs.update(kwargs)
    return floorplan_factory(owner=owner, **kwrgs)
