"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "11/11/2021 17:07"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime
from collections import OrderedDict


class BullseyeEriCertification(ProgramBuilder):
    name = "Bullseye ERI Certification"
    slug = "bullseye-eri-certification"
    owner = "provider-bullseye"

    is_qa_program = False
    opt_in = True
    workflow_default_settings = {}

    min_hers_score = 0
    max_hers_score = 100
    per_point_adder = 0.0

    builder_incentive_dollar_value = 0.0
    rater_incentive_dollar_value = 0.0

    enable_standard_disclosure = False
    require_floorplan_approval = False

    require_input_data = True
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False

    require_rater_of_record = True

    manual_transition_on_certify = True
    allow_sampling = True
    allow_metro_sampling = True
    require_resnet_sampling_provider = False

    is_legacy = False
    is_public = False
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2021, 11, 10)
    start_date = datetime.date(2021, 11, 10)
    close_warning = ""
    submit_warning = ""

    require_home_relationships = {
        "builder": True,
        "hvac": True,
        "utility": True,
        "rater": True,
        "provider": True,
        "qa": False,
    }
    require_provider_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
        "rater": False,
        "provider": False,
        "qa": False,
    }

    measures = {
        "rater": {
            "default": [
                "front-elevation-photo",
                "rating-documentation",
                "is-energy-star",
                "energy_star-documentation",
                "inspection-notes",
            ],
        }
    }
    texts = {
        "default": {
            "front-elevation-photo": "Please attach front-elevation photo",
            "rating-documentation": "Upload all required rating documentation",
            "is-energy-star": "Is this an ENERGY STAR Certification",
            "energy_star-documentation": "Upload all ENERGY STAR documentation",
            "inspection-notes": "Notes",
        },
    }

    instrument_types = {}

    suggested_responses = {
        "default": {
            (
                "Attached (Upload documents tab)",
                "No",
            ): ["rating-documentation", "energy_star-documentation"],
            ("Yes", "No"): ["is-energy-star"],
            (
                "Yes",
                "N/A",
            ): ["front-elevation-photo"],
        },
    }

    suggested_response_flags = {
        "default": {
            "rating-documentation": {
                "No": {"comment_required": True},
            },
            "energy_star-documentation": {
                "No": {"comment_required": True},
            },
            "front-elevation-photo": {
                "N/A": {"comment_required": True},
                "Yes": {"photo_required": True},
            },
        },
    }

    instrument_conditions = {
        "default": {},
        "rater": {
            "instrument": {
                "is-energy-star": {"Yes": ["energy_star-documentation"]},
            },
        },
    }

    optional_measures = ["inspection-notes"]

    annotations = OrderedDict(
        (
            (
                "home-orientation",
                {
                    "name": "Home Orientation",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "north,south,east,west",
                    "is_required": False,
                },
            ),
        )
    )
