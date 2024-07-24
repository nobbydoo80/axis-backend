__author__ = "Autumn Valenta"
__date__ = "02/10/18 12:09 AM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Autumn Valenta",
]


import logging

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime

log = logging.getLogger(__name__)


class IndoorAirplusVersion1Rev03(ProgramBuilder):
    name = "Indoor airPLUS Version 1 (Rev. 03)"
    slug = "indoor-airplus-version-1-rev-03"
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

    visibility_date = datetime.date(2019, 4, 21)
    start_date = datetime.date(2019, 4, 21)

    comment = """<font size="2">

<p><h4>Indoor airPLUS Version 1 (Rev. 03)</h4></p>

<ins><b>Program Information</b></ins>
<p> For more information about the Indoor airPLUS Version 1 (Rev. 03) program, <a href="https://www.epa.gov/indoorairplus/indoor-airplus-construction-specifications-version-1-rev-03" target="_blank">click here.</a></p>

<ins><b>Construction Specifications</b></ins>
<p>For detailed program construction specifications, <a href="https://www.epa.gov/sites/production/files/2015-10/documents/construction_specification_rev_3_508.pdf" target="_blank">click here.</a></p>

<ins><b>Policy Record</b></ins>
<p>For the program policy record, <a href="https://www.epa.gov/sites/production/files/2015-10/documents/policy_record_508.pdf" target="_blank">click here.</a></p>

<ins><b>Inspection Checklist</b></ins>
<p>For a fillable PDF Verification Checklist, <a href="https://www.epa.gov/sites/production/files/2015-10/documents/fillable_verification_checklist_508.pdf" target="_blank">click here.</a></p>

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
                "this-home-has-been-or-is-currently-being-certified",
                "upload-a-completed-epa-indoor-airplus-version-1-r",
            ],
        },
    }
    texts = {
        "rater": {
            "this-home-has-been-or-is-currently-being-certified": "This home has been or is currently being certified under the ENERGY STAR® Version 3/3.1 program.",
            "upload-a-completed-epa-indoor-airplus-version-1-r": "Upload a completed EPA Indoor airPLUS Version 1 (Rev. 03) Verification Checklist for this home.",
        },
    }
    descriptions = {
        "rater": {
            "this-home-has-been-or-is-currently-being-certified": """<a href="https://www.epa.gov/indoorairplus/indoor-airplus-construction-specifications-version-1-rev-03" target="_blank">Click here</a> to view Indoor airPLUS Version 1 (Rev. 03) program requirements.""",
            "upload-a-completed-epa-indoor-airplus-version-1-r": """<a href="https://www.epa.gov/sites/production/files/2015-10/documents/fillable_verification_checklist_508.pdf" target="_blank">Click here</a> to download the Indoor airPLUS Version 1 (Rev. 03) Verification Checklist.""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Yes",
                "No",
                "Not Applicable (comment required)",
            ): [
                "this-home-has-been-or-is-currently-being-certified",
            ],
            (
                "Upload Document(s)",
                "Not Applicable (comment required)",
            ): [
                "upload-a-completed-epa-indoor-airplus-version-1-r",
            ],
        },
    }
    suggested_response_flags = {
        "rater": {
            "this-home-has-been-or-is-currently-being-certified": {
                "Not Applicable (comment required)": {
                    "comment_required": True,
                },
            },
            "upload-a-completed-epa-indoor-airplus-version-1-r": {
                "Upload Document(s)": {
                    "document_required": True,
                },
                "Not Applicable (comment required)": {
                    "comment_required": True,
                },
            },
        },
    }
