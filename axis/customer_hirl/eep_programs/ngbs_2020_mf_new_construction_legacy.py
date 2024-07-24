"""ngbs_2015_mf_remodel_building_legacy.py: """

__author__ = "Artem Hruzd"
__date__ = "05/24/2021 3:42 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Artem Hruzd",
    "Steven Klass",
]

import datetime
from collections import OrderedDict

from axis.annotation.models import Type
from axis.eep_program.program_builder.base import ProgramBuilder


class NGBS2020MFNewConstructionLegacy(ProgramBuilder):
    name = "NGBS 2020 MF New Construction"
    slug = "ngbs-mf-new-construction-2020"
    owner = "provider-home-innovation-research-labs"
    is_multi_family = True

    visibility_date = datetime.date(year=2020, month=11, day=1)
    start_date = datetime.date(year=2020, month=2, day=1)
    close_date = datetime.date(year=2023, month=1, day=1)
    submit_date = datetime.date(year=2023, month=1, day=1)
    end_date = datetime.date(year=2023, month=1, day=1)

    require_home_relationships = {
        "builder": True,
        "rater": False,
        "utility": False,
        "provider": False,
        "hvac": False,
        "qa": False,
    }

    annotations = OrderedDict(
        (
            (
                "certified-nat-gbs",
                {
                    "name": "National Green Building Standard",
                    "description": "National Green Building Standard",
                    "data_type": Type.DATA_TYPE_MULTIPLE_CHOICE,
                    "is_required": False,
                },
            ),
            (
                "certification-standard",
                {
                    "name": "Certification Standard",
                    "data_type": Type.DATA_TYPE_OPEN,
                    "is_required": True,
                },
            ),
            (
                "certification-date",
                {
                    "name": "Certification Date",
                    "data_type": Type.DATA_TYPE_OPEN,
                    "is_required": True,
                },
            ),
            (
                "certification-number",
                {
                    "name": "Certification Number",
                    "data_type": Type.DATA_TYPE_OPEN,
                    "is_required": True,
                },
            ),
            (
                "certification-record-id",
                {
                    "name": "Certification Record ID",
                    "data_type": Type.DATA_TYPE_OPEN,
                    "is_required": True,
                },
            ),
            (
                "project-id",
                {
                    "name": "Project ID",
                    "data_type": Type.DATA_TYPE_OPEN,
                    "is_required": True,
                },
            ),
            (
                "unit-count",
                {
                    "name": "Unit Count",
                    "data_type": Type.DATA_TYPE_OPEN,
                    "is_required": True,
                },
            ),
            (
                "hers-score",
                {
                    "name": "HERS Score",
                    "data_type": Type.DATA_TYPE_OPEN,
                    "is_required": True,
                },
            ),
            (
                "hud-disaster-case-number",
                {
                    "name": "HUD Case number",
                    "data_type": Type.DATA_TYPE_OPEN,
                    "is_required": False,
                },
            ),
        )
    )

    measures = {"rater": {}}
