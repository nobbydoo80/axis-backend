"""factories.py: """

__author__ = "Artem Hruzd"
__date__ = "08/09/2022 22:01"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import random
import re

from axis.company.tests.factories import provider_organization_factory
from axis.core.tests.factories import SET_NULL
from axis.eep_program.tests.factories import basic_eep_program_factory
from axis.home.tests.factories import eep_program_home_status_factory
from axis.qa.models import QARequirement, QAStatus


def qa_requirement_factory(**kwargs) -> QARequirement:
    qa_company = kwargs.pop("qa_company", None)
    if qa_company is SET_NULL:
        qa_company = None
    elif not qa_company:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("qa_company__"):
                _kwrgs[re.sub(r"qa_company__", "", k)] = kwargs.pop(k)
        qa_company = provider_organization_factory(**_kwrgs)

    requirement_type = random.choice([x for x, y in QARequirement.QA_REQUIREMENT_TYPES])
    eep_program = kwargs.pop("eep_program", None)
    if eep_program is None:
        _kwrgs = {"is_qa_program": requirement_type == "field"}
        for k, v in list(kwargs.items()):
            if k.startswith("eep_program__"):
                _kwrgs[re.sub(r"eep_program__", "", k)] = kwargs.pop(k)
        eep_program = basic_eep_program_factory(**_kwrgs)

    kwrgs = {
        "qa_company": qa_company,
        "eep_program": eep_program,
        "type": requirement_type,
    }
    kwrgs.update(kwargs)
    requirement = QARequirement.objects.create(**kwrgs)
    return requirement


def qa_status_factory(**kwargs) -> QAStatus:
    requirement = kwargs.pop("requirement", None)
    if requirement is SET_NULL:
        requirement = None
    elif not requirement:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("requirement__"):
                _kwrgs[re.sub(r"requirement__", "", k)] = kwargs.pop(k)
        requirement = qa_requirement_factory(**_kwrgs)

    owner = kwargs.pop("owner", None)
    if not owner:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("owner__"):
                _kwrgs[re.sub(r"owner__", "", k)] = kwargs.pop(k)
        owner = provider_organization_factory(**_kwrgs)

    home_status = kwargs.pop("home_status", None)
    if home_status is SET_NULL:
        home_status = None
    elif not home_status:
        _kwrgs = {}
        for k, v in list(kwargs.items()):
            if k.startswith("home_status__"):
                _kwrgs[re.sub(r"home_status__", "", k)] = kwargs.pop(k)
        home_status = eep_program_home_status_factory(**_kwrgs)

    kwrgs = {"requirement": requirement, "owner": owner, "home_status": home_status}
    kwrgs.update(kwargs)
    qa_status = QAStatus.objects.create(**kwrgs)
    return qa_status
