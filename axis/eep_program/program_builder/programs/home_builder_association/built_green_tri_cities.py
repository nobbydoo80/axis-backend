"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/23/2022 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime
from collections import OrderedDict


class BuiltGreenTriCities(ProgramBuilder):
    name = "Built Green® Tri-Cities/Walla Walla"
    slug = "built-green-tri-cities"
    owner = "provider-home-builders-association-of-tri-cities"
    is_qa_program = False
    opt_in = False
    workflow_default_settings = {}
    min_hers_score = 0
    max_hers_score = 100
    per_point_adder = 0.0
    builder_incentive_dollar_value = 0.0
    rater_incentive_dollar_value = 0.0
    enable_standard_disclosure = False
    require_floorplan_approval = False
    require_input_data = False
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False
    require_rater_of_record = False
    manual_transition_on_certify = False
    allow_sampling = False
    allow_metro_sampling = False
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = False
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2017, 3, 22)
    start_date = datetime.date(2017, 3, 22)
    close_date = datetime.date(2021, 12, 1)
    submit_date = datetime.date(2021, 12, 31)
    end_date = datetime.date(2021, 12, 31)

    comment = """<font size="2">

<p><h4>Built Green® Tri-Cities/Walla Walla</h4></p>

<ins><b>   Program Information</b></ins>
<p>    For more information about the Built Green Tri-Cities/Walla Walla program, <a href="http://www.hbatc.com/for-members/built-green.html#bf_miniCal_180" target="_blank">click here.</a></p>

<ins><b>   Program Requirements, Enrollment, and Inspection Checklists</b></ins>
<p>   For detailed program requirements, enrollment, and inspection checklists, <a href="http://www.hbatc.com/for-members/built-green/program-materials.html#bf_miniCal_180" target="_blank">click here.</a></p>

</font>"""

    require_home_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
        "rater": False,
        "provider": False,
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
                "upload-a-completed-built-green-checklist-for-this",
            ],
        },
    }
    texts = {
        "rater": {
            "upload-a-completed-built-green-checklist-for-this": "Upload a completed Built Green Inspection Checklist for this home",
        },
    }
    descriptions = {
        "rater": {
            "upload-a-completed-built-green-checklist-for-this": """<a href="http://www.hbatc.com/for-members/built-green/program-materials.html#bf_miniCal_180" target="_blank">Click here</a> to download the Built Green Checklists.""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Upload Document(s)",
                "Not Applicable (comment required)",
            ): [
                "upload-a-completed-built-green-checklist-for-this",
            ],
        },
    }
    optional_measures = [
        "upload-a-completed-built-green-checklist-for-this",
    ]
    suggested_response_flags = {
        "rater": {
            "upload-a-completed-built-green-checklist-for-this": {
                "Upload Document(s)": {
                    "document_required": True,
                },
                "Not Applicable (comment required)": {
                    "comment_required": True,
                },
            },
        },
    }
    annotations = OrderedDict(
        (
            (
                "built-green-certification-level",
                {
                    "name": "Built Green Certification Level",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "3-star,4-star,5-star",
                    "is_required": "True",
                },
            ),
            (
                "built-green-house-size-multiplier",
                {
                    "name": "Built Green House Size Multiplier",
                    "data_type": "float",
                    "valid_multiplechoice_values": "",
                    "is_required": "True",
                },
            ),
            (
                "built-green-points-section-1",
                {
                    "name": "Built Green Points: Section 1",
                    "data_type": "float",
                    "valid_multiplechoice_values": "",
                    "is_required": "True",
                },
            ),
            (
                "built-green-points-section-2",
                {
                    "name": "Built Green Points: Section 2",
                    "data_type": "float",
                    "valid_multiplechoice_values": "",
                    "is_required": "True",
                },
            ),
            (
                "built-green-points-section-3",
                {
                    "name": "Built Green Points: Section 3",
                    "data_type": "float",
                    "valid_multiplechoice_values": "",
                    "is_required": "True",
                },
            ),
            (
                "built-green-points-section-4",
                {
                    "name": "Built Green Points: Section 4",
                    "data_type": "float",
                    "valid_multiplechoice_values": "",
                    "is_required": "True",
                },
            ),
            (
                "built-green-points-section-5",
                {
                    "name": "Built Green Points: Section 5",
                    "data_type": "float",
                    "valid_multiplechoice_values": "",
                    "is_required": "True",
                },
            ),
            (
                "built-green-points-section-6",
                {
                    "name": "Built Green Points: Section 6",
                    "data_type": "float",
                    "valid_multiplechoice_values": "",
                    "is_required": "True",
                },
            ),
            (
                "built-green-points-section-7",
                {
                    "name": "Built Green Points: Section 7",
                    "data_type": "float",
                    "valid_multiplechoice_values": "",
                    "is_required": "True",
                },
            ),
            (
                "energy-star-certification",
                {
                    "name": "ENERGY STAR® Certified?",
                    "data_type": "multiple-choice",
                    "valid_multiplechoice_values": "Yes,No",
                    "is_required": "False",
                },
            ),
            (
                "total-built-green-points",
                {
                    "name": "Total Built Green Points",
                    "data_type": "float",
                    "valid_multiplechoice_values": "",
                    "is_required": "False",
                },
            ),
        )
    )
