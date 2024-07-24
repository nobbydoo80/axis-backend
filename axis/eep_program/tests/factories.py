"""factory.py: Django eep_program"""


import logging
import datetime
import re

from axis.core.utils import random_sequence
from ..models import EEPProgram

__author__ = "Steven Klass"
__date__ = "4/17/13 9:00 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def basic_eep_program_factory(**kwargs):
    """A eep program factory.  get_or_create based on the field 'owner', 'name'."""
    from axis.company.tests.factories import eep_organization_factory

    no_close_dates = kwargs.pop("no_close_dates", False)
    required_annotation_types = kwargs.pop("required_annotation_types", None)
    required_checklists = kwargs.pop("required_checklists", None)

    kwrgs = {
        "name": f"Program {random_sequence(4)}",
        "min_hers_score": 0,
        "max_hers_score": 100,
        "per_point_adder": 0.0,
        "builder_incentive_dollar_value": 0.0,
        "rater_incentive_dollar_value": 0.0,
        "comment": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "require_input_data": False,
        "require_rem_data": False,
        "require_model_file": False,
        "require_ekotrope_data": False,
        "program_visibility_date": datetime.date.today() - datetime.timedelta(days=1),
        "program_start_date": datetime.date.today(),
        "program_close_date": None,
        "program_submit_date": None,
        "program_end_date": None,
        "program_close_warning_date": None,
        "program_close_warning": None,
        "program_submit_warning_date": None,
        "program_submit_warning": None,
        "is_multi_family": False,
        "customer_hirl_certification_fee": 0,
        "customer_hirl_per_unit_fee": 0,
    }
    if not no_close_dates:
        kwrgs.update(
            {
                "program_close_date": datetime.date.today() + datetime.timedelta(days=10),
                "program_submit_date": datetime.date.today() + datetime.timedelta(days=20),
                "program_end_date": datetime.date.today() + datetime.timedelta(days=30),
                "program_close_warning_date": datetime.date.today() + datetime.timedelta(days=5),
                "program_close_warning": "Close Warning!",
                "program_submit_warning_date": datetime.date.today() + datetime.timedelta(days=15),
                "program_submit_warning": "Submit Warning!",
            }
        )

    owner = kwargs.pop("owner", None)
    if owner is None:
        c_kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("owner__"):
                c_kwrgs[re.sub(r"owner__", "", k)] = kwargs.pop(k)
        owner = eep_organization_factory(**c_kwrgs)

    kwrgs.update(kwargs)

    if (
        kwrgs.get("require_rem_data")
        or kwrgs.get("require_model_file")
        or kwrgs.get("require_ekotrope_data")
    ):
        kwrgs["require_input_data"] = True

    name = kwrgs.pop("name", None)

    program, create = EEPProgram.objects.get_or_create(name=name, owner=owner, defaults=kwrgs)
    if create:
        if required_checklists and isinstance(required_checklists, (list, set)):
            program.required_checklists.add(*required_checklists)
        if required_annotation_types and isinstance(required_annotation_types, (list, set)):
            program.required_annotation_types.add(*required_annotation_types)
    return program


def basic_eep_program_checklist_factory(**kwargs):
    """A eep program factory with a checklist.  get_or_create based on the field 'owner', 'name'."""
    from axis.checklist.tests.factories import checklist_factory

    required_checklists = kwargs.pop("required_checklists", [])
    checklist_count = kwargs.pop("checklist_count", 2)
    question_count = kwargs.pop("question_count", None)

    if not len(required_checklists):
        while len(required_checklists) < checklist_count:
            txt = f"Checklist {len(required_checklists) + 1} {random_sequence(4)}"
            required_checklists.append(
                checklist_factory(
                    name=txt,
                    question_count=question_count,
                    question_prefix="C{}.".format(len(required_checklists)),
                )
            )
    kwrgs = {
        "name": f"Program {random_sequence(4)} (with Checklist)",
        "builder_incentive_dollar_value": 1500,
        "required_checklists": required_checklists,
    }
    kwrgs.update(kwargs)
    return basic_eep_program_factory(**kwrgs)
