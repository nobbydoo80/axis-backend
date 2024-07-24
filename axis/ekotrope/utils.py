import json
import logging
import sys
import time
import traceback

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from rest_framework.serializers import ValidationError
from simulation.models import get_or_import_ekotrope_simulation

__author__ = "Autumn Valenta"
__date__ = "10/31/16 09:02"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)


def _get_auth(auth_details):
    return HTTPBasicAuth(auth_details.username, auth_details.password)


def _request_list(auth_details, type):
    url = "{base}/{}".format(type, base=settings.EKOTROPE_API_ENDPOINT)
    auth = _get_auth(auth_details)
    attempt = 1
    while True:
        response = requests.get(url, auth=auth)
        try:
            data = response.json()
        except ValueError:
            if response.text == "":
                return []
            if attempt >= 3:
                raise Exception(
                    f"Error parsing response from Ekotrope API: {response.url}: {response.text}"
                )
            time.sleep(0.5 * attempt)
            attempt += 1
            log.warning(
                f"Attempt {attempt} Error parsing response from "
                f"Ekotrope API: {response.url}: {response.text}"
            )
        else:
            if isinstance(data, dict):
                if "internalErrorCode" in data:
                    data["ekotrope_auth_id"] = auth_details.pk
                    msg = data.pop("message", "Ekotrope internalError")
                    message = "%r Occured for user %s (%s)" % (
                        msg,
                        auth_details.user,
                        auth_details.user.company,
                    )
                    log.error(message, extra=data)
                    return []
                return [data]
            return data


def _request_detail(auth_details, type, id, **data):
    url = "{base}/{}/{}".format(type, id, base=settings.EKOTROPE_API_ENDPOINT)
    auth = _get_auth(auth_details)
    attempt = 1
    while True:
        response = requests.get(url, params=data, auth=auth)
        try:
            data = response.json()
        except ValueError:
            if attempt >= 3:
                raise Exception(
                    f"Error parsing response from Ekotrope API: {response.url}: {response.text}"
                )
            time.sleep(0.5 * attempt)
            attempt += 1
            log.warning(
                f"Attempt {attempt} Error parsing response from "
                f"Ekotrope API: {response.url}: {response.text}"
            )
        else:
            return data, response.url


def request_project_list(auth_details):
    return _request_list(auth_details, "projects")


def request_project(auth_details, id):
    return _request_detail(auth_details, "projects", id)


def request_houseplan(auth_details, id):
    return _request_detail(auth_details, "houseplans", id)


def request_analysis(auth_details, id, building_type="EkotropeAsModeled", codes_to_check=None):
    data = {"buildingType": building_type}
    if codes_to_check:
        data = {"buildingType": building_type, "codesToCheck": codes_to_check}
    return _request_detail(auth_details, "planAnalysis", id, **data)


def stub_project_list(auth_details):
    from axis.ekotrope.models import Project
    from axis.ekotrope.serializers import ProjectStubSerializer

    log.info("Stubbing Ekotrope Project List")
    data = request_project_list(auth_details)

    # Strip list down to only ids we don't already track (or that previously failed the import)
    existing_ids = set(Project.objects.values_list("id", flat=True))
    data = [item for item in data if item.get("id") and item.get("id") not in existing_ids]

    if data:
        serializer = ProjectStubSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.child.company = auth_details.user.company
        serializer.save()
    return data


def stub_houseplan_list(auth_details, project_id):
    from axis.ekotrope.models import Project, HousePlan

    import_project(auth_details, project_id)
    project = Project.objects.get(id=project_id)

    if not project.data:
        # Convert Project stub to full object
        project = import_project(auth_details, project_id)

    existing_ids = set(project.houseplan_set.values_list("id", flat=True))

    new_stubs = []

    # print('--- Stubbing %d HousePlans for Project=%r' % (len(project.data['plans']), project_id))

    for item in project.data["plans"]:
        if item["id"] in existing_ids:
            continue

        new_stubs.append(
            HousePlan(
                **{
                    "id": item["id"],
                    "name": item["name"],
                    "data": {},
                    "project": project,
                }
            )
        )

    HousePlan.objects.bulk_create(new_stubs)


def import_project_tree(auth_details, id, force_refresh=True):
    log.info("Doing full project tree import for id=%r", id)
    result = {}
    project = import_project(auth_details, id)
    if not project:
        log.warning("No Project found for %r", id)
        return result

    result["project"] = project.id
    result["id"] = id
    result["force_refresh"] = force_refresh

    log.debug("Found HousePlans in Project %r: %r", id, project.data["plans"])
    for item in project.data["plans"]:
        log.debug("Importing HousePlan id=%r", item["id"])
        houseplan = import_houseplan(
            auth_details, project, item["id"], item["name"], force_refresh=force_refresh
        )
        if "houseplans" not in result:
            result["houseplans"] = []
        result["houseplans"].append(houseplan.id)
        log.debug("Importing Analysis id=%r", item["id"])
        analysis = import_analysis(
            auth_details, houseplan, item["id"], item["name"], force_refresh=force_refresh
        )
        if "analyses" not in result:
            result["analyses"] = []
        result["analyses"].append(analysis.id)

    simulation = None
    try:
        simulation = get_or_import_ekotrope_simulation(houseplan_id=houseplan.pk, use_tasks=False)
    except ValidationError as err:
        log.error(f"Simulation {id} failed - {err}")
        result["simulation"] = None
    if simulation:
        result["simulation"] = simulation.pk if simulation else "%s" % simulation
    return result


