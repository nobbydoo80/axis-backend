"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/28/2022 17:30"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class WatersenseVersion12(ProgramBuilder):
    name = "WaterSense® Version 1.2"
    slug = "watersense-version-12"
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
    require_input_data = False
    require_rem_data = False
    require_model_file = False
    require_ekotrope_data = False
    require_rater_of_record = False
    manual_transition_on_certify = True
    allow_sampling = False
    allow_metro_sampling = False
    require_resnet_sampling_provider = False
    is_legacy = False
    is_public = True
    is_active = True
    is_multi_family = False

    visibility_date = datetime.date(2016, 1, 1)
    start_date = datetime.date(2016, 1, 1)

    comment = """<font size="2">

<p><h4>WaterSense® Version 1.2 </h4></p>

<ins><b>Program Information</b></ins>
<p> For more information about the WaterSense® Version 1.2 program, <a href="https://www3.epa.gov/watersense/new_homes/homes_final.html" target="_blank">click here.</a></p>


<ins><b>Program Requirements</b></ins>
<p>For detailed program requirements, <a href="https://www3.epa.gov/watersense/docs/home_finalspec508.pdf" target="_blank">click here.</a></p>

<ins><b>Inspection Checklists</b></ins>
<p>For inspection and verification guidance, <a href="https://www3.epa.gov/watersense/docs/home_inspection-guidelines508.pdf" target="_blank">click here.</a></p>
<p>For downloadable checklists, <a href="https://www3.epa.gov/watersense/new_homes/homes_final.html" target="_blank">click here.</a></p>

</font>"""

    require_home_relationships = {
        "builder": True,
        "hvac": False,
        "utility": False,
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
                "upload-a-completed-epa-watersense-version-12-new",
                "front-elevation-photo-of-home-click-question-text",
            ],
        },
    }
    texts = {
        "rater": {
            "upload-a-completed-epa-watersense-version-12-new": "Upload a completed EPA WaterSense® Version 1.2 New Home Inspection Checklist for this home.",
            "front-elevation-photo-of-home-click-question-text": "Front elevation photo of home including landscaping (if possible)",
        },
    }
    descriptions = {
        "rater": {
            "upload-a-completed-epa-watersense-version-12-new": """<p> <a href="https://www3.epa.gov/watersense/docs/home_inspection-checklist508.pdf" target="_blank">Click here</a> to view or download a PDF version of the WaterSense® New Home Inspection Checklist. </p> <p> <a href="https://www3.epa.gov/watersense/docs/home_inspection-guidelines508.pdf" target="_blank">Click here</a> to view WaterSense® inspection and verification guidelines. </p>""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Upload Document(s)",
                "Not Applicable (comment required)",
            ): [
                "upload-a-completed-epa-watersense-version-12-new",
            ],
            (
                "Upload Photo(s)",
                "Not Applicable (comment required)",
            ): [
                "front-elevation-photo-of-home-click-question-text",
            ],
        },
    }
    suggested_response_flags = {
        "rater": {
            "upload-a-completed-epa-watersense-version-12-new": {
                "Upload Document(s)": {
                    "document_required": True,
                },
                "Not Applicable (comment required)": {
                    "comment_required": True,
                },
            },
            "front-elevation-photo-of-home-click-question-text": {
                "Upload Photo(s)": {
                    "photo_required": True,
                },
                "Not Applicable (comment required)": {
                    "comment_required": True,
                },
            },
        },
    }
