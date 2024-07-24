import json
import os

from axis.company.tests.factories import base_company_factory, rater_organization_factory
from axis.core.tests import pop_kwargs
from axis.core.tests.factories import basic_user_factory
from axis.core.utils import random_sequence
from axis.ekotrope.models import HousePlan, Project, EkotropeAuthDetails, Analysis
from settings.base import SITE_ROOT

__author__ = "Artem Hruzd"
__date__ = "5/31/19 11:00 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
]


def ekotrope_auth_details_factory(**kwargs):
    username_and_pw = random_sequence(4)
    kwrgs = {"username": username_and_pw, "password": username_and_pw, "user": basic_user_factory()}
    kwrgs.update(kwargs)
    auth_details, _ = EkotropeAuthDetails.objects.get_or_create(defaults=kwrgs)
    return auth_details


def project_factory(**kwargs):
    _id = kwargs.pop("id", random_sequence(8, include_unicode=False))
    stub_only = kwargs.pop("stub_only", False)
    house_plan_id = kwargs.pop("house_plan_id", None)

    company = kwargs.pop("company", None)
    if company is None:
        company = base_company_factory()

    kwrgs = {
        "id": _id,
        "name": f"House plan {random_sequence(4)}",
        "import_failed": False,
        "company": company,
    }
    if not kwargs.get("data") and stub_only is False:
        data_path = SITE_ROOT, "axis", "ekotrope", "sources", "sample_project_response.json"
        sample_project_response_path = os.path.join(*data_path)
        with open(sample_project_response_path) as sample_project_response_file:
            response = sample_project_response_file.read()
        data = json.loads(response)
        data["id"] = _id
        if house_plan_id:
            data["masterPlanId"] = house_plan_id
            data["plans"][0] = house_plan_id
        kwrgs["data"] = data

    kwrgs.update(kwargs)

    project, _ = Project.objects.get_or_create(defaults=kwrgs)
    return project


def house_plan_factory(**kwargs):
    # We do this to work nicely with axis.ekotrope.tests.mock_responses.mocked_request_houseplan
    _id = kwargs.pop("id", random_sequence(6, include_unicode=False) + "p0")

    stub_only = kwargs.pop("stub_only", False)
    project = kwargs.pop("project", None)
    locally_created_project = False
    if project is None:
        # We do this to work nicely with axis.ekotrope.tests.mock_responses.mocked_request_houseplan
        __id = _id[:-2] + random_sequence(2, include_unicode=False)
        _kw = {"id": __id, "house_plan_id": _id}  # This must be full project
        if "company" in kwargs:
            _kw["company"] = kwargs.pop("company")
        project = project_factory(**_kw)
        locally_created_project = True

    kwrgs = {
        "id": _id,
        "name": f"House plan {random_sequence(4)}",
        "import_failed": False,
        "project": project,
    }

    if not kwargs.get("data") and stub_only is False:
        data_path = SITE_ROOT, "axis", "ekotrope", "sources", "sample_house_plan_response.json"
        sample_houseplan_response_path = os.path.join(*data_path)
        with open(sample_houseplan_response_path) as sample_houseplan_response_file:
            response = sample_houseplan_response_file.read()
        data = json.loads(response)
        data["id"] = _id
        kwrgs["data"] = data

    kwrgs.update(kwargs)

    if not locally_created_project:
        data = project.data
        data["masterPlanId"] = kwrgs.get("id")
        data["plans"][0] = kwrgs.get("id")
        project.data = data
        project.save()

    house_plan, _ = HousePlan.objects.get_or_create(defaults=kwrgs)

    return house_plan


def analysis_factory(**kwargs):
    project = kwargs.pop("project", None)
    if project is None:
        _kw = {}
        if "company" in kwargs:
            _kw["company"] = kwargs.pop("company")
        project = project_factory(**_kw)

    _id = kwargs.pop("id", random_sequence(8, include_unicode=False))

    houseplan = kwargs.pop("houseplan", None)
    if houseplan is None:
        houseplan = house_plan_factory(project=project, id=_id)

    kwrgs = {
        "id": _id,
        "name": f"Analysis {random_sequence(4)}",
        "import_failed": False,
        "project": project,
        "houseplan": houseplan,
    }

    if not kwargs.get("data"):
        data_path = SITE_ROOT, "axis", "ekotrope", "sources", "sample_analysis_response.json"
        sample_analysis_response_path = os.path.join(*data_path)
        with open(sample_analysis_response_path) as sample_analysis_response_file:
            response = sample_analysis_response_file.read()
        data = json.loads(response)
        data["id"] = _id
        kwrgs["data"] = data

    kwrgs.update(kwargs)

    analysis, _ = Analysis.objects.get_or_create(defaults=kwrgs)
    return analysis


def sim_version_project_factory(**kwargs):
    master_plan_id = kwargs.pop("master_plan_id", random_sequence(8))

    company = kwargs.pop("company", None)
    if company is None:
        company = rater_organization_factory(**pop_kwargs("company__", kwargs))
    version = kwargs.pop("version", kwargs.pop("algorithmVersion", None))
    kwrgs = {
        "id": random_sequence(8),
        "name": f"House plan {random_sequence(4)}",
        "import_failed": False,
        "company": company,
    }

    kwrgs.update(kwargs)

    if not kwargs.get("data"):
        sample_project_response_path = os.path.join(
            SITE_ROOT, "axis", "ekotrope", "sources", "sample_project_response.json"
        )
        with open(sample_project_response_path) as fh:
            data = json.load(fh)
        data["id"] = kwrgs["id"]
        _master_plan_id = kwargs.get("masterPlanId")
        for plan in data["plans"]:
            if plan["id"] == _master_plan_id:
                plan["id"] = master_plan_id
        data["masterPlanId"] = master_plan_id
        if version:
            data["algorithmVersion"] = version
        kwrgs["data"] = data
    _id = kwrgs.pop("id")
    project, _ = Project.objects.get_or_create(id=_id, defaults=kwrgs)
    return project


def simulation_factory(**kwargs):
    project_id = kwargs.pop("project_id", random_sequence(8))
    plan_id = kwargs.pop("project_id", random_sequence(8))
    company = kwargs.pop("company", None)
    project_kwargs = pop_kwargs("project__", kwargs)
    if company is None:
        company = rater_organization_factory(**pop_kwargs("company__", kwargs))
    project = sim_version_project_factory(
        id=project_id, master_plan_id=plan_id, company=company, **project_kwargs
    )
    houseplan = house_plan_factory(id=plan_id, project=project)
    analysis_factory(id=plan_id, project=project, houseplan=houseplan)
    return project