def import_project(auth_details, id):
    from axis.ekotrope.models import Project
    from axis.ekotrope.serializers import ProjectSerializer

    company = auth_details.user.company

    # The Project should always already exist due to stubbing them from the project listing import.
    # This is just to cover myself when doing a direct request.
    project, _ = Project.objects.get_or_create(
        id=id,
        defaults={
            "name": "[unknown]",
            "data": {},
            "company": company,
        },
    )

    data, request_string = request_project(auth_details, id)
    serializer = ProjectSerializer(project, data=data)
    try:
        serializer.is_valid(raise_exception=True)
    except ValidationError as e:
        project.import_request = request_string
        project.data = data
        _record_import_error(e, project)
        return

    return _save_object(
        Project,
        instance=project,
        data={
            "data": data,
        },
    )


def import_houseplan(auth_details, project, id, name, force_refresh=False):
    from axis.ekotrope.models import HousePlan
    from axis.ekotrope.serializers import HousePlanSerializer

    houseplan = project.houseplan_set.filter(id=id).first()

    if houseplan and houseplan.data and not houseplan.import_failed and not force_refresh:
        log.info("HousePlan %r already imported.", id)
        return houseplan

    data, request_string = request_houseplan(auth_details, id)
    serializer = HousePlanSerializer(houseplan, data=data)
    try:
        serializer.is_valid(raise_exception=True)
    except ValidationError as e:
        houseplan, _ = HousePlan.objects.get_or_create(
            id=id,
            defaults={
                "name": name,
                "data": {},
                "project": project,
            },
        )
        houseplan.import_request = request_string
        houseplan.data = data
        _record_import_error(e, houseplan)
        return

    return _save_object(
        HousePlan,
        instance=houseplan,
        data={
            "id": id,
            "name": name,
            "data": data,
            "project": project,
        },
    )


def import_analysis(auth_details, houseplan, id, name, force_refresh=False):
    from axis.ekotrope.models import Analysis
    from axis.ekotrope.serializers import AnalysisSerializer

    project = houseplan.project
    analysis = project.analysis_set.filter(id=id).first()

    if analysis and analysis.data and not analysis.import_failed and not force_refresh:
        if analysis.data.get("building_types").keys():
            log.info("Analysis %r already imported.", id)
            return analysis

    results = None

    from axis.ekotrope.validators import DEFAULT_ANALYSES

    for building_type, codes_to_check in DEFAULT_ANALYSES:
        data, request_string = request_analysis(
            auth_details, id, building_type=building_type, codes_to_check=codes_to_check
        )

        # with open('/tmp/analysis_%s.json' % building_type, 'w') as fh:
        #     print("Writing to /tmp/%s.json" % building_type)
        #     fh.write(json.dumps(data, indent=4))

        serializer = AnalysisSerializer(analysis, data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            if building_type != "EkotropeAsModeled":
                log.warning(
                    "Unable to get analysis for building type %s with codes %s - %s",
                    building_type,
                    codes_to_check,
                    e,
                )
                continue
            else:
                analysis, _ = Analysis.objects.get_or_create(
                    id=id,
                    defaults={
                        "project": project,
                        "houseplan": houseplan,
                        "name": name,
                        "data": {},
                    },
                )
                analysis.import_request = request_string
                analysis.data = data
                _record_import_error(e, analysis)
                return analysis

        if results is None:
            results = data
        else:
            if "building_types" not in results:
                results["building_types"] = {}
            results["building_types"][building_type] = data
        time.sleep(0.1)

    # One last check - race condition
    final = Analysis.objects.filter(id=id, project=project, houseplan=houseplan).last()
    if final:
        return final

    return _save_object(
        Analysis,
        instance=analysis,
        data={
            "id": id,
            "name": name,
            "data": results,
            "project": project,
            "houseplan": houseplan,
        },
    )


def _save_object(model, instance, data):
    if instance:
        for k, v in data.items():
            setattr(instance, k, v)
        instance.import_failed = False
        instance.import_error = None
        instance.import_traceback = None
        instance.import_request = None
        instance.save()
    else:
        instance = model.objects.create(**data)
    return instance


def _record_import_error(e, obj):
    obj.import_failed = True
    try:
        obj.import_error = json.dumps(e)
    except TypeError:
        obj.import_error = json.dumps({"message": "%s" % e})
    obj.import_traceback = "".join(traceback.format_tb(sys.exc_info()[-1]))
    obj.save()
