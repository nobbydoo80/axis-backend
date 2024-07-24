"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/23/2022 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class EnergyStarVersion32Rev09(ProgramBuilder):
    name = "ENERGY STAR® Version 3.2 (Rev. 09)"
    slug = "energy-star-version-32-rev-09"
    owner = "us-epa"
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
    require_rem_data = True
    require_model_file = False
    require_ekotrope_data = False
    require_rater_of_record = True
    manual_transition_on_certify = True
    allow_sampling = True
    allow_metro_sampling = True
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = True
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2019, 1, 1)
    start_date = datetime.date(2019, 1, 1)
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
        "builder": False,
        "hvac": False,
        "utility": False,
        "rater": False,
        "provider": False,
        "qa": False,
    }
    measures = {
        "rater": {
            "default": [
                "for-this-home-upload-the-following-completed-ene-2",
                "this-home-complies-with-the-energy-star-version--0",
            ],
        },
    }
    texts = {
        "rater": {
            "for-this-home-upload-the-following-completed-ene-2": "For this home, upload the following completed ENERGY STAR® Version 3.2 (Rev. 09) documents: Rater Design Review Checklist, Rater Field Checklist, HVAC Design Report, and HVAC Commissioning Checklist.",
            "this-home-complies-with-the-energy-star-version--0": "This home complies with the ENERGY STAR® Version 3/3.1 (Rev. 09) mandatory Water Management System builder requirements.",
        },
    }
    descriptions = {
        "rater": {
            "for-this-home-upload-the-following-completed-ene-2": """<a href="https://www.energystar.gov/sites/default/files/or%20wa%20program%20requirements%203.2%20v3%202018-05-16_clean.pdf" target="_blank">Click here</a> to view or download a fillable PDF version of the ENERGY STAR® Version 3.2 (Rev. 09) Rater checklists.""",
            "this-home-complies-with-the-energy-star-version--0": """<a href="https://www.energystar.gov/sites/default/files/WMS%20v100%202018-05-09_clean.pdf" target="_blank">Click here</a> to view or download a PDF version of the ENERGY STAR® Version 3/3.1 (Rev. 09) Water Management System builder requirements.""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Upload Document(s)",
                "Not Applicable (comment required)",
            ): [
                "for-this-home-upload-the-following-completed-ene-2",
            ],
            (
                "Not Applicable (comment required)",
                "Builder Verified",
            ): [
                "this-home-complies-with-the-energy-star-version--0",
            ],
        },
    }
    suggested_response_flags = {
        "rater": {
            "for-this-home-upload-the-following-completed-ene-2": {
                "Upload Document(s)": {
                    "document_required": True,
                },
                "Not Applicable (comment required)": {
                    "comment_required": True,
                },
            },
            "this-home-complies-with-the-energy-star-version--0": {
                "Not Applicable (comment required)": {
                    "comment_required": True,
                },
            },
        },
    }
