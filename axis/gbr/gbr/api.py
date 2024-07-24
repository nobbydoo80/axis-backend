"""api.py - axis"""

__author__ = "Steven K"
__date__ = "1/10/23 09:29"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import json
import logging

from dataclasses import dataclass
from functools import cached_property

import requests
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from rest_framework.serializers import Serializer

from axis.gbr.models import GreenBuildingRegistry, GbrStatus
from axis.home.models import Home, EEPProgramHomeStatus
from .serializers import GBRHomeSerializer, GBRHomeStatusEPSSerializer

log = logging.getLogger(__name__)
gbr_app = apps.get_app_config("gbr")


class InvalidAssesmentError(Exception):
    pass


@dataclass
class GreenBuildingRegistryAPIConnect:
    use_sandbox: bool = False
    api_key: str = gbr_app.API_KEY

    @cached_property
    def base_url(self):
        if self.use_sandbox:
            return "https://sandbox.greenbuildingregistry.com"
        return "https://api.greenbuildingregistry.com"

    @cached_property
    def headers(self) -> dict:
        return {"Authorization": f"api-key {self.api_key}"}

    def post(self, url, data=None, files=None) -> requests.request:
        # print(f"url = {url}")
        # print(f"data = {json.dumps(data, indent=4)}")
        # print(f"files = {json.dumps(files, indent=4)}")
        # print(f"headers = {json.dumps(self.headers, indent=4)}")
        # print()
        response = requests.post(url, headers=self.headers, data=data, files=files)
        # print(f"response.status_code: {response.status_code}")
        # print(f"response.json: {json.dumps(response.json(), indent=4)}")
        return response

    def get_existing_gbr_annotation(self, home: Home) -> str | None:
        """If we have an existing annotation we should use it"""
        from axis.annotation.models import Annotation

        annotation = Annotation.objects.filter(
            type__slug=gbr_app.EXTERNAL_ID_ANNOTATION_SLUG,
            content_type=ContentType.objects.get_for_model(EEPProgramHomeStatus),
            object_id__in=home.homestatuses.values_list("id", flat=True),
        ).first()
        if annotation:
            return annotation.content

    def create_property(self, home: Home) -> GreenBuildingRegistry:
        url = f"{self.base_url}/api/properties"

        # We may already have an existing GBR - Let's use that if we have it.
        existing = self.get_existing_gbr_annotation(home)
        if existing:
            defaults = {
                "gbr_id": existing,
                "status": GbrStatus.LEGACY_IMPORT,
                "api_result": None,
            }
        else:
            serializer = GBRHomeSerializer(instance=home)
            response = self.post(url, data=serializer.data)
            data = response.json()
            if response.status_code == 201:
                defaults = {
                    "gbr_id": data["gbr_id"],
                    "status": GbrStatus.PROPERTY_VALID,
                    "api_result": None,
                }
            else:
                defaults = {"status": GbrStatus.PROPERTY_INVALID, "api_result": data}
                if "error" in data:
                    if "service unavailable" in data["error"].lower():
                        defaults["status"] = GbrStatus.SERVICE_UNAVAILABLE
                    elif "throttled" in data["error"].lower():
                        defaults["status"] = GbrStatus.SERVICE_THROTTLED
        obj, create = GreenBuildingRegistry.objects.update_or_create(home=home, defaults=defaults)
        return obj

    def get_assessment_serializer(
        self, obj: GreenBuildingRegistry, assessment: str = "eps"
    ) -> Serializer:
        """Get the right serializer for the job"""
        if assessment == "eps":
            home_status = (
                EEPProgramHomeStatus.objects.filter(
                    eep_program__is_qa_program=False,
                    eep_program__owner__slug="eto",
                    eep_program__slug__icontains="eto",
                    home_id=obj.home_id,
                )
                .order_by("pk")
                .last()
            )
            if not home_status:
                raise InvalidAssesmentError(f"No home statuses exist for {assessment} serializer")
            return GBRHomeStatusEPSSerializer(instance=home_status)
        raise InvalidAssesmentError(f"Assessment serializer {assessment} not yet supported")

    def create_assessment(
        self, obj: GreenBuildingRegistry, assessment: str = "eps"
    ) -> GreenBuildingRegistry:
        url = f"{self.base_url}/api/assessments/{assessment}"

        if not obj.gbr_id or obj.status == GbrStatus.ASSESSMENT_CREATED:
            return obj

        serializer = self.get_assessment_serializer(obj, assessment)
        response = self.post(url, data=serializer.data)
        if response.status_code == 201:
            obj.status = GbrStatus.ASSESSMENT_CREATED
            obj.api_result = response.json()
            obj.save()
        else:
            obj.status = GbrStatus.ASSESSMENT_INVALID
            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError as err:  # pragma no cover
                log.exception(
                    f"Unable to parse response from GBR {obj.id} on home {obj.home_id} {obj.home}"
                )
                obj.api_result = {
                    "error": "Unable to parse the response from GBR",
                    "result": str(response.content),
                    "exception": str(err),
                }
            else:
                obj.api_result = data
                if "error" in data:
                    if "service unavailable" in data["error"].lower():
                        obj.status = GbrStatus.SERVICE_UNAVAILABLE
                        obj.api_result = data
                    elif "throttled" in data["error"].lower():
                        obj.status = GbrStatus.SERVICE_THROTTLED
                        obj.api_result = data

            obj.save()

        obj.refresh_from_db()
        return obj
