"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/23/2022 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class EnergyStarVersion3Rev07(ProgramBuilder):
    name = "ENERGY STAR® Version 3 (Rev. 07)"
    slug = "energy-star-version-3-rev-07"
    owner = "us-epa"
    is_qa_program = False
    opt_in = True
    workflow_default_settings = {}
    min_hers_score = 0
    max_hers_score = 100
    per_point_adder = 0.0
    builder_incentive_dollar_value = 0.0
    rater_incentive_dollar_value = 0.0
    enable_standard_disclosure = True
    require_floorplan_approval = False
    require_input_data = True
    require_rem_data = True
    require_model_file = True
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

    visibility_date = datetime.date(2016, 1, 1)
    start_date = datetime.date(2016, 1, 1)
    close_warning = ""
    close_date = datetime.date(2021, 11, 1)
    submit_date = datetime.date(2021, 11, 1)
    submit_warning = ""
    end_date = datetime.date(2021, 11, 1)

    comment = """<font size="2">

<p><h4>ENERGY STAR® Version 3 (Rev. 07)</h4></p>

<ins><b>   Program Information</b></ins>
<p>    For more information about the ENERGY STAR Version 3 program, <a href="https://www.energystar.gov/index.cfm?c=bldrs_lenders_raters.nh_v3_guidelines" target="_blank">click here.</a></p>

<ins><b>   Program Requirements</b></ins>
<p>   For detailed program requirements, <a href="https://www.energystar.gov/ia/partners/bldrs_lenders_raters/downloads/National_Program_Requirements.pdf" target="_blank">click here.</a></p>

<ins><b>Inspection Checklists</b></ins>
<p>For fillable PDF checklists, <a href="https://www.energystar.gov/ia/partners/bldrs_lenders_raters/downloads/Inspection_Checklists.pdf" target="_blank">click here.</a></p>

</font>"""

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
                "for-this-home-upload-the-following-completed-ene-0",
            ],
        },
    }
    texts = {
        "rater": {
            "for-this-home-upload-the-following-completed-ene-0": "For this home, upload the following completed ENERGY STAR® Version 3 documents: Thermal Enclosure System Rater Checklist, HVAC System Quality Installation Contractor Checklist, HVAC System Quality Installation Rater Checklist, and Water Management System Builder Checklist.",
        },
    }
    descriptions = {
        "rater": {
            "for-this-home-upload-the-following-completed-ene-0": """<a href="https://www.energystar.gov/ia/partners/bldrs_lenders_raters/downloads/Inspection_Checklists.pdf" target="_blank">Click here</a> to donwload the ENERGY STAR Version 3 inspection checklists.""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Upload Document(s)",
                "Not Applicable (comment required)",
            ): [
                "for-this-home-upload-the-following-completed-ene-0",
            ],
        },
    }
    suggested_response_flags = {
        "rater": {
            "for-this-home-upload-the-following-completed-ene-0": {
                "Upload Document(s)": {
                    "document_required": True,
                },
                "Not Applicable (comment required)": {
                    "comment_required": True,
                },
            },
        },
    }
