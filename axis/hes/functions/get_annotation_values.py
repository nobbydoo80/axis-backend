import logging
from axis.home.models import EEPProgramHomeStatus
from django.apps import apps

log = logging.getLogger(__name__)
app = apps.get_app_config("hes")

__author__ = "Benjamin S"
__date__ = "9/9/2022 12:00"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Benjamin S",
]


def get_external_id_from_annotation(home_status: EEPProgramHomeStatus) -> str | None:
    return _get_value_from_annotation(home_status, app.EXTERNAL_ID_ANNOTATION_SLUG)


def get_orientation_from_annotation(home_status: EEPProgramHomeStatus) -> str | None:
    return _get_value_from_annotation(home_status, app.ORIENTATION_ANNOTATION_SLUG)


def _get_value_from_annotation(home_status: EEPProgramHomeStatus, slug) -> str | None:
    annotation = home_status.annotations.filter(type__slug=slug).first()

    if annotation:
        val = annotation.content
        log.debug(
            f"Found annotation '{slug}' with value '{val}' from annotation for EEPProgramHomeStatus {home_status.pk}"
        )
        return val
    return None
