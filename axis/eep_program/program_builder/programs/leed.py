"""This was generated via write_program"""

__author__ = "Steven K"
__date__ = "04/23/2022 21:35"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven K",
]

from axis.eep_program.program_builder.base import ProgramBuilder
import datetime


class Leed(ProgramBuilder):
    name = "LEED v4 Homes and Multifamily"
    slug = "leed"
    owner = "eep-us-green-building-council-usgbc"
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

<p><h4>LEED v4 Homes and Multifamily</h4></p>

<ins><b>   Program Information</b></ins>
<p>    For more information about the LEED v4 program, <a href="http://www.usgbc.org/cert-guide/homes" target="_blank">click here.</a></p>

<ins><b>   Reference Guide</b></ins>
<p>    To view the LEED v4 Reference Guide, <a href="http://www.usgbc.org/guide/homes" target="_blank">click here.</a></p>

<ins><b>   LEED for Homes Provider Organizations</b></ins>
<p>    For a list of LEED for Homes Provider Organizations, <a href="http://www.usgbc.org/organizations/members/homes-providers" target="_blank">click here.</a></p>

<ins><b>   LEED for Homes Green Raters</b></ins>
<p>    For a list of LEED for Homes Green Raters, <a href="http://www.usgbc.org/people/green-raters" target="_blank">click here.</a></p>

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
                "upload-a-completed-leed-bdc-homes-and-multifamil",
            ],
        },
    }
    texts = {
        "rater": {
            "upload-a-completed-leed-bdc-homes-and-multifamil": "Upload a completed LEED BD+C: Homes and Multifamily v4 Workbook for this home",
        },
    }
    descriptions = {
        "rater": {
            "upload-a-completed-leed-bdc-homes-and-multifamil": """<a href="http://www.usgbc.org/cert-guide/homes" target="_blank">Click here</a> for information on the LEED v4 certification process and LEED v4 Workbook.""",
        },
    }
    suggested_responses = {
        "rater": {
            (
                "Upload Document(s)",
                "Not Applicable (comment required)",
            ): [
                "upload-a-completed-leed-bdc-homes-and-multifamil",
            ],
        },
    }
    suggested_response_flags = {
        "rater": {
            "upload-a-completed-leed-bdc-homes-and-multifamil": {
                "Upload Document(s)": {
                    "document_required": True,
                },
                "Not Applicable (comment required)": {
                    "comment_required": True,
                },
            },
        },
    }
