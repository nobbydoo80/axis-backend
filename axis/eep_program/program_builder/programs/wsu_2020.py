"""wsu_2020.py: Django """

__author__ = "Steven K"
__date__ = "12/02/2019 14:18"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from collections import OrderedDict
from datetime import date
from axis.annotation.models import Type as AnnotationType

from axis.eep_program.program_builder.base import ProgramBuilder


class Wsu2020(ProgramBuilder):
    """Program Specs for the WSU-2020"""

    name = "WSU Certification 2020"
    comment = "Washington State University Certification 2020"

    slug = "wsu-hers-2020"
    owner = "provider-washington-state-university-extension-ene"

    viewable_by_company_type = "qa,provider,rater"
    qa_viewable_by_company_type = "qa,provider"

    require_input_data = True
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False

    manual_transition_on_certify = True
    require_home_relationships = {
        "builder": True,
        "rater": True,
        "utility": True,
        "provider": True,
        "hvac": False,
        "qa": True,
    }
    require_provider_relationships = {
        "builder": False,
        "rater": False,
        "utility": False,
        "provider": False,
        "hvac": False,
        "qa": False,
    }
    visibility_date = date(year=2020, month=4, day=15)
    start_date = date(year=2020, month=4, day=15)
    close_date = None
    submit_date = None
    end_date = None
    hers_range = [0, 500]

    measures = {
        "rater": {
            "default": [
                "front-elevation-photo",
                "resnet-standard-disclosure",
                "blueprints",
                "data-collection-worksheets",
                # Notes
                "inspection-notes",
            ],
        },
    }
    texts = {
        "rater": {
            "front-elevation-photo": "Please attach front-elevation photo",
            "resnet-standard-disclosure": "RESNET Home Energy Rating Standard Disclosure",
            "blueprints": "Blueprints",
            "data-collection-worksheets": "Data collection worksheets",
            "inspection-notes": "Notes",
        },
    }
    descriptions = {}
    suggested_responses = {
        # noqa
        "default": {
            (
                "Attached (Upload documents tab)",
                "No",
            ): ["resnet-standard-disclosure", "blueprints", "data-collection-worksheets"],
            (
                "Yes",
                "N/A",
            ): ["front-elevation-photo"],
        }
    }
    instrument_types = {}
    instrument_conditions = {}

    suggested_response_flags = {
        "default": {
            "resnet-standard-disclosure": {
                "No": {"comment_required": True},
            },
            "blueprints": {
                "No": {"comment_required": True},
            },
            "data-collection-worksheets": {
                "No": {"comment_required": True},
            },
            "front-elevation-photo": {
                "N/A": {"comment_required": True},
                "Yes": {"photo_required": True},
            },
        },
    }

    optional_measures = [
        "front-elevation-photo",
        "resnet-standard-disclosure",
        "blueprints",
        "data-collection-worksheets",
        "inspection-notes",
    ]

    annotations = OrderedDict(
        (
            (
                # old naming compatibility
                "wsu-payee",
                {
                    "name": "Home Orientation",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Rater/Verifier,Builder",
                    "is_required": False,
                },
            ),
            (
                # old naming compatibility
                "certified-doe-zero-ready",
                {
                    "name": "DOE Zero Energy Ready Home™",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
                    "is_required": "False",
                },
            ),
            (
                # old naming compatibility
                "certified-estar",
                {
                    "name": "EPA ENERGY STAR®",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
                    "is_required": "False",
                },
            ),
            (
                # old naming compatibility
                "indoor-airplus",
                {
                    "name": "EPA Indoor airPLUS®",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
                    "is_required": "False",
                },
            ),
            (
                # old naming compatibility
                "watersense",
                {
                    "name": "EPA WaterSense®",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
                    "is_required": "False",
                },
            ),
            (
                "resnet-registry-id-wsu-hers-2020",
                {
                    "name": "RESNET Registry ID",
                    "data_type": AnnotationType.DATA_TYPE_OPEN,
                    "is_required": "False",
                },
            ),
        )
    )
