"""annotations.py - Axis"""

__author__ = "Steven K"
__date__ = "11/4/21 15:50"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

import datetime
import logging
import typing

from axis.eep_program.models import EEPProgram
from axis.home.models import EEPProgramHomeStatus

log = logging.getLogger(__name__)


def get_annotations(
    home_status_id: int, eep_program_id: int, annotation_last_update: datetime.datetime
):
    """Gathers the annotations for a home."""
    home_status = EEPProgramHomeStatus.objects.filter(id=home_status_id).first()
    if home_status is None:
        eep_program = EEPProgram.objects.get(id=eep_program_id)
        if eep_program is None:
            return {}
        return {k.slug: None for k in eep_program.required_annotation_types.all()}
    return {k.slug: v.content for k, v in home_status.get_annotations_breakdown().items()}


def get_wcc_annotations(
    home_status_id: int,
    eep_program_id: typing.Union[int, None],
    annotation_last_update: typing.Union[datetime.datetime, None],
):
    """Gathers the annotations for a home."""
    annotations = get_annotations(home_status_id, eep_program_id, annotation_last_update)
    annotations = {k.replace("wcc-", ""): v for k, v in annotations.items()}
    return {k.replace("-", "_"): v for k, v in annotations.items()}
